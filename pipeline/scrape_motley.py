import requests
from bs4 import BeautifulSoup

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
        print(line)
        if line:
            text.append(line)
    
    return text

if __name__ == "__main__":
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    transcript = fetch_transcript(url)

    with open("data/raw/sample.txt", "w", encoding="utf-8") as f:
        for line in transcript:
            f.write(line + "\n")