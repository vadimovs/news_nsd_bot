import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo

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
    now = datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%H:%M")
        text = (
        "📰 НОВОСТИ СЕГО ДНЯ\n\n"
        "— Тестовая публикация\n"
        "— Бот работает стабильно\n"
        "— GitHub Actions\n\n"
        f"⏰ Время (UTC): {now}"
    )
    post_message(text)

if __name__ == "__main__":
    main()
