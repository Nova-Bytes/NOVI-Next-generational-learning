import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("C:/Python projects/NOVI/backend/ai_functions.py"), "..")))

import streamlit as st
from pathlib import Path
from backend import ai_functions

# ----- Page Config -----
st.set_page_config(page_title="NOVI — Smart Study Assistant", layout="wide", page_icon="📘")

# ----- Figma tokens (replace with your friend's values) -----
PRIMARY = "#4CAF50"
SECONDARY = "#1976D2"
BG = "#FFFFFF"
FONT = "Poppins"  # Google font

ASSETS = Path("C:/Python projects/NOVI/assets/logo.png").resolve().parent.parent / "assets"

# ----- Load font + CSS -----
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    body, .stApp {{ background-color: {BG}; font-family: '{FONT}', sans-serif; color: #111; }}
    h1 {{ color: {PRIMARY}; }}
    div.stButton > button {{ background-color: {PRIMARY}; color: white; border-radius: 8px; padding: 8px 14px; }}
    div.stButton > button:hover {{ background-color: {SECONDARY}; }}
    .card {{ background: white; padding: 16px; border-radius: 12px; box-shadow: 0 6px 18px rgba(20,20,20,0.06); }}
</style>
""", unsafe_allow_html=True)

# ----- Header -----
col1, col2 = st.columns([1, 5])
with col1:
    logo_path = ASSETS / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=100)
with col2:
    st.title("NOVI — Smart Study Assistant")
    st.markdown("Organize • Summarize • Revise — AI-powered study helper")

st.write("---")

# ----- Session State Init -----
if "text" not in st.session_state:
    st.session_state.text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# quiz-related state
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# ----- Tabs -----
tab1, tab2, tab3 = st.tabs(["📖 Revision", "📝 Quiz", "🎯 Focus Mode"])

# ---- Revision Tab ----
with tab1:
    st.subheader("Upload study material (PDF / DOCX / TXT)")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        with st.spinner("Extracting text..."):
            st.session_state.text = ai_functions.extract_text_from_file(uploaded_file)
        st.success("✅ Text extracted successfully!")

    if st.session_state.text:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("**Document Preview (first 4k chars)**")
        st.write(st.session_state.text[:4000] + ("..." if len(st.session_state.text) > 4000 else ""))
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Generate Summary"):
        with st.spinner("Summarizing..."):
            st.session_state.summary = ai_functions.summarize_text(st.session_state.text)
        st.success("✅ Summary ready!")

    if st.session_state.summary:
        st.text_area("Summary", st.session_state.summary, height=300)
        st.download_button("Download summary", data=st.session_state.summary, file_name="novi_summary.txt")

# ---- Quiz Tab ----
with tab2:
    st.subheader("Auto-generated Quiz")
    if not st.session_state.text:
        st.info("Upload a document in Revision tab first.")
    else:
        quiz_data = ai_functions.generate_quiz_from_text(st.session_state.text, n=3)

        if not st.session_state.show_result:
            if st.session_state.quiz_index < len(quiz_data):
                quiz = quiz_data[st.session_state.quiz_index]

                st.markdown(f"**Question {st.session_state.quiz_index + 1}:** {quiz['question']}")

                # For now: free-text answer input (since backend doesn't generate MCQs)
                choice = st.text_input("Your Answer:")

                if st.button("Submit Answer"):
                    if choice.strip().lower() in quiz['answer'].lower():
                        st.success("✅ Correct Answer")
                        st.session_state.score += 1
                    else:
                        st.error(f"❌ Wrong Answer\n\n**Correct Answer:** {quiz['answer']}")
                    st.session_state.quiz_index += 1

                    if st.session_state.quiz_index >= len(quiz_data):
                        st.session_state.show_result = True
                    st.rerun()
        else:
            st.subheader("🎉 Quiz Completed!")
            st.write(f"Your Score: {st.session_state.score} / {len(quiz_data)}")
            if st.button("Try Again"):
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.show_result = False
                st.experimental_rerun()

# ---- Focus Mode Tab ----
with tab3:
    st.subheader("Suggested Focus Sections")
    if not st.session_state.text:
        st.info("Upload a document in Revision tab first.")
    else:
        if st.button("Show Focus Sections"):
            sections = ai_functions.suggest_focus_sections(st.session_state.text, n=5)
            for i, s in enumerate(sections, 1):
                st.markdown(f"**{i}.** {s}")

st.write("---")
st.caption("Built at DevJams'25 — NOVI Team")
