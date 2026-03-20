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


