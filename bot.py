import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

LAST_FILE = "last_video.txt"

YOUTUBE_CHANNELS = {
    "Taras_Lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "Znai_Pravdu": "https://www.youtube.com/feeds/videos.xml?channel_id=UCYwVw5wqvQzjJ9X0lL5PZ0Q",
    "1Day_News": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxvQ4kXzF7n6w7N2x4ZcYkA"
}

def load_last_ids():
    if not os.path.exists(LAST_FILE):
        return {}
    data = {}
    with open(LAST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                k, v = line.strip().split("|", 1)
                data[k] = v
    return data

def save_last_ids(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}|{v}\n")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })

def main():
    last_ids = load_last_ids()
    updated = False

    for name, feed_url in YOUTUBE_CHANNELS.items():
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        latest = feed.entries[0]
        video_id = latest.id

        if last_ids.get(name) == video_id:
            continue

        title = latest.title
        link = latest.link

        message = f"📺 {name}\n\n{title}\n\n{link}"
        send_message(message)

        last_ids[name] = video_id
        updated = True

    if updated:
        save_last_ids(last_ids)

if __name__ == "__main__":
    main()
