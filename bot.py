import os
import json
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# ===== YouTube RSS каналы =====
YOUTUBE_FEEDS = {
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxx",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UCyyyyyyyyyyyyyyyyyyyy"
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
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def main():
    posted = load_state()
    new_posts = []

    for name, feed_url in YOUTUBE_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            video_id = entry.get("id")
            if video_id in posted:
                continue

            title = entry.title
            link = entry.link
            published = entry.published

            message = (
                f"📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
                f"{title}\n\n"
                f"{link}\n\n"
                f"🕒 {published}\n"
                f"📌 Канал: {name}"
            )

            new_posts.append((video_id, message))

    # отправляем старые → новые (по времени)
    for video_id, message in reversed(new_posts):
        send_message(message)
        posted.add(video_id)

    save_state(posted)


if __name__ == "__main__":
    main()
