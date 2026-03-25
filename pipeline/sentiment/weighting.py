def get_weight(sentence):
    weight = 1.0

    keywords = ["growth", "decline", "margin", "guidance", "forecast"]

    if any(k in sentence.lower() for k in keywords):
        weight += 0.5

    if any(char.isdigit() for char in sentence):
        weight += 0.5

    return weight


def boost_strong_phrases(sentence, score):
    strong_positive = [
        "all-time high",
        "all-time record",
        "best",
        "record",
        "could not be happier",
        "terrific quarter"
    ]

    if any(p in sentence.lower() for p in strong_positive):
        return score * 2

    return score


def adjust_for_contrast(sentence, score):
    if any(word in sentence.lower() for word in ["however", "but", "although"]):
        return score * 1.5
    return score