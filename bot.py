import os
import json
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"

KEYWORDS = [
    "ukraine", "russia", "war", "putin", "zelensky",
    "nato", "europe", "sanctions"
]

STATE_FILE = "last_link.json"


def load_last_link():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("link")


def save_last_link(link):
    with open(STATE_FILE, "w") as f:
        json.dump({"link": link}, f)


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

    last_link = load_last_link()

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        title_l = title.lower()

        if link == last_link:
            return  # уже публиковали

        if any(word in title_l for word in KEYWORDS):
            text = f"📰 {title}\n\n🔗 {link}"
            post_message(text)
            save_last_link(link)
            return


if __name__ == "__main__":
    main()
