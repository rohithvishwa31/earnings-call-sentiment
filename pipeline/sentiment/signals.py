from .lm_dictionary import LM_POSITIVE, LM_NEGATIVE


def extract_signals(sentence):
    words = sentence.lower().split()

    pos_hits = [w for w in words if w in LM_POSITIVE]
    neg_hits = [w for w in words if w in LM_NEGATIVE]

    # Phrase-level financial signals (VERY IMPORTANT)
    s = sentence.lower()

    strong_positive_phrases = [
        "all-time high", "all-time record", "best",
        "terrific quarter", "strong growth",
        "very happy", "great value", "opportunity",
        "strong product cycle", "beloved", "excited"
    ]

    strong_negative_phrases = [
        "declining margins", "supply constraint", "cost pressure",
        "difficult environment", "uncertain outlook"
    ]

    phrase_pos = [p for p in strong_positive_phrases if p in s]
    phrase_neg = [p for p in strong_negative_phrases if p in s]

    return {
        "positive": pos_hits + phrase_pos,
        "negative": neg_hits + phrase_neg,
        "neutral": []
    }


def compute_lm_score(signals):
    return len(signals["positive"]) - len(signals["negative"])


def detect_growth(sentence):
    s = sentence.lower()
    if "%" in sentence and any(word in s for word in ["up", "growth", "increase"]):
        return 1.5
    return 1.0