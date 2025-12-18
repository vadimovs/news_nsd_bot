import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# ===== YouTube RSS (3 канала) =====
CHANNELS = {
    "Taras_Lawyer": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
        "last_file": "last_taras.txt",
    },
    "Znai_Pravdu": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxx",
        "last_file": "last_znai.txt",
    },
    "1_Day_News": {
        "feed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxxxxx",
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

def process_channel(name, feed_url, last_file):
    last_video = read_last(last_file)

    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return

    entry = feed.entries[0]
    video_id = entry.yt_videoid
    video_url = entry.link
    title = entry.title

    if video_id == last_video:
        return

    text = (
        f"📺 Новое видео:\n"
        f"{title}\n"
        f"{video_url}\n\n"
        f"Канал: {name}"
    )

    send_to_telegram(text)
    write_last(last_file, video_id)

def main():
    for name, data in CHANNELS.items():
        process_channel(name, data["feed"], data["last_file"])

if __name__ == "__main__":
    main()
