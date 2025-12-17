import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"

KEYWORDS = [
    "ukraine", "russia", "war", "putin", "zelensky",
    "nato", "europe", "u.s.", "usa"
]

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_last_channel_message():
    url = f"{TELEGRAM_API}/getUpdates"
    r = requests.get(url, timeout=15)
    data = r.json()

    if not data.get("result"):
        return ""

    texts = []
    for item in data["result"]:
        msg = item.get("channel_post") or item.get("message")
        if msg and msg.get("chat", {}).get("id") == int(CHANNEL_ID):
            texts.append(msg.get("text", ""))

    return texts[-1] if texts else ""

def post_message(text):
    url = f"{TELEGRAM_API}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False  # КАРТОЧКИ ВКЛЮЧЕНЫ
    }
    requests.post(url, data=data, timeout=15)

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    last_post = get_last_channel_message().lower()

    entry = feed.entries[0]  # БЕРЁМ ТОЛЬКО САМУЮ НОВУЮ
    title = entry.title
    link = entry.link
    title_l = title.lower()

    if title_l in last_post:
        return  # УЖЕ БЫЛО

    if any(word in title_l for word in KEYWORDS):
        text = f"📰 {title}\n\n🔗 {link}"
        post_message(text)

if __name__ == "__main__":
    main()
