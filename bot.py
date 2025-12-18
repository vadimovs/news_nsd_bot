import os
import json
import requests
from datetime import datetime, timezone
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

STATE_FILE = "yt_state.json"

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC7pGq6bQbY8h4YkYz2G9J3Q"  # taras_lawyer
]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=20)


def main():
    state = load_state()
    updated = False

    for feed_url in YOUTUBE_FEEDS:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        latest = feed.entries[0]
        video_id = latest.get("yt_videoid")
        published = latest.get("published")

        if not video_id:
            continue

        if state.get(feed_url) == video_id:
            continue

        title = latest.title
        link = latest.link

        msg = (
            "📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
            f"{title}\n\n"
            f"{link}\n\n"
            f"🕒 {published}"
        )

        send_telegram(msg)
        state[feed_url] = video_id
        updated = True

    if updated:
        save_state(state)


if __name__ == "__main__":
    main()
