import os
import requests
from bs4 import BeautifulSoup

URL = "https://faculty.univ-eloued.dz/faculty/fll/category/2"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_FILE = "last_post.txt"


def get_latest_post():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if "/post/" not in href:
            continue

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        if href.startswith("/"):
            href = "https://faculty.univ-eloued.dz" + href

        print("Found:", title)
        print("URL:", href)

        return title, href

    print("No announcement found")
    return None, None


def read_last():
    if not os.path.exists(LAST_FILE):
        return ""

    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last(link):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(link)


def send_telegram(title, link):

    text = f"""📢 إعلان جديد

{title}

🔗 {link}
"""

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

    print("Telegram status:", response.status_code)
    print(response.text)


def main():

    print("Starting monitor...")

    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing")
        return

    if not CHAT_ID:
        print("ERROR: CHAT_ID missing")
        return

    title, link = get_latest_post()

    if not link:
        print("No announcement found")
        return

    print("Title:", title)
    print("Link:", link)

    last = read_last()

    if link == last:
        print("No new announcement")
        return

    send_telegram(title, link)

    save_last(link)

    print("Announcement sent")


if __name__ == "__main__":
    main()
