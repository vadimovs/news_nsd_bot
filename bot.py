import os
import json
import hashlib
import requests
import feedparser
from openai import OpenAI

# ======================
# ENV
# ======================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ======================
# FILE FOR DEDUPLICATION
# ======================
POSTED_FILE = "posted.json"

if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        posted = set(json.load(f))
else:
    posted = set()

# ======================
# RSS SOURCES
# ======================
RSS_FEEDS = [
    ("NY Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Reuters", "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
]

# ======================
# FUNCTIONS
# ======================
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_to_ru(text: str) -> str:
    if not text.strip():
        return text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты профессиональный новостной переводчик. Переводи точно, без добавлений."
            },
            {
                "role": "user",
                "content": f"Переведи на русский:\n\n{text}"
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    requests.post(url, json=payload, timeout=20)


# ======================
# MAIN
# ======================
new_posts = []

for source_name, feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries[:5]:
        title_en = entry.get("title", "")
        desc_en = entry.get("summary", "")
        link = entry.get("link", "")

        uid = hash_text(title_en + link)
        if uid in posted:
            continue

        title_ru = translate_to_ru(title_en)
        desc_ru = translate_to_ru(desc_en)

        message = (
            "📰 <b>НОВОСТИ СЕГО ДНЯ</b>\n"
            "🌍 <b>Политика</b>\n\n"
            f"<b>{title_ru}</b>\n\n"
            f"{desc_ru}\n\n"
            f"🔗 <a href='{link}'>Читать полностью</a>\n"
            f"Источник: {source_name}"
        )

        send_to_telegram(message)

        posted.add(uid)
        new_posts.append(uid)

# ======================
# SAVE DEDUP STATE
# ======================
with open(POSTED_FILE, "w", encoding="utf-8") as f:
    json.dump(list(posted), f, ensure_ascii=False)

print(f"Posted {len(new_posts)} new items")
