import os
import requests
import re
from xml.etree import ElementTree

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

YOUTUBE_FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCZ2wD3kY9Zp8j04YfGLmRoQ"
]

STATE_FILE = "posted_youtube.txt"


def load_posted():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_posted(ids):
    with open(STATE_FILE, "w") as f:
        for i in ids:
            f.write(i + "\n")


def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def parse_feed(url):
    r = requests.get(url, timeout=15)
    root = ElementTree.fromstring(r.text)
    ns = {"yt": "http://www.youtube.com/xml/schemas/2015"}
    videos = []
    for entry in root.findall("entry"):
        vid = entry.find("yt:videoId", ns).text
        title = entry.find("title").text
        link = entry.find("link").attrib["href"]
        videos.append((vid, title, link))
    return videos


def main():
    posted = load_posted()
    new_posted = set(posted)

    for feed in YOUTUBE_FEEDS:
        videos = parse_feed(feed)
        for vid, title, link in videos:
            if vid in posted:
                continue
            send(f"🎥 {title}\n\n{link}")
            new_posted.add(vid)

    save_posted(new_posted)


if __name__ == "__main__":
    main()
