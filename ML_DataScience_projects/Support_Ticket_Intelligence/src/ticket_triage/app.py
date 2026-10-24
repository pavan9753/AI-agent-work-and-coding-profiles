import json

import pandas as pd
import streamlit as st

from ticket_triage.llm import generate_triage_note
from ticket_triage.model import TicketClassifier
from ticket_triage.settings import DATA_PATH, MAX_TICKET_CHARS, METRICS_PATH, get_settings


st.set_page_config(
    page_title="Support Ticket Intelligence",
    page_icon="✳",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #f5f6f3; }
      .block-container { max-width: 1120px; padding-top: 2.4rem; }
      [data-testid="stMetric"] { background: #fff; border: 1px solid #e4e7e1; padding: 1rem; border-radius: 12px; }
      .hero-note { padding: 1rem 1.15rem; border-left: 3px solid #56765e; background: #eaf0e9; border-radius: 4px; color: #3c5141; }
      .muted { color: #717970; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = get_settings()
st.title("Support Ticket Intelligence")
st.caption("A transparent text classifier with an optional LLM triage note for human review.")
st.markdown(
    '<div class="hero-note">Demo only. Use synthetic or non-sensitive text. The optional LLM action sends the ticket text to the OpenAI API.</div>',
    unsafe_allow_html=True,
)

try:
    examples = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Sample data was not found at {DATA_PATH}.")
    st.stop()

with st.sidebar:
    st.subheader("About this demo")
    st.metric("Ticket categories", int(examples["category"].nunique()))
    st.metric("Synthetic examples", int(len(examples)))
    st.caption("TF-IDF features → LogisticRegression → category probabilities")
    st.caption(f"LLM note: {'configured' if settings.has_openai_key else 'API key not set'}")
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        st.caption(f"Held-out macro F1: {float(metrics['macro_f1']):.2f}")

sample_option = st.selectbox(
    "Try a synthetic example",
    ["Write my own"] + examples["subject"].tolist(),
)
sample_message = ""
if sample_option != "Write my own":
    sample_message = str(examples.loc[examples["subject"] == sample_option, "message"].iloc[0])

ticket_text = st.text_area(
    "Ticket message",
    value=sample_message,
    height=150,
    max_chars=MAX_TICKET_CHARS,
    key=f"ticket_message_{sample_option}",
    placeholder="Describe the customer's issue in a few sentences...",
)

if st.button("Classify ticket", type="primary", use_container_width=True):
    try:
        classifier = TicketClassifier()
        prediction = classifier.predict(ticket_text)
        st.session_state["ticket_analysis"] = {
            "message": ticket_text,
            "prediction": prediction,
            "note": None,
        }
    except FileNotFoundError as error:
        st.error(str(error))
    except ValueError as error:
        st.warning(str(error))

analysis = st.session_state.get("ticket_analysis")
if analysis and analysis["message"] == ticket_text:
    prediction = analysis["prediction"]
    st.divider()
    left, right = st.columns([1, 1.1], gap="large")
    with left:
        st.subheader("Classifier result")
        st.metric("Predicted category", prediction.category.replace("_", " ").title())
        st.metric("Model confidence", f"{prediction.confidence:.1%}")
    with right:
        st.subheader("Ranked categories")
        chart = pd.DataFrame(
            {
                "category": [score.category.replace("_", " ").title() for score in prediction.ranked_categories],
                "probability": [score.probability for score in prediction.ranked_categories],
            }
        ).set_index("category")
        st.bar_chart(chart, horizontal=True, x_label="Probability", y_label="Category")

    st.subheader("Optional LLM analyst note")
    if not settings.has_openai_key:
        st.info("Add OPENAI_API_KEY to `.env` to enable this optional step. The classifier works without it.")
    if st.button("Generate LLM triage note", disabled=not settings.has_openai_key):
        try:
            with st.spinner("Drafting a note for human review..."):
                analysis["note"] = generate_triage_note(ticket_text, prediction)
                st.session_state["ticket_analysis"] = analysis
        except Exception as error:  # Show SDK/network errors without crashing the interface.
            st.error(f"LLM request failed: {error}")

    if analysis["note"]:
        st.markdown(analysis["note"])
        st.caption("Draft only. Review the evidence and follow your normal support process.")
