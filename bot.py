import os
import requests
import feedparser
from openai import OpenAI

# ====== ENV ======
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ====== НАСТРОЙКИ ======
KEYWORDS = [
    "trump", "donald trump", "трамп",
    "putin", "путин",
    "zelensky", "zelenskyy", "зеленский"
]

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"
]

# ====== TELEGRAM ======
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=20)

# ====== OPENAI ======
def translate_and_summarize(text):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты новостной редактор. Переведи на русский и кратко перескажи."},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()

# ====== MAIN ======
def main():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            text_all = f"{title} {summary}".lower()

            if not any(k in text_all for k in KEYWORDS):
                continue

            ru_text = translate_and_summarize(f"{title}\n\n{summary}")

            message = (
                "🗞 <b>НОВОСТИ СЕГО ДНЯ</b>\n"
                "🌍 <b>Политика</b>\n\n"
                f"<b>{ru_text}</b>\n\n"
                f"🔗 {link}\n"
                f"Источник: {feed.feed.get('title', 'Источник')}"
            )

            send_to_telegram(message)
            return  # ❗️ ОДНА новость за запуск

    print("Подходящих новостей не найдено")

if __name__ == "__main__":
    main()
