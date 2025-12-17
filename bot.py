import os
import json
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
STATE_FILE = "last.json"

# ====== ВСПОМОГАТЕЛЬНОЕ ======

def load_last_link():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("link")

def save_last_link(link):
    with open(STATE_FILE, "w") as f:
        json.dump({"link": link}, f)

def translate_to_ru(text: str) -> str:
    url = "https://libretranslate.de/translate"
    data = {
        "q": text,
        "source": "en",
        "target": "ru",
        "format": "text"
    }
    try:
        r = requests.post(url, data=data, timeout=15)
        return r.json()["translatedText"]
    except Exception:
        return text  # если переводчик упал — шлём как есть

def post_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False  # КАРТОЧКА ВКЛЮЧЕНА
    }
    requests.post(url, data=data)

# ====== ОСНОВНАЯ ЛОГИКА ======

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    last_link = load_last_link()

    for entry in feed.entries:
        title_en = entry.title
        link = entry.link

        if link == last_link:
            return  # уже публиковали

        title_ru = translate_to_ru(title_en)

        text = (
            f"📰 {title_ru}\n\n"
            f"🔗 {link}"
        )

        post_message(text)
        save_last_link(link)
        return

if __name__ == "__main__":
    main()
