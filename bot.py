import os
import requests
import re
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# RSS источники
RSS_URLS = [
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

KEYWORDS = [
    "ukraine", "russia", "putin", "zelensky",
    "trump", "war", "nato", "sanctions"
]

STATE_FILE = "last_sent.json"


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"sent": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def translate_ru(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "ru",
        "dt": "t",
        "q": text
    }
    r = requests.get(url, params=params, timeout=10)
    return "".join([x[0] for x in r.json()[0]])


def fetch_news():
    items = []
    for rss in RSS_URLS:
        r = requests.get(rss, timeout=15)
        found = re.findall(
            r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>",
            r.text,
            re.DOTALL
        )
        items.extend(found)
    return items


def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)


def main():
    state = load_state()
    sent = set(state["sent"])

    news = fetch_news()

    for title, link in news:
        title_l = title.lower()

        if not any(k in title_l for k in KEYWORDS):
            continue

        uid = link.strip()
        if uid in sent:
            continue

        title_ru = translate_ru(title)

        text = f"📰 {title_ru}\n\n🔗 {link}"
        post_message(text)

        sent.add(uid)
        state["sent"] = list(sent)[-50:]  # храним последние 50
        save_state(state)
        return  # отправляем ТОЛЬКО ОДНУ новость

    print("No new news")


if __name__ == "__main__":
    main()
