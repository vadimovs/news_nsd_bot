import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# ===== YouTube RSS (3 канала) =====
CHANNELS = {
    "Taras Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCJ9n2EJ3bX2G6a1q2Y7RZ7A",
    "Знай Правду": "https://www.youtube.com/feeds/videos.xml?channel_id=UCV7zv5pFz7m5J4nJz7k3x0A",
    "1 Day News": "https://www.youtube.com/feeds/videos.xml?channel_id=UCqRk3FJ3r8Yp9mZJpX2Lx9Q",
}

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })

def main():
    for channel_name, feed_url in CHANNELS.items():
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            continue

        # 🔥 БЕРЁМ ТОЛЬКО САМОЕ НОВОЕ ВИДЕО
        entry = feed.entries[0]

        title = entry.title
        link = entry.link

        message = (
            "📺 Новое видео\n"
            f"Канал: {channel_name}\n\n"
            f"{title}\n\n"
            f"{link}"
        )

        send(message)

if __name__ == "__main__":
    main()
