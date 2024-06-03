# Telegram Story Downloader Bot

📲 **Telegram Story Downloader Bot** 📥

This bot allows you to download stories from Telegram users effortlessly. Simply send a Telegram username or profile link, and the bot will fetch all available stories for you.

## Features

- **Easy to Use:** Send a Telegram username or profile link, and the bot will download the stories.
- **Real-Time Updates:** Get the latest stories seamlessly.
- **Support:** Reach out to our Support Chat for assistance.

## Getting Started

### Prerequisites

- Python 3.8+
- Telegram API credentials (API ID, API Hash)
- A Telegram bot token

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/telegram-story-downloader-bot.git
    cd telegram-story-downloader-bot
    ```

2. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Set up your configuration:**

    Create a `.env` file with your API credentials and bot token:

    ```python
    # config.py
    API_ID = 'your_api_id'
    API_HASH = 'your_api_hash'
    BOT_TOKEN = 'your_bot_token'
    DEVS = 13,123,213  # List of developer user IDs who can use /status command
    DATABASE_URL = 'sqlite+aiosqlite:///your_database.db'
    ```

### Running the Bot

1. **Start the bot:**

    ```sh
    python -m TgStoryDl
    ```

2. **Interacting with the bot:**

    - Send a Telegram username (e.g., `@username`) or profile link (e.g., `https://t.me/username`) to the bot.

## Example Usage

1. **Send a username or profile link:**

    ```sh
    @example_user
    ```

    or

    ```sh
    https://t.me/example_user
    ```

2. **Receive stories:**

    The bot will download and send the stories from the specified user.

## Support

For assistance, join our [Support Chat](https://t.me/mybotsrealm).

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Happy Coding! 🌟
