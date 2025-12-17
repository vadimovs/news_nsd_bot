import os
import hashlib
import json
import time
import requests
import feedparser
from openai import OpenAI

# ====== CONFIG ======
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

STATE_FILE = "posted.json"

# Ключевые персоны + приоритет
KEYWORDS_PRIORITY = [
    ("trump", 3),
    ("putin", 2),
    ("zelensky", 1),
]

FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
]

client = OpenAI(api_key=OPENAI_API_KEY)


# ====== UTILS ======
def load_posted():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_posted(posted):
    with open(STATE_FILE, "w") as f:
        json.dump(list(posted), f)


def hash_item(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def detect_priority(text):
    text_l = text.lower()
    for key, prio in KEYWORDS_PRIORITY:
        if key in text_l:
            return prio
    return 0


def translate_and_summarize(title, summary):
    prompt = f"""
Переведи на русский и кратко перескажи новость.
Без воды. 3–4 предложения.

Заголовок:
{title}

Текст:
{summary}
"""
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def send_to_telegram(text, link):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": f"📰 НОВОСТИ СЕГО ДНЯ\n\n{text}\n\n🔗 {link}",
        "disable_web_page_preview": False,
    }
    requests.post(url, json=payload, timeout=10)


# ====== MAIN ======
def main():
    posted = load_posted()
    candidates = []

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            full_text = f"{title} {summary}"
            prio = detect_priority(full_text)

            if prio == 0:
                continue

            h = hash_item(link)
            if h in posted:
                continue

            candidates.append((prio, title, summary, link, h))

    if not candidates:
        print("Нет новых приоритетных новостей")
        return

    # Сортировка по приоритету
    candidates.sort(reverse=True, key=lambda x: x[0])

    prio, title, summary, link, h = candidates[0]

    text_ru = translate_and_summarize(title, summary)
    send_to_telegram(text_ru, link)

    posted.add(h)
    save_posted(posted)

    print("Отправлено:", title)


if __name__ == "__main__":
    main()
