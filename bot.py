import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

CHANNELS = {
    "Taras Lawyer": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
        "last_file": "last_taras.txt",
    },
    "Знай Правду": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxx",
        "last_file": "last_znai.txt",
    },
    "1 Day News": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCyyyyyyyyyyyyyyyyyyyy",
        "last_file": "last_1day.txt",
    },
}

def read_last(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_last(path, value):
    with open(path, "w", encoding="utf-8") as f:
        f.write(value)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })

def main():
    for name, cfg in CHANNELS.items():
        feed = feedparser.parse(cfg["feed"])
        if not feed.entries:
            continue

        latest = feed.entries[0]
        video_id = latest.id

        last_id = read_last(cfg["last_file"])

        if video_id == last_id:
            continue  # ❌ уже отправляли

        title = latest.title
        link = latest.link

        message = (
            f"📺 Новое видео\n"
            f"Канал: {name}\n\n"
            f"{title}\n"
            f"{link}"
        )

        send_to_telegram(message)
        write_last(cfg["last_file"], video_id)

if __name__ == "__main__":
    main()
