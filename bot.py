import os
import json
import hashlib
import requests
import feedparser
from pathlib import Path
from openai import OpenAI

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

STATE_FILE = Path("posted.json")

RSS_FEEDS = {
    "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================== ХРАНЕНИЕ СОСТОЯНИЯ ==================

def load_posted():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()

def save_posted(posted):
    STATE_FILE.write_text(json.dumps(list(posted)))

def make_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ================== ПЕРЕВОД ==================

def translate_ru(text):
    if not text:
        return ""
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Переведи текст на русский язык. Без пояснений, только перевод."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.2
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        print("Ошибка перевода:", e)
        return text

# ================== TELEGRAM ==================

def post_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data, timeout=15)

# ================== ОСНОВНАЯ ЛОГИКА ==================

def main():
    posted = load_posted()

    for source, rss_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(rss_url)
        except Exception as e:
            print(f"Ошибка RSS {source}:", e)
            continue

        for entry in feed.entries[:5]:
            title_en = entry.get("title", "")
            link = entry.get("link", "")
            summary_en = entry.get("summary", "")

            uid = make_hash(title_en + link)
            if uid in posted:
                continue  # 🔁 уже публиковали

            title_ru = translate_ru(title_en)
            summary_ru = translate_ru(summary_en)

            message = (
                f"🇺🇦 / 🇺🇸 / 🇷🇺  Политика\n\n"
                f"{title_ru}\n\n"
                f"🔗 {link}\n\n"
                f"Источник: {source}"
            )

            post_to_telegram(message)
            posted.add(uid)
            save_posted(posted)

            return  # ⏱ публикуем только одну новость за запуск

if __name__ == "__main__":
    main()
