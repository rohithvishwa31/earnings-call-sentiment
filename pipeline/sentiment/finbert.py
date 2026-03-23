from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "ProsusAI/finbert"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)


def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

    labels = ["negative", "neutral", "positive"]

    return {
        "label": labels[torch.argmax(probs)],
        "confidence": float(torch.max(probs))
    }

def split_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def aggregate_sentiment(results):
    score_map = {"positive": 1, "neutral": 0, "negative": -1}

    total = 0
    for r in results:
        total += score_map[r["label"]] * r["confidence"]

    avg = total / len(results)

    if avg > 0.2:
        label = "positive"
    elif avg < -0.2:
        label = "negative"
    else:
        label = "neutral"

    return {"label": label, "score": round(avg, 4)}