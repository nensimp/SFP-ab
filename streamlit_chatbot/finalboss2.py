import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

# Configure Gemini
genai.configure(api_key="AIzaSyBBs0JdeM_30o3xLOzM9LgqliHpWHarpFQ")
model = genai.GenerativeModel("gemini-1.5-flash")

# App setup
st.set_page_config(page_title="Syllabus Helper", layout="centered")
st.sidebar.title("📂 Menu")
page = st.sidebar.selectbox("Choose a page", ["📚 Analyzer", "🧪 Quiz Generator"])

# --- Helper Functions (Used by Both Pages) ---
def chunk_text(text, max_words=1000):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def run_gemini(prompt):
    return model.generate_content(prompt).text

# === PAGE 1: Syllabus Analyzer ===
if page == "📚 Analyzer":
    st.title("📚 Syllabus Helper for Students")
    st.write("Choose your subject to get started.")

    subject = st.selectbox("Select Subject", [
        "📘 English", "📐 Maths", "🧲 Physics", "🧬 Biology",
        "⚗️ Chemistry", "📙 Bahasa Melayu", "🈶 Chinese", "🔤 Tamil"
    ])

    input_type = st.radio("Choose input type:", ("📄 PDF", "🌐 URL", "📝 Text"))
    content = None

    if input_type == "📄 PDF":
        pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if pdf_file is not None:
            if pdf_file.size > 20 * 1024 * 1024:
                st.warning("⚠️ PDF is too large. Please upload one under 20MB.")
            else:
                with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                    MAX_PAGES = 10
                    content = "\n".join([doc[i].get_text() for i in range(min(len(doc), MAX_PAGES))])

    elif input_type == "🌐 URL":
        url = st.text_input("Paste a URL")
        if url:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                content = soup.get_text(separator=' ').strip()
            except Exception as e:
                st.error(f"Error fetching URL: {e}")

    elif input_type == "📝 Text":
        content = st.text_area("Paste or type your text here")

    # Analyzer logic
    if content:
        def summarize_text(text):
            chunks = chunk_text(text)
            return "\n\n".join([run_gemini(f"Summarize and simplify for students:\n\n{chunk}") for chunk in chunks])

        def give_essay_tips(text):
            return run_gemini(f"Give tips to improve this English essay:\n\n{text}")

        def solve_math_or_physics(text):
            chunks = chunk_text(text)
            return "\n\n".join([run_gemini(f"Solve with formulas, steps, and answer:\n\n{chunk}") for chunk in chunks])

        def make_easy_notes(text):
            chunks = chunk_text(text)
            return "\n\n".join([run_gemini(f"Simplify this science content into bullet points:\n\n{chunk}") for chunk in chunks])

        def translate_and_explain(text):
            return run_gemini(f"Translate and explain this academic text:\n\n{text}")

        if st.button("🧠 Process"):
            with st.spinner("Thinking..."):
                result = ""

                if subject == "📘 English":
                    result = summarize_text(content)
                    st.subheader("📝 Summary")
                    st.write(result)

                    if st.checkbox("✍️ Show Essay Improvement Tips"):
                        tips = give_essay_tips(content)
                        st.subheader("💡 Essay Tips")
                        st.write(tips)

                elif subject in ["📐 Maths", "🧲 Physics"]:
                    result = solve_math_or_physics(content)
                    st.subheader("🧮 Solution")
                    st.write(result)

                elif subject in ["🧬 Biology", "⚗️ Chemistry"]:
                    result = make_easy_notes(content)
                    st.subheader("📌 Notes")
                    st.write(result)

                elif subject in ["📙 Bahasa Melayu", "🈶 Chinese", "🔤 Tamil"]:
                    result = translate_and_explain(content)
                    st.subheader("🌐 Translated & Explained")
                    st.write(result)

            st.download_button("📥 Download as .txt", result, "result.txt", "text/plain")

# === PAGE 2: Quiz Generator ===
elif page == "🧪 Quiz Generator":
    st.title("🧪 Quiz Generator")
    st.write("Paste any topic or notes, and I’ll generate a quiz for you!")

    quiz_input = st.text_area("Enter your topic, notes, or content here")

    if st.button("🎯 Generate Quiz"):
        with st.spinner("Creating quiz..."):
            prompt = f"""
You are a helpful quiz maker for students. Based on the following content, create a short quiz:
- Include 3–5 multiple choice questions
- Include 4 answer options per question
- Mark the correct answer with an asterisk (*)

Content:
{quiz_input}
"""
            quiz = run_gemini(prompt)
            st.subheader("📝 Your Quiz")
            st.text(quiz)

        st.download_button("📥 Download Quiz", quiz, "quiz.txt", "text/plain")

