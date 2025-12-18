import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

YOUTUBE_FEEDS = {
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCYwVZ2qkK8sG6nQ6X3xY7XA",
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UC0n8YH6sZ0K0QK9yKpZqzDQ",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UC5WZzqgYH7d8dZ5x8nZp5rA",
}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data, timeout=10)

def main():
    for channel_name, feed_url in YOUTUBE_FEEDS.items():
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            continue

        latest = feed.entries[0]
        title = latest.title
        link = latest.link

        message = (
            f"📺 Новое видео\n"
            f"Канал: {channel_name}\n\n"
            f"{title}\n"
            f"{link}"
        )

        send_message(message)

if __name__ == "__main__":
    main()
