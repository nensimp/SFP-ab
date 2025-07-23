
mport streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import random

# Configure Gemini
genai.configure(api_key="AIzaSyBBs0JdeM_30o3xLOzM9LgqliHpWHarpFQ")
model = genai.GenerativeModel("gemini-pro")

# App setup
st.set_page_config(page_title="Syllabus Helper", layout="centered")
st.sidebar.title("\U0001F4C2 Menu")
page = st.sidebar.selectbox("Choose a page", ["\U0001F4DA Analyzer", "\U0001F9EA Quiz Generator"])

# Reaction images
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

# Helper Functions
def chunk_text(text, max_words=1000):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def run_gemini(prompt):
    return model.generate_content(prompt).text

# === PAGE 1: Analyzer ===
if page == "\U0001F4DA Analyzer":
    st.title("\U0001F4DA Syllabus Helper for Students")
    st.write("Choose your subject to get started.")

    subject = st.selectbox("Select Subject", [
        "\U0001F4D8 English", "\U0001F4D0 Maths", "\U0001F9B2 Physics", "\U0001F9EC Biology",
        "\u2697\ufe0f Chemistry", "\U0001F4D9 Bahasa Melayu", "\U0001F238 Chinese", "\U0001F524 Tamil"
    ])

    input_type = st.radio("Choose input type:", ("\U0001F4C4 PDF", "🌐 URL", "📝 Text"))
    content = None

    if input_type == "\U0001F4C4 PDF":
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

        if st.button("\U0001F9E0 Process"):
            with st.spinner("Thinking..."):
                result = ""
                if subject == "\U0001F4D8 English":
                    result = summarize_text(content)
                    st.subheader("\U0001F4DD Summary")
                    st.write(result)
                    if st.checkbox("✍️ Show Essay Improvement Tips"):
                        tips = give_essay_tips(content)
                        st.subheader("💡 Essay Tips")
                        st.write(tips)
                elif subject in ["\U0001F4D0 Maths", "\U0001F9B2 Physics"]:
                    result = solve_math_or_physics(content)
                    st.subheader("\U0001F9EE Solution")
                    st.write(result)
                elif subject in ["\U0001F9EC Biology", "\u2697\ufe0f Chemistry"]:
                    result = make_easy_notes(content)
                    st.subheader("\U0001F4CC Notes")
                    st.write(result)
                else:
                    result = translate_and_explain(content)
                    st.subheader("🌐 Translated & Explained")
                    st.write(result)
                st.download_button("\U0001F4E5 Download as .txt", result, "result.txt", "text/plain")

# === PAGE 2: Quiz Generator ===
elif page == "\U0001F9EA Quiz Generator":
    st.title("\U0001F9EA Quiz Generator")
    st.write("Paste any topic or notes, and I’ll generate a quiz for you!")

    quiz_input = st.text_area("Enter your topic, notes, or content here")
    difficulty = st.selectbox("Select difficulty", ["Easy", "Medium", "Hard"])

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = []
    if 'answers_submitted' not in st.session_state:
        st.session_state.answers_submitted = False
    if 'score' not in st.session_state:
        st.session_state.score = 0

    if st.button("🎯 Generate Quiz"):
        st.session_state.answers_submitted = False
        prompt = f"""
You are a helpful quiz maker. Based on the following content, generate a 10-question multiple choice quiz.
- Each question should have 4 answer choices.
- Mark the correct answer with an asterisk (*)
- Include a short explanation for each correct answer.
- Difficulty: {difficulty}

Content:
{quiz_input}
"""
        raw_quiz = run_gemini(prompt)
        questions = []
        for block in raw_quiz.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 5:
                q = lines[0]
                options = [line.replace("*", "").strip() for line in lines[1:5]]
                answer = [line for line in lines[1:5] if "*" in line]
                explanation = lines[5] if len(lines) > 5 else ""
                if answer:
                    questions.append({
                        "question": q,
                        "options": options,
                        "answer": answer[0].replace("*", "").strip(),
                        "explanation": explanation.strip()
                    })
        st.session_state.quiz_data = questions

    if st.session_state.quiz_data:
        st.subheader("📝 Take the Quiz")
        for i, q in enumerate(st.session_state.quiz_data):
            st.radio(f"{i+1}. {q['question']}", q['options'], key=f"user_answer_{i}")

        if st.button("✅ Check Answers") and not st.session_state.answers_submitted:
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                user_ans = st.session_state.get(f"user_answer_{i}")
                correct_ans = q["answer"]
                explanation = q.get("explanation", "")
                col1, col2 = st.columns([3, 1])
                if user_ans == correct_ans:
                    with col1:
                        st.success(f"Question {i+1}: Correct! 🎉")
                        st.markdown(f"**Correct Answer:** {correct_ans}")
                        st.markdown(f"**Explanation:** {explanation}")
                    with col2:
                        st.image(random.choice(correct_reactions), width=100)
                    score += 1
                else:
                    with col1:
                        st.error(f"Question {i+1}: Incorrect.")
                        st.markdown(f"**Correct Answer:** {correct_ans}")
                        st.markdown(f"**Explanation:** {explanation}")
                    with col2:
                        st.image(random.choice(incorrect_reactions), width=100)
            st.session_state.score = score
            st.session_state.answers_submitted = True
            st.markdown(f"### 🏆 Your Score: {score} / 10")
