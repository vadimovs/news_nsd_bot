import os
import requests
import feedparser
import hashlib

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# ===== ИСТОЧНИКИ =====
RSS_SOURCES = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.reuters.com/rssFeed/worldNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://apnews.com/rss/apf-world-rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",

    # YouTube канал
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw"
]

PRIORITY = [
    ("trump", 1),
    ("putin", 2),
    ("zelensky", 3)
]

HISTORY_FILE = "sent_news.txt"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        for h in history:
            f.write(h + "\n")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)


def score_item(title):
    t = title.lower()
    for key, score in PRIORITY:
        if key in t:
            return score
    return 99


def fetch_all_news():
    items = []
    for src in RSS_SOURCES:
        feed = feedparser.parse(src)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            uid = hashlib.md5((title + link).encode()).hexdigest()
            items.append({
                "title": title,
                "link": link,
                "uid": uid,
                "priority": score_item(title)
            })
    return items


def main():
    history = load_history()
    news = fetch_all_news()

    # убираем уже отправленные
    fresh = [n for n in news if n["uid"] not in history]

    if not fresh:
        print("Новых новостей нет")
        return

    # сортировка по приоритету
    fresh.sort(key=lambda x: x["priority"])

    item = fresh[0]
    history.add(item["uid"])
    save_history(history)

    message = (
        "📰 НОВОСТИ СЕГОДНЯ\n\n"
        f"{item['title']}\n\n"
        f"{item['link']}"
    )

    send_telegram(message)


if __name__ == "__main__":
    main()
