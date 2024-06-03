import asyncio

from TgStoryDl.plugins.config import config
from TgStoryDl.plugins.database import Database
from TgStoryDl.plugins.handler import TelegramBot


async def main():
    database = Database(config.DATABASE_URL)

    await database.create_tables()

    bot = TelegramBot(config.API_ID, config.API_HASH, config.TOKEN, database)
    await bot.init_telegram_client()
    await bot.client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
