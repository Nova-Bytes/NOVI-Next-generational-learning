import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Python projects/NOVI/backend/ai_functions.py"), "..")))
from pathlib import Path
import streamlit as st
from backend import ai_functions  # Make sure this path is correct


# ----- Page Config -----
st.set_page_config(
    page_title="NOVI — Smart Study Assistant",
    layout="wide",
    page_icon="📘"
)

# ----- Minimalist Theme Colors -----
PRIMARY_COLOR = "#4ADE80"        # soft green accent
SECONDARY_COLOR = "#60A5FA"      # soft blue accent
BACKGROUND_COLOR = "#0F1117"     # deep dark
CARD_BACKGROUND_COLOR = "#1A1C23" # slightly lighter dark
TEXT_COLOR = "#E5E7EB"           # soft white
FONT = "Inter"

ASSETS_PATH = Path("C:/Python projects/NOVI").resolve()

# ----- Custom CSS for Minimalist Look -----
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}&display=swap" rel="stylesheet">
<style>
html, body, .stApp {{
    background-color: {BACKGROUND_COLOR};
    color: {TEXT_COLOR};
    font-family: '{FONT}', sans-serif;
}}
h1, h2, h3, h4 {{
    color: {PRIMARY_COLOR};
    font-weight: 500;
}}
p, li {{
    color: {TEXT_COLOR}CC;
    line-height: 1.6;
}}
.stButton>button {{
    background-color: {PRIMARY_COLOR};
    color: {BACKGROUND_COLOR};
    border-radius: 12px;
    padding: 0.5em 1.2em;
    font-weight: 500;
    transition: 0.2s;
}}
.stButton>button:hover {{
    background-color: {SECONDARY_COLOR};
    color: {TEXT_COLOR};
}}
.stTextInput input, .stTextArea textarea {{
    background-color: {CARD_BACKGROUND_COLOR};
    color: {TEXT_COLOR};
    border-radius: 12px;
    padding: 0.6em;
    border: 1px solid {PRIMARY_COLOR}30;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {PRIMARY_COLOR};
    box-shadow: 0 0 5px {PRIMARY_COLOR}40;
}}
.card {{
    background: {CARD_BACKGROUND_COLOR};
    padding: 1.5em;
    border-radius: 15px;
    margin-bottom: 1.5em;
    transition: transform 0.2s ease;
}}
.card:hover {{
    transform: translateY(-2px);
}}
.stFileUploader>div>button {{
    background-color: transparent;
    color: {PRIMARY_COLOR};
    border: 2px dashed {PRIMARY_COLOR}40;
    border-radius: 12px;
    padding: 0.7em 1.5em;
}}
.stFileUploader>div>button:hover {{
    background-color: {PRIMARY_COLOR}10;
}}
</style>
""", unsafe_allow_html=True)

# ----- Header -----
col1, col2 = st.columns([1, 5])
with col1:
    logo_path = ASSETS_PATH / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=70)
with col2:
    st.markdown(f"<h1>NOVI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{PRIMARY_COLOR}; margin-top:-0.5em;'>Smart Study Assistant</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_COLOR}80;'>Organize • Summarize • Revise — AI-powered study helper</p>", unsafe_allow_html=True)
st.markdown("---")

# ----- Session State -----
for key, default in {
    "text": "",
    "summary": "",
    "quiz_data": [],
    "quiz_index": 0,
    "score": 0,
    "show_result": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----- Tabs -----
tab1, tab2, tab3 = st.tabs(["📖 Revision", "📝 Quiz", "🎯 Focus Mode"])

# ----- Revision Tab -----
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Upload Study Material</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Extracting text..."):
            st.session_state.text = ai_functions.extract_text_from_file(uploaded_file)
        st.success("Text extracted successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.text:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>Document Preview</h4>", unsafe_allow_html=True)
        st.markdown(f"<div style='max-height:300px; overflow-y:auto; white-space:pre-wrap;'>{st.session_state.text[:4000]}{'...' if len(st.session_state.text)>4000 else ''}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.text and st.button("Generate Summary"):
        with st.spinner("Summarizing..."):
            st.session_state.summary = ai_functions.summarize_text(st.session_state.text)
        st.success("Summary ready!")

    if st.session_state.summary:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>Summary</h4>", unsafe_allow_html=True)
        st.text_area(" ", st.session_state.summary, height=300, key="summary_output")
        st.download_button("Download Summary", data=st.session_state.summary, file_name="novi_summary.txt")
        st.markdown("</div>", unsafe_allow_html=True)

# ----- Quiz Tab -----
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Auto-generated Quiz</h3>", unsafe_allow_html=True)
    if not st.session_state.text:
        st.info("Upload a document first.")
    else:
        if not st.session_state.quiz_data:
            with st.spinner("Generating quiz..."):
                st.session_state.quiz_data = ai_functions.generate_quiz_from_text(st.session_state.text, n=3)

        if st.session_state.quiz_data and not st.session_state.show_result:
            quiz = st.session_state.quiz_data[st.session_state.quiz_index]
            st.markdown(f"<p><strong>Q{st.session_state.quiz_index + 1}:</strong> {quiz['question']}</p>", unsafe_allow_html=True)
            answer = st.text_input("Your Answer:", key=f"quiz_input_{st.session_state.quiz_index}")
            if st.button("Submit Answer", key=f"submit_button_{st.session_state.quiz_index}"):
                if answer.strip().lower() in quiz['answer'].lower():
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Wrong! Correct: {quiz['answer']}")
                st.session_state.quiz_index += 1
                if st.session_state.quiz_index >= len(st.session_state.quiz_data):
                    st.session_state.show_result = True
                st.experimental_rerun()
        elif st.session_state.show_result:
            st.markdown(f"<h3>Quiz Completed!</h3><p>Score: {st.session_state.score}/{len(st.session_state.quiz_data)}</p>", unsafe_allow_html=True)
            if st.button("Try Again"):
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.show_result = False
                st.session_state.quiz_data = []
                st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Focus Mode Tab -----
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Focus Sections</h3>", unsafe_allow_html=True)
    if not st.session_state.text:
        st.info("Upload a document first.")
    else:
        if st.button("Show Focus Sections"):
            with st.spinner("Analyzing text..."):
                sections = ai_functions.suggest_focus_sections(st.session_state.text, n=5)
            if sections:
                for i, s in enumerate(sections, 1):
                    st.markdown(f"<p><strong>{i}.</strong> {s}</p>", unsafe_allow_html=True)
            else:
                st.warning("No focus sections found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Footer -----
st.markdown("---")
st.markdown(f"<p style='text-align:center; color:{TEXT_COLOR}80;'>Built at DevJams'25 — <span style='color:{PRIMARY_COLOR}'>NOVI Team</span></p>", unsafe_allow_html=True)
