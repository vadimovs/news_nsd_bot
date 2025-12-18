import feedparser
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

YOUTUBE_CHANNELS = {
    "taras": {
        "rss": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
        "file": "last_tarash.txt",
        "name": "Taras Lawyer"
    },
    "znai": {
        "rss": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6zHf0t1t0F6zE1vZ1tcQ3g",
        "file": "last_znai.txt",
        "name": "Знай Правду"
    },
    "oneday": {
        "rss": "https://www.youtube.com/feeds/videos.xml?channel_id=UCwK5ZpR0Vd3Rz1k1ZzZQ1rA",
        "file": "last_1day.txt",
        "name": "1 Day News"
    }
}

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })

for key, ch in YOUTUBE_CHANNELS.items():
    feed = feedparser.parse(ch["rss"])
    if not feed.entries:
        continue

    latest = feed.entries[0]
    video_id = latest.id

    last_id = ""
    if os.path.exists(ch["file"]):
        with open(ch["file"], "r") as f:
            last_id = f.read().strip()

    if video_id == last_id:
        continue

    text = f"📺 {ch['name']}\n\n{latest.title}\n\n{latest.link}"
    send(text)

    with open(ch["file"], "w") as f:
        f.write(video_id)
