import streamlit as st

st.title("🎓 My resume app 🎓")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

#you see me?? i dont see u kaka
# resume_parser_app.py

import PyPDF2
import re

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    return full_text

def extract_special_data(text):
    name = re.search(r"Name[:\-]?\s*(.*)", text)
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    phone = re.search(r"Phone[:\-]?\s*([\d\-\s\(\)]+)", text, re.IGNORECASE)
    skills = re.search(r"Skills[:\-]?\s*(.+?)(Education|Experience|$)", text, re.IGNORECASE | re.DOTALL)
    education = re.search(r"Education[:\-]?\s*(.+?)(Experience|$)", text, re.IGNORECASE | re.DOTALL)
    experience = re.search(r"Experience[:\-]?\s*(.+)", text, re.IGNORECASE | re.DOTALL)

    return {
        "Name": name.group(1).strip() if name else "Not found",
        "Email": email.group(0).strip() if email else "Not found",
        "Phone": phone.group(1).strip() if phone else "Not found",
        "Skills": skills.group(1).strip() if skills else "Not found",
        "Education": education.group(1).strip() if education else "Not found",
        "Experience": experience.group(1).strip() if experience else "Not found"
    }



st.title("📄 Resume Parser")

uploaded_file = st.file_uploader("Upload your PDF resume", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")
    text = extract_text_from_pdf(uploaded_file)
    parsed_data = extract_special_data(text)

    with st.expander("📌 View Extracted Resume Info", expanded=True):
        for key, value in parsed_data.items():
            st.markdown(f"**{key}:** {value}")



