import os
import hashlib
import requests
import feedparser
from openai import OpenAI

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

POSTED_FILE = "posted.txt"

RSS_SOURCES = [
    # NY Times
    ("NY Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("NY Times Politics", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"),

    # BBC
    ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC Politics", "https://feeds.bbci.co.uk/news/politics/rss.xml"),

    # Reuters
    ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
    ("Reuters Politics", "https://feeds.reuters.com/Reuters/politicsNews"),

    # Associated Press
    ("AP World", "https://apnews.com/rss/apf-worldnews"),
    ("AP Politics", "https://apnews.com/rss/apf-politics"),

    # Al Jazeera
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),

    # Deutsche Welle
    ("DW World", "https://rss.dw.com/xml/rss-en-world")
]


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())


def save_posted(posted):
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        for h in posted:
            f.write(h + "\n")


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_to_ru(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты переводчик новостей. Переводи на чистый литературный русский."},
            {"role": "user", "content": text}
        ],
        temperature=0.2
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
    requests.post(url, json=payload, timeout=20)


def main():
    posted = load_posted()
    sent_count = 0

    for source_name, rss_url in RSS_SOURCES:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:3]:  # берем до 3 новостей с источника
            title_en = entry.get("title", "")
            summary_en = entry.get("summary", "")
            link = entry.get("link", "")

            uid = hash_text(title_en + link)
            if uid in posted:
                continue

            title_ru = translate_to_ru(title_en)
            summary_ru = translate_to_ru(summary_en)

            message = (
                f"<b>НОВОСТИ СЕГО ДНЯ</b>\n\n"
                f"🌍 <b>{title_ru}</b>\n\n"
                f"{summary_ru}\n\n"
                f"🔗 {link}\n"
                f"Источник: {source_name}"
            )

            send_to_telegram(message)
            posted.add(uid)
            sent_count += 1

            if sent_count >= 10:
                break

        if sent_count >= 10:
            break

    save_posted(posted)


if __name__ == "__main__":
    main()
