import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import random

# ====== Gemini API Setup ======
genai.configure(api_key="AIzaSyAktUcLRf6p1UVnF3Caq5bQXuArKHlqRJs")
model = genai.GenerativeModel("gemini-1.5-flash")

# ====== Streamlit Setup ======
st.set_page_config(page_title="Syllabus Helper", layout="centered")
st.sidebar.title("📂 Menu")
page = st.sidebar.selectbox("Choose a page", ["📖 Analyzer", "🧪 Quiz Generator"])

# ====== GIF Reactions ======
correct_gifs = [
    "https://media.tenor.com/Vz2_0thQ9jIAAAAC/thumbs-up-cartoon.gif",
    "https://media.tenor.com/7nnIDHUJSU4AAAAC/nodding-thumbs-up.gif"
]
incorrect_gifs = [
    "https://media.tenor.com/I-I-1cqqJ6YAAAAC/uh-oh-sad.gif",
    "https://media.tenor.com/tVLI4B5du3gAAAAC/wrong-incorrect.gif"
]

# ====== Helper Functions ======
def run_gemini(prompt):
    return model.generate_content(prompt).text

def chunk_text(text, max_words=1000):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# ====== Analyzer Page ======
if page == "📖 Analyzer":
    st.title("📖 Syllabus Analyzer")
    subject = st.selectbox("Select Subject", [
        "📘 English", "📐 Maths", "🧲 Physics", "🧬 Biology",
        "⚗️ Chemistry", "📙 Bahasa Melayu", "🈷️ Chinese", "🔣 Tamil"
    ])
    input_type = st.radio("Choose input type:", ("📄 PDF", "🌐 URL", "📝 Text"))
    content = None

    if input_type == "📄 PDF":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf_file:
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
        content = st.text_area("Paste or type your text")

    if content:
        def summarize_text(text):
            return "\n\n".join([run_gemini(f"Summarize and simplify for students:\n\n{chunk}") for chunk in chunk_text(text)])

        def give_essay_tips(text):
            return run_gemini(f"Give clear, practical tips to improve this English essay:\n\n{text}")

        def solve_math_or_physics(text):
            return "\n\n".join([run_gemini(f"Solve with formula, working steps and final answer:\n\n{chunk}") for chunk in chunk_text(text)])

        def make_easy_notes(text):
            return "\n\n".join([run_gemini(f"Convert the following science content into simple bullet-point notes:\n\n{chunk}") for chunk in chunk_text(text)])

        def translate_and_explain(text):
            return run_gemini(f"Translate and explain the following academic text:\n\n{text}")

        if st.button("🧠 Process"):
            with st.spinner("Thinking..."):
                result = ""
                if subject == "📘 English":
                    result = summarize_text(content)
                    st.subheader("📄 Summary")
                    st.write(result)
                    if st.checkbox("✍️ Show Essay Tips"):
                        tips = give_essay_tips(content)
                        st.subheader("💡 Essay Tips")
                        st.write(tips)
                elif subject in ["📐 Maths", "🧲 Physics"]:
                    result = solve_math_or_physics(content)
                    st.subheader("🧠 Solution")
                    st.write(result)
                elif subject in ["🧬 Biology", "⚗️ Chemistry"]:
                    result = make_easy_notes(content)
                    st.subheader("📝 Notes")
                    st.write(result)
                else:
                    result = translate_and_explain(content)
                    st.subheader("🌍 Translation")
                    st.write(result)
                st.download_button("⬇️ Download as .txt", result, "result.txt", "text/plain")

# ====== Quiz Generator Page ======
elif page == "🧪 Quiz Generator":
    st.title("🧪 Quiz Generator")
    content = st.text_area("Paste your topic/notes here")
    difficulty = st.selectbox("Select difficulty", ["Easy", "Medium", "Hard"])

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'score' not in st.session_state:
        st.session_state.score = 0

    if st.button("🎯 Generate Quiz"):
        st.session_state.submitted = False
        st.session_state.score = 0

        prompt = f"""
You are a helpful quiz generator.

Generate 10 multiple choice questions based on this content.
- Each question must have 4 options.
- Mark the correct option with an asterisk (*).
- After the options, include a line starting with "Explanation:" followed by a short explanation.

Difficulty: {difficulty}
Content: {content}
"""
        raw_quiz = run_gemini(prompt)
        questions = []

        for block in raw_quiz.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 6:
                q = lines[0]
                options = [line.replace("*", "").strip() for line in lines[1:5]]
                answer = [line.replace("*", "").strip() for line in lines[1:5] if "*" in line]
                explanation = ""
                for line in lines[5:]:
                    if line.lower().startswith("explanation:"):
                        explanation = line.split("Explanation:")[1].strip()
                if answer:
                    questions.append({
                        "question": q,
                        "options": options,
                        "answer": answer[0],
                        "explanation": explanation
                    })
        st.session_state.quiz_data = questions

    if st.session_state.quiz_data:
        st.subheader("📋 Take the Quiz")
        for i, q in enumerate(st.session_state.quiz_data):
            st.radio(f"{i+1}. {q['question']}", q["options"], key=f"user_answer_{i}")

        if st.button("✅ Check Answers") and not st.session_state.submitted:
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                user_ans = st.session_state.get(f"user_answer_{i}")
                correct_ans = q["answer"]
                explanation = q.get("explanation", "")
                col1, col2 = st.columns([4, 1])
                if user_ans == correct_ans:
                    with col1:
                        st.success(f"✅ Q{i+1}: Correct!")
                        st.info(f"Explanation: {explanation}")
                    with col2:
                        st.image(random.choice(correct_gifs), width=100)
                    score += 1
                else:
                    with col1:
                        st.error(f"❌ Q{i+1}: Incorrect. Correct answer: {correct_ans}")
                        st.info(f"Explanation: {explanation}")
                    with col2:
                        st.image(random.choice(incorrect_gifs), width=100)

            st.session_state.score = score
            st.session_state.submitted = True
            st.markdown(f"### 🏆 Your Score: **{score} / 10**")
