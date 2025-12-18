import os
import requests
import feedparser
from datetime import datetime
import hashlib
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

YOUTUBE_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw"
STATE_FILE = "youtube_state.json"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=20)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    feed = feedparser.parse(YOUTUBE_RSS)
    if not feed.entries:
        return

    state = load_state()
    last_id = state.get("last_video_id")

    latest = feed.entries[0]
    video_id = latest.id

    if video_id == last_id:
        return  # уже отправляли

    title = latest.title
    link = latest.link
    published = latest.published

    message = (
        "📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
        f"{title}\n\n"
        f"{link}\n\n"
        f"🕒 {published}"
    )

    send_telegram(message)

    state["last_video_id"] = video_id
    save_state(state)


if __name__ == "__main__":
    main()
