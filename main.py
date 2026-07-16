import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://faculty.univ-eloued.dz"
URL = "https://faculty.univ-eloued.dz/faculty/fll"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_FILE = "last_post.txt"


def get_latest_post():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/post/" in href:

            title = a.get_text(" ", strip=True)

            if not title:
                continue

            link = urljoin(BASE_URL, href)

            return title, link

    return None, None


def get_post_content(link):

    r = requests.get(
        link,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text("\n", strip=True)

    images = []

    for img in soup.find_all("img", src=True):

        src = urljoin(BASE_URL, img["src"])
        images.append(src)

    files = []

    for a in soup.find_all("a", href=True):

        href = urljoin(BASE_URL, a["href"])

        if any(x in href.lower() for x in [".pdf", ".doc", ".docx"]):
            files.append(href)

    return text, images, files


def read_last():

    if not os.path.exists(LAST_FILE):
        return ""

    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last(link):

    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(link)


def send_message(text):

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def send_photo(photo):

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "photo": photo
        }
    )


def send_file(file):

    data = {
        "chat_id": CHAT_ID
    }

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        data=data,
        files={
            "document": requests.get(file).content
        }
    )


def main():

    title, link = get_latest_post()

    if not link:
        print("No announcement")
        return

    last = read_last()

    if link == last:
        print("No new announcement")
        return


    content, images, files = get_post_content(link)


    message = f"""
📢 إعلان جديد

{title}

{content}

🔗 الرابط:
{link}
"""


    send_message(message)


    for img in images:
        send_photo(img)


    for file in files:
        send_file(file)


    save_last(link)

    print("Announcement sent")


if __name__ == "__main__":
    main()
