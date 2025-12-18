# bot.py
import os
import json
import time
import requests
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC5EoX6PZz2n9XyE6R9nK0kA"  # taras_lawyer
]

STATE_FILE = "posted_videos.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(list(state), f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def parse_feed(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"yt": "http://www.youtube.com/xml/schemas/2015", "atom": "http://www.w3.org/2005/Atom"}
    videos = []
    for entry in root.findall("atom:entry", ns):
        vid = entry.find("yt:videoId", ns).text
        title = entry.find("atom:title", ns).text
        link = entry.find("atom:link", ns).attrib["href"]
        published = entry.find("atom:published", ns).text
        videos.append((vid, title, link, published))
    return videos


def main():
    posted = load_state()
    new_posted = set(posted)

    for feed in YOUTUBE_FEEDS:
        videos = parse_feed(feed)
        for vid, title, link, published in videos:
            if vid in posted:
                continue
            msg = (
                "📺 НОВОЕ ВИДЕО НА YOUTUBE\n\n"
                f"{title}\n\n"
                f"{link}\n"
                f"🕒 {published}"
            )
            send_telegram(msg)
            new_posted.add(vid)
            time.sleep(2)

    save_state(new_posted)


if __name__ == "__main__":
    main()
