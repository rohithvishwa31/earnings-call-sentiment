import spacy
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "ProsusAI/finbert"
#MODEL_NAME = "D:/projects/Earnings-call-sentiment/earnings-call-sentiment/training/finbert-tuned-final"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("sentencizer")


def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

    labels = ["positive", "negative", "neutral"]

    prob_dict = {label: float(probs[i]) for i, label in enumerate(labels)}

    return prob_dict

def split_into_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]