import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import random

# === Gemini Pro Setup ===
genai.configure(api_key="AIzaSyBE_5y5i6xM5gQb7AOCB8eWJ9jVH3GzUIY")
model = genai.GenerativeModel("gemini-1.5-pro")

# === Streamlit Config ===
st.set_page_config(page_title="Syllabus Helper", layout="centered")
st.sidebar.title("\U0001F4C2 Menu")
page = st.sidebar.selectbox("Choose a page", ["\U0001F4DA Analyzer", "\U0001F9EA Quiz Generator"])

correct_reactions = [
    "https://media.tenor.com/Vz2_0thQ9jIAAAAC/thumbs-up-cartoon.gif",
    "https://media.tenor.com/nWvIvNi3VdYAAAAC/minions-thumbs-up.gif",
    "https://media.tenor.com/4k_buGx-lcoAAAAC/emoji-thumbs-up.gif",
    "https://media.tenor.com/7nnIDHUJSU4AAAAC/nodding-thumbs-up.gif"
]
incorrect_reactions = [
    "https://media.tenor.com/2roX3uxz_68AAAAM/milk-meme.gif",
    "https://media.tenor.com/fL4jWHY7L2gAAAAC/you-fail-fail.gif",
    "https://media.tenor.com/tVLI4B5du3gAAAAC/wrong-incorrect.gif",
    "https://media.tenor.com/I-I-1cqqJ6YAAAAC/uh-oh-sad.gif"
]

def chunk_text(text, max_words=1000):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def run_gemini(prompt):
    return model.generate_content(prompt).text

# === Analyzer ===
if page == "\U0001F4DA Analyzer":
    st.title("\U0001F4DA Syllabus Helper for Students")
    subject = st.selectbox("Select Subject", [
        "\U0001F4D8 English", "\U0001F4D0 Maths", "\U0001F9B2 Physics", "\U0001F9EC Biology",
        "\u2697\ufe0f Chemistry", "\U0001F4D9 Bahasa Melayu", "\U0001F238 Chinese", "\U0001F524 Tamil"
    ])

    input_type = st.radio("Choose input type:", ("\U0001F4C4 PDF", "🌐 URL", "📝 Text"))
    content = None

    if input_type == "\U0001F4C4 PDF":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf_file:
            with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                content = "\n".join([doc[i].get_text() for i in range(min(10, len(doc)))])
    elif input_type == "🌐 URL":
        url = st.text_input("Enter URL")
        if url:
            try:
                html = requests.get(url).text
                soup = BeautifulSoup(html, "html.parser")
                content = soup.get_text(separator=' ')
            except Exception as e:
                st.error(f"Failed to fetch URL: {e}")
    else:
        content = st.text_area("Paste or write your content")

    if content and st.button("\U0001F9E0 Process"):
        with st.spinner("Processing..."):
            chunks = chunk_text(content)
            result = ""

            if subject == "\U0001F4D8 English":
                summary = "\n\n".join([run_gemini(f"Summarize and simplify this English content for students:\n\n{chunk}") for chunk in chunks])
                st.subheader("\U0001F4DD Summary")
                st.write(summary)

                if st.checkbox("✍️ Show Essay Improvement Tips"):
                    tips = run_gemini(f"Give improvement tips for this essay:\n\n{content}")
                    st.subheader("💡 Essay Tips")
                    st.write(tips)
            elif subject in ["\U0001F4D0 Maths", "\U0001F9B2 Physics"]:
                solutions = "\n\n".join([run_gemini(f"Solve and explain step-by-step:\n\n{chunk}") for chunk in chunks])
                st.subheader("\U0001F9EE Solution")
                st.write(solutions)
            elif subject in ["\U0001F9EC Biology", "\u2697\ufe0f Chemistry"]:
                notes = "\n\n".join([run_gemini(f"Convert this science text to simple bullet notes:\n\n{chunk}") for chunk in chunks])
                st.subheader("\U0001F4CC Notes")
                st.write(notes)
            else:
                explanation = run_gemini(f"Translate and explain the following:\n\n{content}")
                st.subheader("🌐 Translated & Explained")
                st.write(explanation)

# === Quiz Generator ===
elif page == "\U0001F9EA Quiz Generator":
    st.title("\U0001F9EA Quiz Generator")
    quiz_input = st.text_area("Enter topic or notes")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = []
    if 'answers_submitted' not in st.session_state:
        st.session_state.answers_submitted = False

    if st.button("🎯 Generate Quiz"):
        st.session_state.answers_submitted = False
        prompt = f"""
Create a 10-question multiple choice quiz from the following notes:
- Each question must have 4 options.
- Mark the correct one with an asterisk (*)
- Include a short explanation for the correct answer.
- Difficulty: {difficulty}

Content:
{quiz_input}
"""
        quiz_raw = run_gemini(prompt)
        questions = []

        for block in quiz_raw.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 5:
                question = lines[0]
                options = [line.replace("*", "").strip() for line in lines[1:5]]
                correct = [line for line in lines[1:5] if "*" in line][0].replace("*", "").strip()
                explanation = lines[5] if len(lines) > 5 else ""
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": correct,
                    "explanation": explanation
                })
        st.session_state.quiz_data = questions

    if st.session_state.quiz_data:
        st.subheader("📝 Quiz Time")
        for i, q in enumerate(st.session_state.quiz_data):
            st.radio(f"{i+1}. {q['question']}", q['options'], key=f"user_answer_{i}")

        if st.button("✅ Submit Answers") and not st.session_state.answers_submitted:
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                user_ans = st.session_state.get(f"user_answer_{i}")
                correct = q['answer']
                exp = q.get("explanation", "")
                col1, col2 = st.columns([3, 1])
                if user_ans == correct:
                    with col1:
                        st.success(f"Q{i+1}: Correct! 🎉")
                        st.info(f"Explanation: {exp}")
                    with col2:
                        st.image(random.choice(correct_reactions), width=100)
                    score += 1
                else:
                    with col1:
                        st.error(f"Q{i+1}: Incorrect. Correct answer: {correct}")
                        st.info(f"Explanation: {exp}")
                    with col2:
                        st.image(random.choice(incorrect_reactions), width=100)
            st.session_state.answers_submitted = True
            st.markdown(f"### 🏆 Your Score: {score} / 10")

