import os
import json
import hashlib
import requests
import feedparser
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

STATE_FILE = "state.json"

RSS_SOURCES = {
    "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    "BBC": "https://feeds.bbci.co.uk/news/world/rss.xml"
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"posted": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def hash_item(title, link):
    return hashlib.sha256(f"{title}{link}".encode()).hexdigest()

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data, timeout=15)

def fetch_feed(name, url):
    try:
        return feedparser.parse(url)
    except Exception as e:
        print(f"[WARN] {name} RSS error:", e)
        return None

def main():
    state = load_state()

    for source, url in RSS_SOURCES.items():
        feed = fetch_feed(source, url)
        if not feed or not feed.entries:
            continue

        for entry in feed.entries[:5]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            uid = hash_item(title, link)
            if uid in state["posted"]:
                continue

            text = (
                f"📰 {title}\n\n"
                f"🔗 {link}\n\n"
                f"Источник: {source}"
            )

            post_message(text)
            state["posted"].append(uid)
            save_state(state)
            return  # публикуем ОДНУ новость за запуск

if __name__ == "__main__":
    main()
