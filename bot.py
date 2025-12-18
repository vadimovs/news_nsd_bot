import os
import json
import hashlib
import requests
import feedparser
from openai import OpenAI

# ====== ENV ======
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SENT_FILE = "sent.json"

# ====== LOAD SENT ======
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent_hashes = set(json.load(f))
else:
    sent_hashes = set()

# ====== SOURCES ======
FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
]

# ====== PRIORITY ======
KEYWORDS = {
    "trump": 1,
    "putin": 2,
    "zelensky": 3,
}

# ====== HELPERS ======
def hash_news(title, link):
    return hashlib.sha256(f"{title}{link}".encode()).hexdigest()

def get_priority(text):
    text = text.lower()
    for k, p in KEYWORDS.items():
        if k in text:
            return p
    return None

def translate_and_summarize(text):
    prompt = f"""
Переведи на русский и кратко перескажи новость (3–4 предложения).
Без домыслов, только факты.

Текст:
{text}
"""
    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return r.choices[0].message.content.strip()

def send_to_telegram(text, link):
    msg = f"{text}\n\n🔗 {link}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHANNEL_ID,
        "text": msg,
        "disable_web_page_preview": False
    })

# ====== MAIN ======
candidates = []

for feed_url in FEEDS:
    feed = feedparser.parse(feed_url)
    for e in feed.entries[:10]:
        title = e.title
        link = e.link
        summary = e.get("summary", "")

        h = hash_news(title, link)
        if h in sent_hashes:
            continue

        pr = get_priority(title + " " + summary)
        if pr is None:
            continue

        candidates.append({
            "priority": pr,
            "title": title,
            "summary": summary,
            "link": link,
            "hash": h
        })

# ====== PICK BEST ======
if not candidates:
    print("Нет новых подходящих новостей")
    exit(0)

candidates.sort(key=lambda x: x["priority"])
news = candidates[0]

text_ru = translate_and_summarize(news["summary"] or news["title"])
send_to_telegram(text_ru, news["link"])

sent_hashes.add(news["hash"])
with open(SENT_FILE, "w", encoding="utf-8") as f:
    json.dump(list(sent_hashes), f, ensure_ascii=False)

print("Новость отправлена")
