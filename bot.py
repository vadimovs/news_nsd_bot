import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://feeds.reuters.com/Reuters/worldNews"

KEYWORDS = [
    "ukraine", "russia", "war", "president",
    "election", "putin", "zelensky", "trump",
    "nato", "sanctions"
]


def get_latest_news():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return None

    for entry in feed.entries:
        title = entry.title.lower()
        if any(word in title for word in KEYWORDS):
            return f"📰 {entry.title}\n\n🔗 {entry.link}"

    return None


def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    requests.post(url, data=data)


def main():
    news = get_latest_news()
    if not news:
        print("No political news found")
        return

    post_message(news)


if __name__ == "__main__":
    main()
