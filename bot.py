import os
import json
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml"
STATE_FILE = "last_link.json"

KEYWORDS = [
    "ukraine", "russia", "war", "putin", "zelensky",
    "europe", "nato", "sanctions"
]

def load_last_link():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("link")

def save_last_link(link):
    with open(STATE_FILE, "w") as f:
        json.dump({"link": link}, f)

def translate_to_ru(text: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ru",
        "dt": "t",
        "q": text
    }
    r = requests.get(url, params=params)
    return "".join([i[0] for i in r.json()[0]])

def post_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    last_link = load_last_link()

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        title_l = title.lower()

        if last_link == link:
            return

        if any(word in title_l for word in KEYWORDS):
            title_ru = translate_to_ru(title)

            text = (
                "🇺🇦 / 🇺🇸 / 🇷🇺 <b>Политика</b>\n\n"
                f"<b>{title_ru}</b>\n\n"
                f"🔗 {link}\n\n"
                "Источник: <i>NY Times</i>"
            )

            post_message(text)
            save_last_link(link)
            return

if __name__ == "__main__":
    main()
