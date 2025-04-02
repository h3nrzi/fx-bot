import requests
import os
from dotenv import load_dotenv


class TelegramNotifier:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message):
        """Send a message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id:
            print("Telegram bot token or chat ID not configured.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
