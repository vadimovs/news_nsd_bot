import os
import requests
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

RSS_URL = "https://feeds.reuters.com/Reuters/worldNews"

KEYWORDS = [
    "ukraine", "russia", "u.s.", "usa", "nato",
    "president", "election", "sanctions",
    "war", "putin", "zelensky", "trump"
]


def post_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    r = requests.post(url, data=data)
    print("Telegram response:", r.text)


def get_latest_news():
    resp = requests.get(RSS_URL, timeout=15)
    if resp.status_code != 200:
        return None

    items = re.findall(
        r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>",
        resp.text,
        re.DOTALL
    )

    for title, link in items:
        title_lower = title.lower()
        for kw in KEYWORDS:
            if kw in title_lower:
                return f"📰 {title}\n\n🔗 {link}"

    return None


def main():
    news = get_latest_news()
    if not news:
        print("No political news found")
        return

    post_message(news)


if __name__ == "__main__":
    main()
