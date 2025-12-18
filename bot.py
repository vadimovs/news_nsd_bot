import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

CHANNELS = {
    "Taras Lawyer": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
        "file": "last_taras.txt",
    },
    "Знай Правду": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxx",
        "file": "last_znai.txt",
    },
    "1 Day News": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxx",
        "file": "last_1day.txt",
    },
}

def send(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHANNEL_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
    )

def load_last(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def save_last(path, video_id):
    with open(path, "w", encoding="utf-8") as f:
        f.write(video_id)

def main():
    for channel, cfg in CHANNELS.items():
        feed = feedparser.parse(cfg["feed"])
        if not feed.entries:
            continue

        latest = feed.entries[0]
        video_id = latest.id
        last_id = load_last(cfg["file"])

        if video_id == last_id:
            continue  # НЕТ НОВОГО ВИДЕО

        title = latest.title
        link = latest.link

        text = (
            f"📺 Новое видео\n"
            f"Канал: {channel}\n\n"
            f"{title}\n"
            f"{link}"
        )

        send(text)
        save_last(cfg["file"], video_id)

if __name__ == "__main__":
    main()
