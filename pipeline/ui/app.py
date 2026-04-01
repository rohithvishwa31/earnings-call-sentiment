import html
import json
import re

import streamlit as st

from pipeline.sentiment.sentiment_pipeline import analyze_with_rag, get_sentiment_cached

st.set_page_config(page_title="FinSense Analytics", layout="wide")


def normalize_label(label, score):
    if isinstance(label, str) and label.strip():
        raw = label.strip().lower()
        if raw in {"positive", "negative", "neutral"}:
            return raw.title()
    if score > 0.05:
        return "Positive"
    if score < -0.05:
        return "Negative"
    return "Neutral"


def extract_drivers_and_risks(result):
    drivers = result.get("drivers", []) or result.get("positive_signals", []) or []
    risks = result.get("risks", []) or result.get("negative_signals", []) or []

    if not drivers and not risks:
        signals = result.get("signals", {})
        if isinstance(signals, dict):
            drivers = signals.get("positive", []) or []
            risks = signals.get("negative", []) or []

    # Deduplicate while preserving first-seen order
    drivers = list(dict.fromkeys([str(x).strip() for x in drivers if str(x).strip()]))
    risks = list(dict.fromkeys([str(x).strip() for x in risks if str(x).strip()]))
    return drivers, risks


def classify_polarity(text_chunk):
    try:
        sentiment = get_sentiment_cached(text_chunk)
        polarity = sentiment.get("positive", 0) - sentiment.get("negative", 0)
    except Exception:
        polarity = 0

    if polarity > 0.05:
        return "positive", "rgba(22, 163, 74, 0.28)"
    if polarity < -0.05:
        return "negative", "rgba(220, 38, 38, 0.28)"
    return "neutral", "rgba(234, 179, 8, 0.24)"


def build_whitespace_flexible_regex(text):
    tokens = re.findall(r"\S+", text.strip())
    if not tokens:
        return None
    return r"\s+".join(re.escape(t) for t in tokens)


def highlight_evidence_in_text(full_text, evidences):
    escaped_text = html.escape(full_text or "")
    if not escaped_text:
        return ""

    sorted_evidences = sorted(
        [e for e in evidences if isinstance(e, str) and e.strip()],
        key=len,
        reverse=True,
    )

    highlighted_text = escaped_text
    for ev in sorted_evidences:
        pattern = build_whitespace_flexible_regex(html.escape(ev))
        if not pattern:
            continue

        polarity, color = classify_polarity(ev)
        badge = "POS" if polarity == "positive" else "NEG" if polarity == "negative" else "NEU"
        replacement = (
            f'<mark style="background:{color}; padding:2px 3px; border-radius:4px;">'
            f"\\g<0>"
            f'</mark><span style="font-size:11px; margin-left:4px; color:var(--text-color); opacity:0.75;">{badge}</span>'
        )
        highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)

    return highlighted_text


