# 📊 Earnings Call Sentiment Analysis (FinBERT + RAG)

## 🚀 Overview

This project builds a **financial sentiment analysis pipeline** using earnings call transcripts (scraped from Motley Fool).
It processes raw transcripts into structured data, separates **Prepared Remarks vs Q&A**, and enables **fine-grained sentiment analysis** using FinBERT.

The system is designed with **RAG (Retrieval-Augmented Generation)** in mind, enabling intelligent querying over earnings calls.

---

## 🎯 Objectives

* Scrape earnings call transcripts
* Structure raw text into speaker-level data
* Identify **Prepared vs Q&A sections**
* Classify **speaker types (executive, analyst, operator)**
* Build **Analyst → Executive QA pairs**
* Perform **financial sentiment analysis (FinBERT)**
* Enable **RAG-based querying over transcripts**

---

## 🏗️ Pipeline Architecture

```text
Raw Transcript (Motley Fool)
        ↓
Text Cleaning & Parsing
        ↓
Structured Format (speaker, text)
        ↓
Section Labeling (Prepared / QA)
        ↓
Speaker Classification (exec / analyst / operator)
        ↓
QA Pair Construction
        ↓
Sentiment Analysis (FinBERT)
        ↓
RAG Indexing (vector DB)
```

---

## 📂 Project Structure

```bash
.
├── scrape_motley.py        # Scraping transcripts & participant names
├── parser.py               # structure_transcript()
├── section_labeler.py      # QA vs Prepared detection
├── speaker_classifier.py   # speaker_type logic
├── qa_builder.py           # QA pairing logic
├── sentiment.py            # FinBERT integration (planned)
├── rag_pipeline.py         # RAG system (planned)
├── main.py                 # Entry point
└── README.md
```

---

## 🧩 Data Format

### 🔹 Structured Transcript

```json
{
  "speaker": "Tim Cook",
  "text": "We had a strong quarter...",
  "section": "prepared",
  "speaker_type": "executive",
  "position": 12
}
```

---

### 🔹 QA Pair Format

```json
{
  "analyst": "Amit Daryanani",
  "question": "How should we think about margins?",
  "executives": ["Tim Cook"],
  "answer": "We expect margins to improve..."
}
```

---

## ⚙️ Key Components

### 1. Scraper

* Extracts transcript and participant names from Motley Fool

---

### 2. Transcript Structuring

* Converts raw text → structured speaker blocks
* Handles multi-line speech aggregation

---

### 3. Section Labeling

* Detects transition into Q&A using:

  * Phrase patterns (e.g., “let’s open for questions”)
  * Speaker changes
* Handles **no-QA transcripts**

---

### 4. Speaker Classification

* Uses participant list to classify:

  * `executive`
  * `analyst`
  * `operator`

---

### 5. QA Pairing

* Groups:

  * Analyst → Question
  * Executive(s) → Answer
* Merges multi-speaker responses

---

### 6. Sentiment Analysis (Planned)

* Uses **FinBERT** for financial sentiment
* Separate analysis for:

  * Prepared remarks
  * Executive responses

---

### 7. RAG System (Planned)

* Embedding + vector search
* Enables queries like:

  * “What concerns did analysts raise about revenue?”
  * “What did Apple say about supply chain?”

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/earnings-call-sentiment.git
cd earnings-call-sentiment

pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py
```

---

## 📌 Example Workflow

```python
url = "Motley Fool earnings call URL"

transcript = fetch_transcript(url)
exec_names = fetch_exec_names(url)

structured = structure_transcript(transcript)
labeled = label_transcript_sections(structured, exec_names)
qa_pairs = build_qa_pairs(labeled)
```

---

## ⚠️ Current Limitations

* Speaker classification may mislabel moderators as analysts
* Edge cases in transcripts (format inconsistencies)
* QA pairing assumes standard call structure

---

## 🔮 Future Improvements

* Improve speaker classification using ML/NLP
* Better handling of edge cases (no-QA, mixed speakers)
* Fine-tuned financial sentiment models
* Full RAG pipeline with vector database
* Dashboard for visualization

---

## 🧠 Tech Stack

* Python
* Regex / Text Processing
* FinBERT (HuggingFace)
* Vector DB (FAISS / Pinecone - planned)

---

## 💡 Key Insight

Earnings calls are not just text — they are **structured financial dialogues**:

* Prepared remarks → company narrative
* Q&A → analyst pressure & real insights

This project leverages that structure for **deeper financial analysis**.



* Motley Fool for transcript data
* FinBERT for financial sentiment modeling

---
