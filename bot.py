import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

YOUTUBE_FEEDS = {
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UC0z9qR4K9X6sFzq8h8v9wQ",
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UCqJm4C0b5b8Jxk9rPZx8c8A",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UCV7k9zXz7yZpY9t5mR8d6sA",
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

        # ❗ Берём ТОЛЬКО самое новое видео
        video = feed.entries[0]

        title = video.title
        link = video.link

        message = (
            f"📺 Новое видео\n"
            f"Канал: {channel_name}\n\n"
            f"{title}\n"
            f"{link}"
        )

        send_message(message)

if __name__ == "__main__":
    main()
