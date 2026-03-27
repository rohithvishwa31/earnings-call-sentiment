from pipeline.scraping.scrape_motley import fetch_transcript, fetch_exec_names
from pipeline.preprocessing.structure import structure_transcript
from pipeline.preprocessing.section import label_transcript_sections
from pipeline.qa.qa_builder import build_qa_pairs
from pipeline.sentiment.sentiment_pipeline import add_sentiment_to_qa
from pipeline.sentiment.lm_dictionary import load_lm_dictionary
import json

def main():
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    
    load_lm_dictionary("data/Loughran-McDonald_MasterDictionary_1993-2024.csv") 

    transcript = fetch_transcript(url)
    exec_names = fetch_exec_names(url)

    structured = structure_transcript(transcript)

    section_labeled = label_transcript_sections(structured, exec_names)

    qa_pairs = build_qa_pairs(section_labeled)

    qa_with_sentiment = add_sentiment_to_qa(qa_pairs)

    print(json.dumps(qa_with_sentiment, indent=2))

if __name__ == "__main__":
    main()