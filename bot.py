import os
import requests
import xml.etree.ElementTree as ET

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# ===== YOUTUBE КАНАЛЫ (МОЖЕШЬ ДОБАВЛЯТЬ СЮДА) =====
YOUTUBE_CHANNELS = [
    "UCgtxz5_xa6xkDTghNPkuRYw",   # канал 1
    "UCxxxxxxxxxxxxxxxxxx",      # канал 2 (если добавишь)
]

# ===== ФАЙЛ ДЛЯ ДЕДУПЛИКАЦИИ =====
SEEN_FILE = "seen_videos.txt"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for v in seen:
            f.write(v + "\n")


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)


def fetch_channel_videos(channel_id):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    r = requests.get(rss_url, timeout=15)
    root = ET.fromstring(r.text)
    ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}

    videos = []
    for entry in root.findall("entry"):
        video_id = entry.find("yt:videoId", ns).text
        title = entry.find("title").text
        link = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((video_id, title, link))
    return videos


def main():
    seen = load_seen()

    for channel in YOUTUBE_CHANNELS:
        videos = fetch_channel_videos(channel)

        for video_id, title, link in videos:
            if video_id in seen:
                continue

            message = f"📺 НОВОЕ ВИДЕО\n\n{title}\n\n{link}"
            send_message(message)

            seen.add(video_id)

    save_seen(seen)


if __name__ == "__main__":
    main()
