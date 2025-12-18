import os
import json
import requests
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# ===== YouTube RSS каналы =====
YOUTUBE_CHANNELS = {
    "1day_news": "https://www.youtube.com/feeds/videos.xml?channel_id=UCgtxz5_xa6xkDTghNPkuRYw",
    "taras_lawyer": "https://www.youtube.com/feeds/videos.xml?channel_id=UCf7uJ4w8z5d7j4w9Zl8N8Mw",
    "news_channel_3": "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxxxxxxxxx"
}

STATE_FILE = "yt_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def parse_youtube_feed(url):
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return []

    entries = []
    for block in r.text.split("<entry>")[1:]:
        title = block.split("<title>")[1].split("</title>")[0]
        link = block.split('href="')[1].split('"')[0]
        published = block.split("<published>")[1].split("</published>")[0]
        entries.append((title, link, published))
    return entries

def main():
    state = load_state()
    updated = False

    for name, feed_url in YOUTUBE_CHANNELS.items():
        last_time = state.get(name)
        videos = parse_youtube_feed(feed_url)

        for title, link, published in videos:
            published_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))

            if last_time:
                last_dt = datetime.fromisoformat(last_time)
                if published_dt <= last_dt:
                    continue

            message = f"📺 {title}\n\n{link}"
            post_message(message)

            state[name] = published_dt.isoformat()
            updated = True

    if updated:
        save_state(state)

if __name__ == "__main__":
    main()
