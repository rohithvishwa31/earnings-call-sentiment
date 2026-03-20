from pipeline.scraping.scrape_motley import fetch_transcript, fetch_exec_names
from pipeline.preprocessing.structure import structure_transcript
from pipeline.preprocessing.section import label_transcript_sections
from pipeline.qa.qa_builder import build_qa_pairs
import json

def main():
    url = "https://www.fool.com/earnings/call-transcripts/2026/01/29/apple-aapl-q1-2026-earnings-call-transcript/"
    transcript = fetch_transcript(url)
    exec_names = fetch_exec_names(url)

    structured = structure_transcript(transcript)

    section_labeled = label_transcript_sections(structured, exec_names)

    qa_pairs = build_qa_pairs(section_labeled)

    print(json.dumps(qa_pairs, indent=2))

if __name__ == "__main__":
    main()