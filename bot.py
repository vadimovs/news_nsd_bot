import os
import json
import time
import hashlib
import requests
import feedparser
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

HEADERS = {"User-Agent": "news-bot"}

STATE_FILE = "sent_items.json"

PRIORITY_KEYWORDS = [
    ("trump", 3),
    ("putin", 2),
    ("zelensky", 1),
]

NEWS_SOURCES = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.reuters.com/Reuters/worldNews",
]

YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw"


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(list(state), f)


def score_item(text):
    text = text.lower()
    score = 0
    for key, weight in PRIORITY_KEYWORDS:
        if key in text:
            score += weight
    return score


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False,
    }
    requests.post(url, json=payload, timeout=15)


def fetch_rss():
    items = []
    for feed_url in NEWS_SOURCES:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            uid = hashlib.sha256(link.encode()).hexdigest()
            items.append({
                "uid": uid,
                "title": title,
                "link": link,
                "text": title,
            })
    return items


def fetch_youtube():
    items = []
    feed = feedparser.parse(YOUTUBE_FEED)
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        uid = hashlib.sha256(link.encode()).hexdigest()
        items.append({
            "uid": uid,
            "title": f"📺 YouTube: {title}",
            "link": link,
            "text": title,
        })
    return items


def main():
    sent = load_state()

    candidates = []

    for item in fetch_rss() + fetch_youtube():
        if item["uid"] in sent:
            continue
        item["score"] = score_item(item["text"])
        if item["score"] > 0:
            candidates.append(item)

    if not candidates:
        print("Нет новых приоритетных новостей")
        return

    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]

    message = f"📰 НОВОСТИ СЕГОДНЯ\n\n{best['title']}\n\n{best['link']}"
    send_message(message)

    sent.add(best["uid"])
    save_state(sent)


if __name__ == "__main__":
    main()
