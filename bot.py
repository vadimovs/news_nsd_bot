import os
import hashlib
import json
import time
import requests
import feedparser
from openai import OpenAI

# ====== ENV ======
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ====== FILES ======
POSTED_FILE = "posted_hashes.json"

if not os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "w") as f:
        json.dump([], f)

with open(POSTED_FILE, "r") as f:
    POSTED_HASHES = set(json.load(f))

# ====== FEEDS ======
FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/worldNews",
]

# ====== HELPERS ======
def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def translate_ru(text: str) -> str:
    if not text:
        return ""
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Переведи текст на русский язык, без добавлений."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return r.choices[0].message.content.strip()

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=20)

# ====== MAIN ======
new_hashes = set()

for feed_url in FEEDS:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:
        title_en = entry.get("title", "")
        summary_en = entry.get("summary", "")
        link = entry.get("link", "")
        source = feed.feed.get("title", "Источник")

        uniq = sha(title_en + link)
        if uniq in POSTED_HASHES or uniq in new_hashes:
            continue

        title_ru = translate_ru(title_en)
        summary_ru = translate_ru(summary_en)

        message = (
            f"<b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
            f"<b>{title_ru}</b>\n\n"
            f"{summary_ru}\n\n"
            f"🔗 {link}\n"
            f"Источник: {source}"
        )

        send_telegram(message)
        new_hashes.add(uniq)

        time.sleep(2)

# ====== SAVE ======
POSTED_HASHES.update(new_hashes)
with open(POSTED_FILE, "w") as f:
    json.dump(list(POSTED_HASHES), f)

print(f"Опубликовано новых новостей: {len(new_hashes)}")
