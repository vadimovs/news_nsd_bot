import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

def post_message(text):
    feed = feedparser.parse("https://www.unian.net/rss/world")
    if not feed.entries:
        return None
    
RSS_URL = "https://feeds.reuters.com/Reuters/worldNews"

KEYWORDS = [
    "Ukraine", "Russia", "U.S.", "USA", "NATO",
    "president", "election", "sanctions",
    "war", "Putin", "Zelensky", "Trump"
]

def get_latest_news():
    resp = requests.get(RSS_URL, timeout=10)
    if resp.status_code != 200:
        return None

    items = resp.text.split("<item>")
    for item in items[1:]:
        title_part = item.split("<title>")[1].split("</title>")[0]
        link_part = item.split("<link>")[1].split("</link>")[0]

        title = title_part.strip()
        link = link_part.strip()

        for kw in KEYWORDS:
            if kw.lower() in title.lower():
                return f"📰 {title}\n\n🔗 {link}"

    return None

def main():
    news = get_latest_news()
    if not news:
        print("No political news")
        return

    post_message(news)

if __name__ == "__main__":
    main()
