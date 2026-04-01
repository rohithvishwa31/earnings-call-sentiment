from rag.retrieve import Retriever
from .finbert import get_sentiment, split_into_sentences
from .signals import extract_signals, detect_growth
from .weighting import get_weight, boost_strong_phrases, adjust_for_contrast
from .aggregation import aggregate_results
from .signals import extract_signals, compute_lm_score

sentiment_cache = {}

def get_sentiment_cached(text):
    if text not in sentiment_cache:
        sentiment_cache[text] = get_sentiment(text)
    return sentiment_cache[text]


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

    # print({
    #     "window": window[:80],
    #     "probs": {
    #         "pos": round(pos, 3),
    #         "neg": round(neg, 3),
    #         "neu": round(neu, 3)
    #     },
    #     "polarity": round(polarity, 3),
    #     "finbert": round(finbert_score, 3),
    #     "lm": round(lm_score, 3),
    #     "final": round(score, 3)
    # })

    return {
        "score": score,
        "weight": weight,
        "signals": signals
    }

def add_sentiment_to_qa(qa_pairs):
    enriched = []

    for qa in qa_pairs:
        sentiment = analyze_with_rag(qa["answer"]) 
        qa["sentiment"] = sentiment
        enriched.append(qa)

    return enriched

def chunk_text(text, chunk_size=2, stride=3):
    sentences = split_into_sentences(text)

    if len(sentences) <= chunk_size:
        return [" ".join(sentences)]

    chunks = []
    for i in range(0, len(sentences), stride):
        chunk = " ".join(sentences[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks

def analyze_with_rag(answer):
    sentiment = analyze_answer(answer)

    chunks = chunk_text(answer)

    retriever = Retriever()
    retriever.fit(chunks)

    signals = extract_signals(answer)
    query = build_evidence_query(answer, sentiment, signals)

    candidates = retriever.query(query, top_k=6)

    candidates = deduplicate(candidates)

    def is_valid(text):
        bad_starts = ("thank", "hi", "yeah", "operator")
        return len(text.split()) > 6 and not text.lower().startswith(bad_starts)

    candidates = [c for c in candidates if is_valid(c)]

    if not candidates:
        sentiment["evidence"] = []
        return sentiment

    embedder = retriever.index.embedder

    query_vec = embedder.encode([query])[0]
    chunk_vecs = embedder.encode(candidates)

    similarities = chunk_vecs @ query_vec

    scored = list(zip(candidates, similarities))
    scored.sort(key=lambda x: x[1], reverse=True)

    evidence = [c for c, _ in scored[:3]]

    sentiment["evidence"] = evidence

    return sentiment

def deduplicate(texts):
    seen = set()
    unique = []

    for t in texts:
        key = t.strip().lower()
        if key not in seen:
            unique.append(t)
            seen.add(key)

    return unique

def build_evidence_query(answer, sentiment, signals):
    signal_terms = " ".join(signals.get("drivers", [])[:3])

    sentences = split_into_sentences(answer)

    seed = max(
        sentences,
        key=lambda s: abs(
            get_sentiment_cached(s)["positive"] -
            get_sentiment_cached(s)["negative"]
        ),
        default=answer[:120]
    )

    return f"{signal_terms} {seed}"

def score_chunk_alignment(chunk, target_label):
    s = get_sentiment_cached(chunk)
    polarity = s["positive"] - s["negative"]

    if target_label == "positive":
        return polarity
    elif target_label == "negative":
        return -polarity
    else:
        return (1 - abs(polarity)) - 0.5 * s["neutral"]