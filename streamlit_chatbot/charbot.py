import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io

# ==== Gemini Setup ====
genai.configure(api_key="AIzaSyDrPg76fT83nwzj3ZFHtw7mHvr0lVzyzGE")  # Replace with your actual API key
text_model = genai.GenerativeModel("gemini-pro")
vision_model = genai.GenerativeModel("gemini-pro-vision")

# ==== Extract from PDF ====
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ==== Extract from URL ====
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator=" ").strip()
    except Exception as e:
        return f"Error fetching URL: {e}"

# ==== Summarize Text ====
def summarize_text_with_gemini(text):
    prompt = f"Summarize and simplify this syllabus or content for a student:\n\n{text[:6000]}"
    response = text_model.generate_content(prompt)
    return response.text

# ==== Summarize Image ====
def summarize_image_with_gemini(image):
    prompt = "Please summarize and simplify the content in this image for a student."
    response = vision_model.generate_content([prompt, image])
    return response.text

# ==== UI ====
st.set_page_config(page_title="Syllabus Summarizer", layout="centered")
st.title("\ud83d\udcda Syllabus Summarizer (Text, PDF, URL, Image)")
st.write("Upload or paste educational content. Gemini AI will summarize it into student-friendly notes.")

input_type = st.radio("Choose your input type:", ["\ud83d\udcc4 PDF", "\ud83c\udf10 URL", "\ud83d\uddbc\ufe0f Image", "\ud83d\udcdd Raw Text"])

content = ""

# ==== PDF Upload ====
if input_type == "\ud83d\udcc4 PDF":
    uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            content = extract_text_from_pdf(uploaded_pdf)

# ==== URL Input ====
elif input_type == "\ud83c\udf10 URL":
    url = st.text_input("Enter a URL")
    if url:
        with st.spinner("Extracting text from webpage..."):
            content = extract_text_from_url(url)

# ==== Image Upload ====
elif input_type == "\ud83d\uddbc\ufe0f Image":
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        if st.button("\ud83d\udd0d Summarize Image"):
            with st.spinner("Summarizing image..."):
                result = summarize_image_with_gemini(image)
            st.subheader("\ud83d\udcdd Summary")
            st.write(result)

            st.download_button(
                label="\ud83d\udcc5 Download Summary as .txt",
                data=result,
                file_name="summary_from_image.txt",
                mime="text/plain"
            )

# ==== Raw Text Input ====
elif input_type == "\ud83d\udcdd Raw Text":
    content = st.text_area("Paste your text here")

# ==== Summarize Text ====
if content and input_type != "\ud83d\uddbc\ufe0f Image":
    if st.button("\ud83d\udd0d Summarize"):
        with st.spinner("Summarizing..."):
            result = summarize_text_with_gemini(content)
        st.subheader("\ud83d\udcdd Summary")
        st.write(result)

        st.download_button(
            label="\ud83d\udcc5 Download Summary as .txt",
            data=result,
            file_name="summary.txt",
            mime="text/plain"
        )
