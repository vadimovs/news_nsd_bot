import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

YOUTUBE_CHANNELS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",  # канал 1
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxx",     # Тарас (вставь ID)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyyyyyyyyyyyyyyyyy"      # 1day_news
]

LAST_FILE = "last_video.txt"


def read_last():
    try:
        with open(LAST_FILE, "r") as f:
            return f.read().strip()
    except:
        return "EMPTY"


def write_last(video_id):
    with open(LAST_FILE, "w") as f:
        f.write(video_id)


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHANNEL_ID, "text": msg}
    )


def main():
    last_id = read_last()

    for feed_url in YOUTUBE_CHANNELS:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        entry = feed.entries[0]
        video_id = entry.id

        if video_id == last_id:
            continue

        text = f"📺 Новое видео:\n{entry.title}\n{entry.link}"
        send(text)
        write_last(video_id)
        break


if __name__ == "__main__":
    main()
