import os
import requests
import feedparser
import json
import time

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# ===== YouTube каналы (RSS) =====
YOUTUBE_FEEDS = {
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UC4yG0dK6Pj4pXH2t3pX5L6A",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UC9p1daynewsxxxxxxxxxxxx"
}

STATE_FILE = "posted.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(state), f)


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data, timeout=20)


def main():
    posted = load_state()

    for channel_name, feed_url in YOUTUBE_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            video_id = entry.get("id")
            if not video_id or video_id in posted:
                continue

            title = entry.title
            link = entry.link
            published = entry.get("published", "")

            message = (
                f"📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
                f"{title}\n\n"
                f"{link}\n\n"
                f"🕒 {published}"
            )

            send_message(message)
            posted.add(video_id)

            time.sleep(2)

    save_state(posted)


if __name__ == "__main__":
    main()
