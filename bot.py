import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

YOUTUBE_RSS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",  # канал 1
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxx",  # Тарас Юрист (вставь правильный ID)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyyyyyyyyyyyyyyyyyyyy"   # 1day_news (вставь правильный ID)
]

KEYWORDS = ["trump", "putin", "zelensky", "зеленськ", "путін", "трамп"]

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data, timeout=15)

def main():
    for rss in YOUTUBE_RSS:
        feed = feedparser.parse(rss)
        if not feed.entries:
            continue

        entry = feed.entries[0]  # ТОЛЬКО САМОЕ НОВОЕ
        title = entry.title.lower()

        if any(k in title for k in KEYWORDS):
            message = f"▶️ {entry.title}\n\n{entry.link}"
            post_message(message)

if __name__ == "__main__":
    main()