def parse_batch_payload(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("qa_pairs", "qa", "items", "data", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("Unsupported JSON shape. Expected a list or a dict containing list data.")


def normalize_qa_item(item):
    if not isinstance(item, dict):
        return None

    answer = item.get("answer") or item.get("response") or item.get("text") or ""
    question = item.get("question") or item.get("prompt") or "Question"

    if not isinstance(answer, str) or not answer.strip():
        return None

    return {
        "question": str(question),
        "answer": answer.strip(),
        "analyst": item.get("analyst"),
        "executives": item.get("executives", []),
    }


def render_scorecard(result):
    raw_score = result.get("score", 0.0)
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        score = 0.0

    label = normalize_label(result.get("label", ""), score)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Label", label)
    with c2:
        st.metric("Score", f"{score:.2f}")


def render_analysis_results(result, raw_text):
    evidences = (result.get("evidence", []) or [])[:3]
    drivers, risks = extract_drivers_and_risks(result)
    top = st.columns([1, 2])

    with top[0]:
        st.subheader("Executive Scorecard")
        render_scorecard(result)
        st.markdown("---")

        st.subheader("Extracted Signals")
        d_col, r_col = st.columns(2)
        with d_col:
            st.caption("Drivers")
            if drivers:
                for driver in drivers:
                    st.markdown(f"- `{driver}`")
            else:
                st.write("No driver signals.")
        with r_col:
            st.caption("Risks")
            if risks:
                for risk in risks:
                    st.markdown(f"- `{risk}`")
            else:
                st.write("No risk signals.")

        st.markdown("---")
        st.subheader("RAG Evidence Chunks (Top 3)")
        if evidences:
            for idx, ev in enumerate(evidences, start=1):
                _, color = classify_polarity(ev)
                st.markdown(
                    f'<div style="border-left:4px solid {color}; padding:8px 10px; margin-bottom:8px; '
                    f'border-radius:6px; background:var(--secondary-background-color); color:var(--text-color); '
                    f'border:1px solid color-mix(in srgb, var(--text-color) 12%, transparent);">'
                    f'{idx}. {html.escape(ev)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No evidence chunks returned by the retriever.")

    with top[1]:
        st.subheader("Contextual Heatmap")
        st.caption("Green = positive polarity evidence, Red = negative polarity evidence.")
        highlighted = highlight_evidence_in_text(raw_text, evidences)
        st.markdown(
            (
                '<div style="line-height:1.8; font-size:15px; padding:16px; '
                'border:1px solid color-mix(in srgb, var(--text-color) 16%, transparent); '
                'border-radius:10px; background:var(--background-color); color:var(--text-color); '
                'white-space:pre-wrap;">'
                f"{highlighted}</div>"
            ),
            unsafe_allow_html=True,
        )


st.title("Financial Sentiment & RAG Workbench")
st.caption("Dual mode analysis: sandbox testing and production batch processing.")

tab1, tab2 = st.tabs(["Sandbox (Manual Input)", "Batch Processing (JSON Upload)"])

with tab1:
    st.write("Paste tricky phrases or full answers to debug edge cases in real time.")
    user_input = st.text_area(
        "Earnings Call Answer",
        height=180,
        placeholder="Example: margin pressure offset by massive cloud growth",
    )

    if st.button("Analyze Sandbox Input", use_container_width=True):
        if not user_input.strip():
            st.warning("Please enter text before running analysis.")
        else:
            with st.spinner("Running sentiment + RAG analysis..."):
                analysis = analyze_with_rag(user_input.strip())
            render_analysis_results(analysis, user_input)

with tab2:
    st.write("Upload scraped Q&A JSON and process every answer at scale.")
    uploaded_file = st.file_uploader("Upload JSON", type=["json"])

    if uploaded_file:
        try:
            payload = json.load(uploaded_file)
            raw_items = parse_batch_payload(payload)
            qa_items = [normalize_qa_item(item) for item in raw_items]
            qa_items = [item for item in qa_items if item is not None]

            if not qa_items:
                st.warning("No valid records found. Each record needs at least an `answer` field.")
            else:
                st.success(f"Loaded {len(qa_items)} analyzable Q&A records.")
                with st.spinner("Processing batch answers with the pipeline..."):
                    for i, qa in enumerate(qa_items):
                        qa["sentiment"] = analyze_with_rag(qa["answer"])

                for i, qa in enumerate(qa_items):
                    q_title = qa.get("question", "Question")
                    with st.expander(f"{i + 1}. {q_title}", expanded=(i == 0)):
                        analyst = qa.get("analyst")
                        executives = qa.get("executives", [])
                        if analyst:
                            st.caption(f"Analyst: {analyst}")
                        if executives:
                            st.caption(f"Executives: {', '.join(executives)}")
                        render_analysis_results(qa["sentiment"], qa["answer"])
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON document.")
        except Exception as exc:
            st.error(f"Batch processing failed: {exc}")