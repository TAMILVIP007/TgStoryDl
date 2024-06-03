import asyncio
import logging
import os
import re
from datetime import datetime

from telethon import Button, TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.stories import GetPeerStoriesRequest

from .config import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot(TelegramClient):
    def __init__(self, api_id, api_hash, bot_token, database):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.database = database
        self.client = TelegramClient("tgstorydl", self.api_id, self.api_hash)
        self.user_client = (
            TelegramClient(
                StringSession(config.STRING_SESSION), self.api_id, self.api_hash
            )
            if config.STRING_SESSION
            else TelegramClient("userbot", self.api_id, self.api_hash)
        )
        self.start_time = datetime.now()
        self.user_tasks = {}
        self.lock = asyncio.Lock()

    async def init_telegram_client(self):
        await self.client.start(bot_token=self.bot_token)
        await self.user_client.start()
        self.client.add_event_handler(self.handle_message, events.NewMessage)
        self.client.add_event_handler(
            self.handle_start,
            events.NewMessage(pattern="/start", func=lambda e: e.is_private),
        )
        self.client.add_event_handler(
            self.show_status,
            events.NewMessage(pattern="/status", from_users=config.DEVS),
        )
        logger.info("Telegram client initialized.")

    async def handle_message(self, event):
        message_text = event.message.message
        chat_id = event.chat_id
        await self.database.add_user(event.sender_id, event.sender.access_hash)
        if message_text.startswith("/") or not event.is_private:
            return
        if username := self.extract_username_or_link(message_text):
            await self.download_story(chat_id, username)
        else:
            await event.reply("Please send a valid Telegram username or profile link.")

    async def handle_start(self, event):
        await event.reply(
            "Welcome! Send me a Telegram username or profile link to download stories.",
            buttons=[Button.url("Updates", url="https://t.me/mybotsrealm")],
        )

    def extract_username_or_link(self, message_text):
        tg_username_pattern = r"@[A-Za-z0-9_]{5,32}"
        if re.match(tg_username_pattern, message_text):
            return message_text.strip("@")
        url_pattern = r"https?://(?:www\.)?t\.me/([A-Za-z0-9_]{5,32})"
        return (
            match.group(1)
            if (match := re.search(url_pattern, message_text))
            else None
        )

    async def download_story(self, chat_id, username):
        try:
            async with self.lock:
                if chat_id not in self.user_tasks:
                    self.user_tasks[chat_id] = []

            msg = await self.client.send_message(
                chat_id,
                f"<b>Downloading story from</b> <code>{username}</code>",
                parse_mode="html",
            )
            download_msg_id = msg.id
            task = asyncio.create_task(
                self.create_download_task(chat_id, username, download_msg_id)
            )
            async with self.lock:
                self.user_tasks[chat_id].append(task)
        except Exception as e:
            logger.error(f"Error downloading story from {username}: {e}")
            await self.client.send_message(
                chat_id, f"Failed to download story from {username}"
            )

    async def create_download_task(self, chat_id, username, download_msg_id):
        try:
            stories = await self.user_client(GetPeerStoriesRequest(username))
            if not stories.stories or len(stories.stories.stories) < 1:
                return await self.client.edit_message(
                    chat_id,
                    download_msg_id,
                    f"<b>No stories found for</b> <code>{username}</code>",
                    parse_mode="html",
                )

            for story in stories.stories.stories:
                await self.download_task(chat_id, username, story)
            await self.client.delete_messages(chat_id, download_msg_id)
            await self.client.send_message(
                chat_id,
                f"All stories from <code>{username}</code> have been uploaded.",
                parse_mode="html",
            )

        except Exception as e:
            logger.error(f"Error creating download task for {username}: {e}")
            await self.client.send_message(
                chat_id, f"Failed to download story from {username}"
            )

    async def download_task(self, chat_id, username, story):
        try:
            story_file = await self.user_client.download_media(story.media)
            story_thumb = await self.user_client.download_media(story.media, thumb=-1)
            task = {
                "username": username,
                "story": story,
                "file": story_file,
                "thumb": story_thumb,
                "caption": story.caption,
                "attributes": (
                    story.media.document.attributes
                    if hasattr(story.media, "document")
                    else None
                ),
            }
            await self.send_file_with_attributes(chat_id, task)
        except Exception as e:
            logger.error(f"Error downloading story from {username}: {e}")
        finally:
            if task.get("file") and os.path.exists(task["file"]):
                os.remove(task["file"])
            if task.get("thumb") and os.path.exists(task["thumb"]):
                os.remove(task["thumb"])

    async def send_file_with_attributes(self, chat_id, task):
        try:
            await self.client.send_file(
                chat_id,
                task["file"],
                attributes=task["attributes"],
                thumb=task["thumb"],
                caption=task["caption"],
            )
            await self.database.add_downloaded_file()
        except Exception as e:
            logger.error(f"Error sending file from {task['username']}: {e}")

    async def show_status(self, event):
        total_users, downloaded_files_count, db_size_mb, db_size_kb = (
            await self.database.get_status()
        )
        uptime = datetime.now() - self.start_time

        await event.reply(
            f"<b>Total users:</b> <code>{total_users}</code>\n"
            f"<b>Downloaded files:</b> <code>{downloaded_files_count}</code>\n"
            f"<b>Uptime:</b> <code>{uptime}</code>\n"
            f"<b>Database size:</b> <code>{db_size_mb:.2f} MB ({db_size_kb:.2f} KB)</code>",
            parse_mode="html",
        )
