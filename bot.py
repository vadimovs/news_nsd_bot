import os
import json
import requests
import feedparser
from datetime import datetime
from openai import OpenAI

# ====== CONFIG ======
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

STATE_FILE = "sent_links.json"

KEYWORDS_PRIORITY = [
    ("trump", "Трамп"),
    ("putin", "Путин"),
    ("zelensky", "Зеленский"),
]

RSS_SOURCES = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
]

client = OpenAI(api_key=OPENAI_API_KEY)

# ====================

def load_sent():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(STATE_FILE, "w") as f:
        json.dump(list(sent), f)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=15)

def translate_and_summarize(title, summary):
    prompt = f"""
Переведи на русский и кратко перескажи новость.
Сначала заголовок, потом 3–4 предложения текста.

ЗАГОЛОВОК:
{title}

ТЕКСТ:
{summary}
"""
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return r.choices[0].message.content.strip()

def main():
    sent_links = load_sent()
    candidates = []

    for feed_url in RSS_SOURCES:
        feed = feedparser.parse(feed_url)
        for e in feed.entries:
            link = e.get("link", "")
            if not link or link in sent_links:
                continue

            text_blob = (e.get("title", "") + " " + e.get("summary", "")).lower()

            for idx, (kw, name_ru) in enumerate(KEYWORDS_PRIORITY):
                if kw in text_blob:
                    candidates.append({
                        "priority": idx,
                        "name": name_ru,
                        "entry": e
                    })
                    break

    if not candidates:
        print("Нет подходящих новостей")
        return

    # сортировка по приоритету
    candidates.sort(key=lambda x: x["priority"])
    chosen = candidates[0]
    e = chosen["entry"]

    title_en = e.get("title", "")
    summary_en = e.get("summary", "")
    link = e.get("link", "")

    text_ru = translate_and_summarize(title_en, summary_en)

    message = (
        f"<b>НОВОСТИ СЕГО ДНЯ</b>\n"
        f"🌍 Политика\n\n"
        f"{text_ru}\n\n"
        f"🔗 {link}\n"
        f"Источник: NY Times"
    )

    send_to_telegram(message)

    sent_links.add(link)
    save_sent(sent_links)

    print("Новость отправлена:", link)

if __name__ == "__main__":
    main()
