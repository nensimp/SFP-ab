import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

# ==== Gemini Config ====
genai.configure(api_key="AIzaSyDrPg76fT83nwzj3ZFHtw7mHvr0lVzyzGE")
model = genai.GenerativeModel("gemini-pro")

# ==== Helper: Extract from PDF ====
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ==== Helper: Extract from URL ====
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=' ')
        return text.strip()
    except Exception as e:
        return f"Error fetching URL: {e}"

# ==== Gemini Summary Function ====
def summarize_text_with_gemini(text):
    prompt = f"Summarize and simplify this syllabus or content for a student:\n\n{text[:6000]}"
    response = model.generate_content(prompt)
    return response.text

# ==== Streamlit UI ====
st.set_page_config(page_title="Syllabus Summarizer", layout="centered")
st.title("📚 Syllabus Summarizer using Gemini AI")
st.write("Upload a PDF or paste a link to summarize complex content into student-friendly notes.")

option = st.radio("Choose Input Type:", ["📄 Upload PDF", "🌐 Paste a URL"])

user_text = ""

# ==== Handle PDF Upload ====
if option == "📄 Upload PDF":
    uploaded_pdf = st.file_uploader("Upload your PDF file", type="pdf")
    if uploaded_pdf:
        with st.spinner("Reading PDF..."):
            user_text = extract_text_from_pdf(uploaded_pdf)

# ==== Handle URL Input ====
if option == "🌐 Paste a URL":
    url = st.text_input("Enter a valid URL")
    if url:
        with st.spinner("Fetching and extracting text from URL..."):
            user_text = extract_text_from_url(url)

# ==== Show Raw Extracted Text (optional) ====
if user_text:
    st.text_area("📄 Extracted Text (Preview)", user_text[:1000], height=200)

    if st.button("🔍 Summarize"):
        with st.spinner("Summarizing with Gemini..."):
            result = summarize_text_with_gemini(user_text)
        st.subheader("📝 Summary")
        st.write(result)