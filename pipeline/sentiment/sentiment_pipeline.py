from pipeline.sentiment.finbert import get_sentiment, split_text, aggregate_sentiment


def analyze_answer(answer):
    chunks = split_text(answer)
    results = [get_sentiment(chunk) for chunk in chunks]
    return aggregate_sentiment(results)


def add_sentiment_to_qa(qa_pairs):
    enriched = []

    for qa in qa_pairs:
        sentiment = analyze_answer(qa["answer"])
        qa["sentiment"] = sentiment
        enriched.append(qa)

    return enriched