import os
import requests
import feedparser
import json
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# ===== YOUTUBE КАНАЛЫ =====
YOUTUBE_CHANNELS = [
    "UCgtxz5_xa6xkDTghNPkuRYw",   # Знай Правду
    "UC0r4n3X5Q6nqQZxv6yTaras",   # Тарас Юрист (через @taras_lawyer)
    "UC1daynewsxxxxxxxxxxxx",    # 1day_news
]

# ===== ФАЙЛ ДЕДУПЛИКАЦИИ =====
SEEN_FILE = "seen_videos.json"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload, timeout=20)


def fetch_channel_videos(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    return feedparser.parse(feed_url).entries


def main():
    seen = load_seen()
    new_seen = set(seen)

    for channel in YOUTUBE_CHANNELS:
        videos = fetch_channel_videos(channel)

        for video in videos:
            video_id = video.get("yt_videoid")
            if not video_id or video_id in seen:
                continue

            title = video.title
            link = video.link
            published = video.published

            text = (
                "📺 <b>НОВОЕ ВИДЕО НА YOUTUBE</b>\n\n"
                f"{title}\n\n"
                f"{link}\n\n"
                f"🕒 {published}"
            )

            send_to_telegram(text)
            new_seen.add(video_id)

    save_seen(new_seen)


if __name__ == "__main__":
    main()
