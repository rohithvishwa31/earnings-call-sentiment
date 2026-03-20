from pipeline.preprocessing.speaker import get_speaker_type

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

