import re

def is_valid_speaker(speaker):
    blacklist = [
        "Image source",
        "Thursday",
        "Need a quote"
    ]

    return not any(speaker.startswith(x) for x in blacklist)


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