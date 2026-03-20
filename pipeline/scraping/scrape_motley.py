import re
import requests
from bs4 import BeautifulSoup


def extract_name(text):
    match = re.search(r"[—-]\s*(.+)", text)
    return match.group(1).strip() if match else text

def fetch_exec_names(url):
    headers = {
        "user-agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("div", id="article-body-transcript")

    if not article:
        print("Article not found!")
        return []

    heading = article.find("h2", id="call-participants")

    if not heading:
        print("Call Participants section not found!")
        return []

    ul = heading.find_next("ul")

    exec_names = []

    if ul:
        items = ul.find_all("li")
        for item in items:
            name = item.get_text().strip()
            if name:
                exec_names.append(extract_name(name).lower())

    return exec_names

def fetch_transcript(url):

    headers = {
        "user-agent" : "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("div", id="article-body-transcript")

    if not article:
        print("Article not found!")
        return ""
    
    paragraphs = article.find_all("p")

    text = []

    for p in paragraphs:
        line = p.get_text().strip()
        if line:
            text.append(line)
    
    return text

