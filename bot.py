import os
import hashlib
import feedparser
import requests
from openai import OpenAI

# ========= НАСТРОЙКИ =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

POSTED_FILE = "posted.txt"

# ========= OPENAI =========
client = OpenAI(api_key=OPENAI_API_KEY)

# ========= ВСПОМОГАТЕЛЬНОЕ =========
def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_posted(posted):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        for p in posted:
            f.write(p + "\n")

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ========= ПЕРЕВОД =========
def translate_to_ru(text: str) -> str:
    if not text.strip():
        return text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Translate the following text into Russian. Preserve meaning, do not add commentary."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()

# ========= TELEGRAM =========
def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

# ========= ОСНОВНАЯ ЛОГИКА =========
def main():
    posted = load_posted()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title_en = entry.get("title", "")
            summary_en = entry.get("summary", "")
            link = entry.get("link", "")

            unique_hash = hash_text(title_en + link)

            if unique_hash in posted:
                continue

            title_ru = translate_to_ru(title_en)
            summary_ru = translate_to_ru(summary_en)

            message = (
                "📰 <b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
                f"<b>{title_ru}</b>\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n\n"
                "Источник: NY Times"
            )

            send_to_telegram(message)
            posted.add(unique_hash)

    save_posted(posted)

# ========= ЗАПУСК =========
if __name__ == "__main__":
    main()
