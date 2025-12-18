import os
import requests
import feedparser
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

YOUTUBE_CHANNELS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",  # 1day_news
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCk9wZ8z7Z9n6w5nGJ7Z0L6A",  # Taras Lawyer (пример)
]

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })

def main():
    newest = None

    for feed_url in YOUTUBE_CHANNELS:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        entry = feed.entries[0]  # ТОЛЬКО САМОЕ НОВОЕ
        published = entry.get("published_parsed")
        if not published:
            continue

        published_dt = datetime(*published[:6], tzinfo=timezone.utc)

        if newest is None or published_dt > newest["time"]:
            newest = {
                "time": published_dt,
                "title": entry.title,
                "link": entry.link
            }

    if newest:
        msg = f"📺 Новое видео:\n\n{newest['title']}\n\n{newest['link']}"
        send(msg)

if __name__ == "__main__":
    main()
