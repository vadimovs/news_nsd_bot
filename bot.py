import os
import json
import requests
import feedparser
from pathlib import Path

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_FEEDS = [
    ("NY Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Reuters", "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
]

KEYWORDS = [
    "ukraine", "russia", "war", "putin", "zelensky",
    "nato", "europe", "usa", "united states"
]

STATE_FILE = Path("posted_links.json")

# ---------- STATE ----------

def load_posted():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def save_posted(links):
    STATE_FILE.write_text(json.dumps(list(links)))

# ---------- TELEGRAM ----------

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

# ---------- MAIN ----------

def main():
    posted = load_posted()

    for source, feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            link = entry.get("link")
            title = entry.get("title", "")
            title_l = title.lower()

            if not link or link in posted:
                continue

            if not any(k in title_l for k in KEYWORDS):
                continue

            text = (
                f"🇺🇦 / 🇺🇸 / 🇷🇺 Политика\n\n"
                f"{title}\n\n"
                f"🔗 {link}\n\n"
                f"Источник: {source}"
            )

            post_message(text)

            posted.add(link)
            save_posted(posted)

            return  # 🔴 СТРОГО ОДНА НОВОСТЬ ЗА ЗАПУСК

if __name__ == "__main__":
    main()
