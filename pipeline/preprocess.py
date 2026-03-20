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

def is_qa_start(chunk, exec_names):
    speaker = chunk["speaker"].lower()
    text = chunk["text"].lower()

    # Signal 1: Explicit phrase (STRONGEST)
    if any(p in text for p in [
        "question-and-answer",
        "q&a session",
        "take questions",
        "first question"
    ]):
        return True

    # Signal 2: Operator signaling Q&A
    if speaker == "operator" and "question" in text:
        return True

    # Signal 3: Unknown speaker (your idea, but delayed)
    if speaker not in exec_names and speaker != "operator":
        return True

    return False

def get_speaker_type(speaker, exec_names):

    if speaker == "operator":
        return "operator"
    elif speaker in exec_names:
        return "executive"
    else:
        return "analyst"

def structure_transcript(lines):
    structured = []

    current_speaker = None
    current_text = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Match "Speaker: text"
        match = re.match(r"^([A-Za-z.\s]+):\s*(.*)", line)

        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()

            if not is_valid_speaker(speaker):
                continue

            # Save previous speaker block
            if current_speaker and current_text:
                structured.append({
                    "speaker": current_speaker.lower(),
                    "text": " ".join(current_text)
                })

            # Start new speaker
            current_speaker = speaker
            current_text = [text] if text else []

        else:
            # Continuation of previous speaker
            if current_speaker:
                current_text.append(line)

    # Save last speaker block
    if current_speaker and current_text:
        structured.append({
            "speaker": current_speaker.lower(),
            "text": " ".join(current_text)
        })

    return structured

def label_transcript_sections(transcript, exec_names):
    labeled_data = []
    in_qa = False

    for i, chunk in enumerate(transcript):
        if not in_qa and is_qa_start(chunk, exec_names):
            in_qa = True
        
        speaker = chunk["speaker"]
        text = chunk["text"]

        labeled_chunk = {
            "speaker": speaker,
            "text": text,
            "section": "qa" if in_qa else "prepared",
            "speaker_type": get_speaker_type(speaker, exec_names),
            "position": i
        }

        labeled_data.append(labeled_chunk)

    return labeled_data

if __name__ == "__main__":
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    transcript = scrape_motley.fetch_transcript(url)
    exec_names = scrape_motley.fetch_exec_names(url)

    structured = structure_transcript(transcript)

    section_labeled = label_transcript_sections(structured, exec_names)

    print(json.dumps(section_labeled, indent=2))