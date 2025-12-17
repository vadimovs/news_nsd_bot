import os
import hashlib
import json
import requests
import feedparser
from openai import OpenAI

# ================== ENV ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not BOT_TOKEN or not CHANNEL_ID:
    raise RuntimeError("BOT_TOKEN или CHANNEL_ID не заданы")

# OpenAI может быть временно недоступен — не валим бота
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# ================== FILES ==================
POSTED_FILE = "posted.json"

# ================== RSS ==================
RSS_FEEDS = [
    ("NY Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Reuters", "https://feeds.reuters.com/Reuters/worldNews"),
]

# ================== UTILS ==================
def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_posted(data):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(data), f)

def hash_item(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ================== TRANSLATION ==================
def translate(text):
    if not client:
        return text  # fallback

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Переведи текст на русский язык. Без добавлений."
                },
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return text  # не падаем

# ================== TELEGRAM ==================
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

# ================== MAIN ==================
def main():
    posted = load_posted()
    new_posted = set(posted)

    for source, url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            uid = hash_item(title + link)
            if uid in posted:
                continue

            title_ru = translate(title)
            summary_ru = translate(summary)

            message = (
                f"<b>НОВОСТИ СЕГО ДНЯ</b>\n"
                f"🌍 Политика\n\n"
                f"<b>{title_ru}</b>\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n"
                f"Источник: {source}"
            )

            try:
                send_to_telegram(message)
                new_posted.add(uid)
            except Exception as e:
                print("Telegram error:", e)

    save_posted(new_posted)

if __name__ == "__main__":
    main()
