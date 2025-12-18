import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

YOUTUBE_FEEDS = {
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxx",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxx",
}

def get_last_telegram_messages():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url).json()
    texts = []
    for item in r.get("result", []):
        msg = item.get("channel_post") or item.get("message")
        if msg and "text" in msg:
            texts.append(msg["text"])
    return texts

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def main():
    already_sent = get_last_telegram_messages()

    for name, feed_url in YOUTUBE_FEEDS.items():
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        video = feed.entries[0]  # ТОЛЬКО ПОСЛЕДНЕЕ
        video_id = video.link

        if any(video_id in msg for msg in already_sent):
            continue

        text = (
            "📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
            f"{video.title}\n\n"
            f"{video.link}\n\n"
            f"📌 Канал: {name}"
        )

        send(text)

if __name__ == "__main__":
    main()
