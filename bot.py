import os
import hashlib
import requests
import feedparser
from openai import OpenAI

# ======================
# НАСТРОЙКИ
# ======================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# RSS-источники
FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

# Файл для дедупликации
POSTED_FILE = "posted.txt"


# ======================
# ВСПОМОГАТЕЛЬНОЕ
# ======================

def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_posted(post_id):
    with open(POSTED_FILE, "a") as f:
        f.write(post_id + "\n")


def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_to_ru(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты переводчик новостей. Переводи текст на чистый, нейтральный русский язык."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def send_to_telegram(message):
    requests.post(
        TELEGRAM_API,
        json={
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        },
        timeout=20
    )


# ======================
# ОСНОВНАЯ ЛОГИКА
# ======================

def main():
    posted = load_posted()

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            original_title = entry.get("title", "").strip()
            original_summary = entry.get("summary", "").strip()
            link = entry.get("link", "").strip()
            source = feed.feed.get("title", "Источник")

            if not original_title or not link:
                continue

            uid = make_id(original_title + link)
            if uid in posted:
                continue

            # ПЕРЕВОД
            title_ru = translate_to_ru(original_title)
            summary_ru = translate_to_ru(original_summary) if original_summary else ""

            message = (
                f"<b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
                f"<b>{title_ru}</b>\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n"
                f"Источник: {source}"
            )

            send_to_telegram(message)
            save_posted(uid)


if __name__ == "__main__":
    main()
