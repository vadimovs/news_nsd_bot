import os
import json
import time
import requests
import feedparser
from openai import OpenAI

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

POSTED_FILE = "posted.json"

SOURCES = {
    "NY Times": [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    ],
    "Reuters": [
        "https://feeds.reuters.com/Reuters/worldNews"
    ],
    "BBC": [
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ]
}

KEYWORDS_PRIORITY = [
    ("трамп", 3),
    ("trump", 3),
    ("путин", 2),
    ("putin", 2),
    ("зеленск", 1),
    ("zelensky", 1)
]


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_posted(posted):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(posted), f, ensure_ascii=False, indent=2)


def translate(text):
    if not text.strip():
        return text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Переведи текст на русский язык, кратко и нейтрально."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def priority_score(text):
    score = 0
    lower = text.lower()
    for word, weight in KEYWORDS_PRIORITY:
        if word in lower:
            score += weight
    return score


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload, timeout=20)


def main():
    posted = load_posted()
    candidates = []

    for source, feeds in SOURCES.items():
        for feed_url in feeds:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                link = entry.get("link")
                if not link or link in posted:
                    continue

                title = entry.get("title", "")
                summary = entry.get("summary", "")

                score = priority_score(title + " " + summary)
                if score == 0:
                    continue

                candidates.append({
                    "source": source,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "score": score
                })

    if not candidates:
        print("Нет новых приоритетных новостей")
        return

    # 🔥 выбираем САМУЮ приоритетную
    candidates.sort(key=lambda x: x["score"], reverse=True)
    news = candidates[0]

    title_ru = translate(news["title"])
    text_ru = translate(news["summary"])

    message = (
        f"<b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
        f"<b>{title_ru}</b>\n\n"
        f"{text_ru}\n\n"
        f"🔗 {news['link']}\n"
        f"Источник: {news['source']}"
    )

    send_to_telegram(message)

    posted.add(news["link"])
    save_posted(posted)


if __name__ == "__main__":
    main()
