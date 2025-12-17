import os
import hashlib
import requests
import feedparser
from openai import OpenAI

# === ENV ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# === RSS SOURCES ===
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
]

# === DEDUP STORAGE ===
POSTED_FILE = "posted.txt"


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


def save_posted(posted):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        for p in posted:
            f.write(p + "\n")


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_to_ru(text):
    if not text:
        return ""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Переведи текст на русский язык. Без комментариев, только перевод."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=30)


def main():
    posted = load_posted()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title_en = entry.get("title", "")
            summary_en = entry.get("summary", "")
            link = entry.get("link", "")

            uid = hash_text(title_en + link)
            if uid in posted:
                continue

            title_ru = translate_to_ru(title_en)
            summary_ru = translate_to_ru(summary_en)

            message = (
                "🗞 <b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
                f"<b>{title_ru}</b>\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n"
                "Источник: NY Times"
            )

            send_to_telegram(message)
            posted.add(uid)

    save_posted(posted)


if __name__ == "__main__":
    main()
