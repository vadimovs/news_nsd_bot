import os
import json
import time
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# === YOUTUBE КАНАЛЫ ===
YOUTUBE_CHANNELS = [
    "UCgtxz5_xa6xkDTghNPkuRYw",   # канал 1
    "UCxxxxxxxxxxxxxxxxxxxx",   # канал 2
]

# === ФАЙЛ ДЕДУПЛИКАЦИИ ===
SEEN_FILE = "seen_videos.json"

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def fetch_channel_videos(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    return feed.entries

def main():
    seen = load_seen()
    new_seen = set(seen)

    for channel in YOUTUBE_CHANNELS:
        videos = fetch_channel_videos(channel)

        for video in videos:
            video_id = video.get("id")
            if video_id in seen:
                continue

            title = video.get("title", "Новое видео")
            link = video.get("link")
            published = video.get("published", "")

            message = (
                "📺 <b>НОВОЕ ВИДЕО НА YOUTUBE</b>\n\n"
                f"<b>{title}</b>\n\n"
                f"{link}\n\n"
                f"🕒 {published}"
            )

            send_to_telegram(message)
            new_seen.add(video_id)

            time.sleep(2)  # чтобы Telegram не резал

    save_seen(new_seen)

if __name__ == "__main__":
    main()
