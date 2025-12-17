import os
import requests
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

RSS_SOURCES = [
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

# ❗ ТОЛЬКО ЭТИ ЛЮДИ
PERSONS = [
    "trump", "donald trump",
    "zelensky", "zelenskyy",
    "putin", "vladimir putin"
]

# файл для дедупликации
POSTED_FILE = "posted.txt"


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(f.read().splitlines())


def save_posted(link):
    with open(POSTED_FILE, "a") as f:
        f.write(link + "\n")


def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)


def fetch_news():
    posted = load_posted()

    for rss in RSS_SOURCES:
        r = requests.get(rss, timeout=15)
        items = re.findall(
            r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>",
            r.text,
            re.DOTALL
        )

        for title, link in items:
            title_low = title.lower()

            # 🔥 ФИЛЬТР ТОЛЬКО ПО ИМЕНАМ
            if not any(name in title_low for name in PERSONS):
                continue

            if link in posted:
                continue

            text = f"📰 {title}\n\n🔗 {link}"
            post_message(text)
            save_posted(link)
            return  # ⛔️ ТОЛЬКО ОДНА НОВОСТЬ ЗА ЗАПУСК

    print("No matching news found")


if __name__ == "__main__":
    fetch_news()
