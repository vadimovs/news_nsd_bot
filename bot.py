import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

def post_message(text):
    def get_latest_news():
    feed = feedparser.parse("https://www.unian.net/rss/world")
    if not feed.entries:
        return None

    keywords = [
        "трамп", "зеленск", "путин",
        "сша", "росси", "украин",
        "нато", "выбор", "президент"
    ]

    for entry in feed.entries:
        title = entry.title.lower()

        if any(word in title for word in keywords):
            return f"📰 {entry.title}\n\n🔗 {entry.link}"

    return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }

    r = requests.post(url, data=data)
    print("Telegram response:", r.text)
    
def main():
    news = get_latest_news()
    if not news:
        return

    post_message(news)

if __name__ == "__main__":
    main()
