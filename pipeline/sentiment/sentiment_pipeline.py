from .finbert import get_sentiment, split_into_sentences
from .signals import extract_signals, detect_growth
from .weighting import get_weight, boost_strong_phrases, adjust_for_contrast
from .aggregation import aggregate_results
from .signals import extract_signals, compute_lm_score


def analyze_answer(answer):
    sentences = split_into_sentences(answer)
    windows = create_context_windows(sentences, window_size=2)

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

    score_map = {"positive": 1, "neutral": 0, "negative": -1}

    # 🔻 Reduce FinBERT dominance
    finbert_score = score_map[sentiment["label"]] * (sentiment["confidence"] - 0.5)

    # 🔻 LM Dictionary score
    signals = extract_signals(window)
    lm_score = compute_lm_score(signals)

    # 🔻 Combine scores (IMPORTANT WEIGHTS)
    score = (
        0.3 * finbert_score +   # context
        0.7 * lm_score          # lexical signal
    )

    # Optional boosts
    score = boost_strong_phrases(window, score)
    score = adjust_for_contrast(window, score)
    score *= detect_growth(window)

    weight = get_weight(window)

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