import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyDrPg76fT83nwzj3ZFHtw7mHvr0lVzyzGE")

def summarize_text_with_gemini(text):
    prompt = f"Summarize and simplify this syllabus content for a student:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("📘 AI Syllabus Summarizer (Gemini)")
st.write("Paste your school notes and get a simplified summary.")

user_input = st.text_area("Enter syllabus content:", height=300)

if st.button("Summarize with Gemini"):
    if user_input.strip():
        with st.spinner("Summarizing with Gemini..."):
            result = summarize_text_with_gemini(user_input)
        st.subheader("📝 Simplified Summary:")
        st.write(result)
    else:
        st.warning("Please enter some text to summarize.")
