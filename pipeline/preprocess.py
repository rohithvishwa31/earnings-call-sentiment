import re
import scrape_motley
import json

def is_speaker_line(line):
    return bool(re.match(r"[A-Z][a-zA-Z.\s]+:", line)) or line.lower() in ["operator", "analyst"]

def is_valid_speaker(speaker):
    blacklist = [
        "Image source",
        "Thursday",
        "Need a quote"
    ]

    return not any(speaker.startswith(x) for x in blacklist)

def structure_transcript(lines):
    structured = []

    for line in lines:
        line = line.strip()

        match = re.match(r"^([A-Za-z.\s]+):\s*(.*)", line)

        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()

            if is_valid_speaker(speaker):
                structured.append({
                    "speaker": speaker,
                    "text": text
                })

    return structured

if __name__ == "__main__":
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    transcript = scrape_motley.fetch_transcript(url)

    structured = structure_transcript(transcript)

    print(json.dumps(structured, indent=2))