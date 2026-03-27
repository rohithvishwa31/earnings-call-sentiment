from .finbert import get_sentiment, split_into_sentences
from .signals import extract_signals, detect_growth
from .weighting import get_weight, boost_strong_phrases, adjust_for_contrast
from .aggregation import aggregate_results
from .signals import extract_signals, compute_lm_score


def analyze_answer(answer):
    sentences = split_into_sentences(answer)
    windows = create_context_windows(sentences, window_size=3)

    results = [analyze_window(w) for w in windows]

    return aggregate_results(results)


def create_context_windows(sentences, window_size=2):
    if len(sentences) < window_size:
        return sentences

    windows = []
    for i in range(len(sentences) - window_size + 1):
        window = " ".join(sentences[i:i+window_size])
        windows.append(window)

    return windows

def analyze_window(window):
    sentiment = get_sentiment(window)

    pos = sentiment["positive"]
    neg = sentiment["negative"]
    neu = sentiment["neutral"]

    polarity = pos - neg

    finbert_score = polarity * (1 - neu)

    signals = extract_signals(window)
    lm_score = compute_lm_score(signals)

    score = (
        0.7 * finbert_score +   
        0.0 * lm_score          
    )

    score = boost_strong_phrases(window, score)
    score = adjust_for_contrast(window, score)
    score *= detect_growth(window)

    score = max(min(score, 1.0), -1.0)

    weight = get_weight(window)

    print({
        "window": window[:80],
        "probs": {
            "pos": round(pos, 3),
            "neg": round(neg, 3),
            "neu": round(neu, 3)
        },
        "polarity": round(polarity, 3),
        "finbert": round(finbert_score, 3),
        "lm": round(lm_score, 3),
        "final": round(score, 3)
    })

    return {
        "score": score,
        "weight": weight,
        "signals": signals
    }

def add_sentiment_to_qa(qa_pairs):
    enriched = []

    for qa in qa_pairs:
        sentiment = analyze_answer(qa["answer"])
        qa["sentiment"] = sentiment
        enriched.append(qa)

    return enriched