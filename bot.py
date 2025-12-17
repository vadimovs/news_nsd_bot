import os
import hashlib
import json
import requests
import feedparser
from openai import OpenAI

# =======================
# ENV
# =======================
BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
CHANNEL_ID = os.environ["CHANNEL_ID"].strip()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"].strip()

client = OpenAI(api_key=OPENAI_API_KEY)

# =======================
# CONFIG
# =======================
RSS_FEEDS = {
    "Политика": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Экономика": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "Технологии": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
}

POSTED_FILE = "posted.json"
MAX_POSTS = 5


# =======================
# HELPERS
# =======================
def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_posted(data):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f)


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_to_ru(text: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Переведи на русский язык:\n\n{text}",
    )
    return response.output_text.strip()


def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()


# =======================
# MAIN
# =======================
def main():
    posted = load_posted()
    sent = 0

    for category, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            if sent >= MAX_POSTS:
                break

            title_en = entry.title
            summary_en = entry.get("summary", "")
            link = entry.link

            uid = hash_text(title_en + link)
            if uid in posted:
                continue

            try:
                title_ru = translate_to_ru(title_en)
                summary_ru = translate_to_ru(summary_en)
            except Exception as e:
                print("Translation error:", e)
                continue

            message = (
                f"🗞 НОВОСТИ СЕГО ДНЯ\n"
                f"🌍 {category}\n\n"
                f"{title_ru}\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n"
                f"Источник: NY Times"
            )

            try:
                send_to_telegram(message)
                posted.add(uid)
                sent += 1
            except Exception as e:
                print("Telegram error:", e)

    save_posted(posted)


if __name__ == "__main__":
    main()
