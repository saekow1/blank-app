# Extracts text + info from uploaded PDF resume

import PyPDF2
import re

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    return full_text

_ = """
def extract_special_data(text):
    name = re.search(r"Name[:\-]?\s*(.*)", text)
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    phone = re.search(r"Phone[:\-]?\s*([\d\-\s\(\)]+)", text, re.IGNORECASE)
    skills = re.search(r"Skills[:\-]?\s*(.+?)(Education|Experience|$)", text, re.IGNORECASE | re.DOTALL)
    education = re.search(r"Education[:\-]?\s*(.+?)(Experience|$)", text, re.IGNORECASE | re.DOTALL)
    experience = re.search(r"Experience[:\-]?\s*(.+)", text, re.IGNORECASE | re.DOTALL)

    return {
        "name": name.group(1).strip() if name else "Not found",
        "email": email.group(0).strip() if email else "Not found",
        "phone": phone.group(1).strip() if phone else "Not found",
        "skills": skills.group(1).strip().split(",") if skills else [],
        "education": education.group(1).strip() if education else "Not found",
        "experience": experience.group(1).strip() if experience else "Not found",
        "summary": "Imported from PDF"
    }
    """
