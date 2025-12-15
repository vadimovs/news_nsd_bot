import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

def post_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": True
    }

    r = requests.post(url, data=data)
    print("Telegram response:", r.text)
    
def main():
    now = datetime.utcnow().strftime("%H:%M UTC")
    text = f"🕒 {now}\n\nТест автопубликации. Бот работает."
    post_message(text)

if __name__ == "__main__":
    main()
