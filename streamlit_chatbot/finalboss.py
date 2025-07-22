import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

# Setup Gemini
genai.configure(api_key="AIzaSyBBs0JdeM_30o3xLOzM9LgqliHpWHarpFQ")
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Syllabus Summarizer", layout="centered")

st.title("📚 Syllabus Helper for Students")
st.write("Choose your subject to get started.")

subject = st.selectbox("Select Subject", [
    "📘 English",
    "📐 Maths",
    "🧲 Physics",
    "🧬 Biology",
    "⚗️ Chemistry",
    "📙 Bahasa Melayu",
    "🈶 Chinese",
    "🔤 Tamil"
])

input_type = st.radio("Choose input type:", ("📄 PDF", "🌐 URL", "📝 Text"))

content = None

# --- Handle different input types ---
if input_type == "📄 PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file is not None:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            text = "\n".join([page.get_text() for page in doc])
        content = text

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

# --- Gemini helpers ---
def summarize_text(text):
    prompt = f"Summarize and simplify this content for students:\n\n{text}"
    return model.generate_content(prompt).text

def give_essay_tips(text):
    prompt = f"Give tips to improve the following English essay:\n\n{text}"
    return model.generate_content(prompt).text

def solve_math_or_physics(text):
    prompt = f"Solve the following question. Include formulas, steps, and final answer clearly:\n\n{text}"
    return model.generate_content(prompt).text

def make_easy_notes(text):
    prompt = f"Convert the following science content into simple and easy-to-understand bullet point notes:\n\n{text}"
    return model.generate_content(prompt).text

def translate_and_explain(text):
    prompt = f"Translate the following non-English academic text into English and explain it simply:\n\n{text}"
    return model.generate_content(prompt).text

# --- Execute based on subject ---
if content:
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

        st.download_button(
            label="📥 Download Result as .txt",
            data=result,
            file_name="result.txt",
            mime="text/plain"
        )