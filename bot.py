import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"

KEYWORDS = [
    "Ukraine", "Russia", "U.S.", "USA", "NATO",
    "president", "election", "sanctions",
    "war", "Putin", "Zelensky"
]

def post_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    requests.post(url, data=data)

def get_latest_news():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return None

    for entry in feed.entries:
        title = entry.title
        title_l = title.lower()

        if any(word.lower() in title_l for word in KEYWORDS):
            return f"📰 {title}\n\n🔗 {entry.link}"

    return None

def main():
    text = get_latest_news()
    if text:
        post_message(text)

if __name__ == "__main__":
    main()
