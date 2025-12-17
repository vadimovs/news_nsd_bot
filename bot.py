import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"

KEYWORDS = [
    "ukraine", "russia", "war", "putin", "zelensky",
    "nato", "sanctions", "europe"
]

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    entry = feed.entries[0]  # 🔥 ВСЕГДА ТОЛЬКО САМАЯ НОВАЯ
    title = entry.title
    link = entry.link

    title_l = title.lower()
    if not any(word in title_l for word in KEYWORDS):
        return

    text = f"📰 {title}\n\n🔗 {link}"
    post_message(text)

if __name__ == "__main__":
    main()
