import scrape_motley
import preprocess
import json

def build_qa_pairs(data):
    qa_pairs = []
    current_question = None
    current_analyst = None
    current_answer = []
    current_execs = set()

    for chunk in data:
        if chunk["section"] != "qa":
            continue

        speaker_type = chunk["speaker_type"]
        speaker = chunk["speaker"]
        text = chunk["text"]

        # 🎯 Analyst → new question
        if speaker_type == "analyst":
            # Save previous QA pair
            if current_question and current_answer:
                qa_pairs.append({
                    "analyst": current_analyst,
                    "question": current_question,
                    "executives": list(current_execs),
                    "answer": " ".join(current_answer)
                })

            # Start new question
            current_question = text
            current_analyst = speaker
            current_answer = []
            current_execs = set()

        # 🎯 Executive → answer
        elif speaker_type == "executive":
            if current_question:
                current_answer.append(text)
                current_execs.add(speaker)

        # Ignore operator
        else:
            continue

    # Save last pair
    if current_question and current_answer:
        qa_pairs.append({
            "analyst": current_analyst,
            "question": current_question,
            "executives": list(current_execs),
            "answer": " ".join(current_answer)
        })

    return qa_pairs

if __name__ == "__main__":
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    transcript = scrape_motley.fetch_transcript(url)
    exec_names = scrape_motley.fetch_exec_names(url)

    structured = preprocess.structure_transcript(transcript)

    section_labeled = preprocess.label_transcript_sections(structured, exec_names)

    qa_pairs = build_qa_pairs(section_labeled)

    print(json.dumps(qa_pairs, indent=2))
