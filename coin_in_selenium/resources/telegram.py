# import json
import os

# from dotenv import load_dotenv
from httpx import Client


# load_dotenv(".env")
tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
tg_channel = os.getenv("TELEGRAM_CHAT_ID")
base_url = f"https://api.telegram.org/bot{tg_token}"


def send_photo(photo_path: str, caption: str) -> dict:
    """https://core.telegram.org/bots/api#sendphoto"""
    with Client(base_url=base_url, timeout=None) as client:
        return client.post(
            "/sendDocument",
            params={"chat_id": tg_channel, "caption": caption, "parse_mode": "HTML"},
            files={"document": open(photo_path, "rb")},
        ).json()


if __name__ == "__main__":
    print(
        send_photo(
            "/media/60gb/Github/python-selenium-coin/screenshot.png", "Hello_telegram"
        )
    )
