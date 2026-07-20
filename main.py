import os
import requests
from bs4 import BeautifulSoup

URL = "https://faculty.univ-eloued.dz/faculty/fll/category/2"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_FILE = "last_post.txt"


def read_last():
    if not os.path.exists(LAST_FILE):
        return ""

    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last(link):
    with open(LAST_FILE, "r+", encoding="utf-8") as f:
        f.seek(0)
        f.write(link)
        f.truncate()


def get_new_posts():

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

    last = read_last()

    posts = []

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if "/post/" not in href:
            continue

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        if href.startswith("/"):
            href = "https://faculty.univ-eloued.dz" + href

        # توقف عند آخر إعلان منشور
        if href == last:
            break

        posts.append((title, href))


    # حذف التكرار
    unique_posts = []
    seen = set()

    for post in posts:
        if post[1] not in seen:
            unique_posts.append(post)
            seen.add(post[1])


    # من الأقدم إلى الأحدث
    unique_posts.reverse()

    return unique_posts


def send_telegram(title, link):

    text = f"""📢 إعلان جديد

📝 {title}

🔗 {link}
"""

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=30
    )

    response.raise_for_status()


def main():

    print("Starting monitor...")

    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing")
        return

    if not CHAT_ID:
        print("ERROR: CHAT_ID missing")
        return


    posts = get_new_posts()

    if not posts:
        print("No new announcements")
        return


    for title, link in posts:
        print("Sending:", title)
        send_telegram(title, link)


    # حفظ آخر إعلان
    save_last(posts[-1][1])

    print(f"Sent {len(posts)} announcement(s)")


if __name__ == "__main__":
    main()
