import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import sympy as sp
from math import sqrt

# Setup Gemini
genai.configure(api_key="AIzaSyBBs0JdeM_30o3xLOzM9LgqliHpWHarpFQ")
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Syllabus Summarizer", layout="centered")

st.title("📚 Syllabus Summarizer for Students")
st.write("Upload content or paste a link/text to get a simplified summary.")

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

# --- Summarization function ---
def summarize_text_with_gemini(text):
    prompt = f"Summarize and simplify this content for students:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

# --- Generate Summary ---
if content:
    if st.button("🔍 Summarize"):
        with st.spinner("Summarizing..."):
            result = summarize_text_with_gemini(content)
        st.subheader("📝 Summary")
        st.write(result)

        st.download_button(
            label="📥 Download Summary as .txt",
            data=result,
            file_name="summary.txt",
            mime="text/plain"
        )

# --- Solve Math/Physics Problem ---
st.header("🧮 Solve Math / Physics Problem")
problem_input = st.text_area("Enter your math or physics problem here:")

if st.button("🧪 Solve") and problem_input:
    with st.spinner("Solving..."):
        try:
            prompt = f"Solve this math or physics problem step-by-step: {problem_input}"
            response = model.generate_content(prompt)
            st.subheader("📘 Solution")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error solving the problem: {e}")

