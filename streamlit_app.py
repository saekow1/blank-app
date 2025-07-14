#to run, type this 
# streamlit run streamlit_app.py
# dont forget to install 
# pip install streamlit PyPDF2
# pip install weaviate-client
# pip install openai
# pip install python-dotenv


import streamlit as st
import weaviate
from weaviate.auth import AuthApiKey
import openai
import uuid

import PyPDF2
import os
import re



from weaviate_helper import connect_to_weaviate, upload_to_weaviate

# if st.button("📤 Upload to Weaviate"):
#     client = connect_to_weaviate()
#     upload_to_weaviate(client, parsed_data)
#     st.success("✅ Resume uploaded to Weaviate!")

st.title("🎓 My resume app 🎓")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

#uploaded_file = st.file_uploader("Upload your PDF resume1", type=["pdf"])

import re

# TO EXTRACT TE
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    return full_text

#copilot

def extract_special_data(text):
    #name = re.search(r"Name[:\-]?\s*(.*)", text)
    # Split into lines and guess name

    lines = [line.strip() for line in text.splitlines() if line.strip()]  # remove empty lines

    # Name: first non-empty line
    name = lines[0] if lines else "Not found"

    # Email and phone
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    phone = re.search(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", text)

    # LinkedIn: extract only the URL
    linkedin = None
    for line in lines:
        match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_]+", line)
        if match:
            linkedin = match.group(0)
            break

    # Find all section headers (all caps, possibly with spaces)
    section_indices = {}
    for i, line in enumerate(lines):
        if re.fullmatch(r"[A-Z][A-Z\s]+", line):
            section_indices[line.strip()] = i

    def get_section(header, aliases=None):
        headers = [header]
        if aliases:
            headers += aliases
        for h in headers:
            if h in section_indices:
                start = section_indices[h] + 1
                following_headers = [idx for idx in section_indices.values() if idx > section_indices[h]]
                end = min(following_headers) if following_headers else len(lines)
                section_lines = lines[start:end]
                items = []
                for l in section_lines:
                    l = l.strip("•- ")
                    if l:
                        # Split by comma if it's a skill line
                        if h == "SKILLS" and "," in l:
                            items.extend([x.strip() for x in l.split(",") if x.strip()])
                        else:
                            items.append(l)
                return items
        return []

    skills = get_section("SKILLS")
    education = get_section("EDUCATION", aliases=["CERTIFICATIONS"])
    experience = get_section("WORK EXPERIENCE", aliases=["EXPERIENCE", "PROJECTS"])

    return {
        "Name": name,
        "Email": email.group(0).strip() if email else "Not found",
        "LinkedIn": linkedin if linkedin else "Not found",
        "Phone": phone.group(1).strip() if phone else "Not found",
        "Skills": skills.group(1).strip() if skills else "Not found",
        "Education": education.group(1).strip() if education else "Not found",
        "Experience": experience.group(1).strip() if experience else "Not found"
    }



st.title("📄 Resume Parser")

uploaded_file = st.file_uploader("Upload your PDF resume2", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")
    text = extract_text_from_pdf(uploaded_file)
    parsed_data = extract_special_data(text)

    with st.expander("📌 View Extracted Resume Info", expanded=True):
        st.markdown(f"**Name:** {parsed_data['Name']}")
        st.markdown(f"**Email:** {parsed_data['Email']}")
        st.markdown(f"**LinkedIn:** {parsed_data['LinkedIn']}")
        st.markdown(f"**Phone:** {parsed_data['Phone']}")

        st.markdown("**Skills:**")
        if parsed_data["Skills"]:
            st.markdown("\n".join([f"- {skill}" for skill in parsed_data["Skills"]]))
        else:
            st.markdown("_Not found_")

        st.markdown("**Education:**")
        if parsed_data["Education"]:
            st.markdown("\n".join([f"- {edu}" for edu in parsed_data["Education"]]))
        else:
            st.markdown("_Not found_")

        st.markdown("**Experience:**")
        if parsed_data["Experience"]:
            st.markdown("\n".join([f"- {exp}" for exp in parsed_data["Experience"]]))
        else:
            st.markdown("_Not found_")

    if st.button("📤 Upload to Weaviate", key="upload_weaviate"):
        client = connect_to_weaviate()
        if client is not None and hasattr(client, "is_ready") and client.is_ready():
            upload_to_weaviate(client, parsed_data)
            st.success("✅ Resume uploaded to Weaviate!")
        else:
            st.error("❌ Failed to connect to Weaviate!")



# def extract_special_data(text):
#     #name = re.search(r"Name[:\-]?\s*(.*)", text)
#     # Split into lines and guess name
#     lines = text.strip().split("\n")
#     lines = [line.strip() for line in lines if line.strip()]  # remove empty lines

#     name = lines[0] if lines else "Not found"
#     #lines = [line.strip() for line in text.split("\n") if line.strip()]
#     #name = lines[0] if lines else "Not found"
    
#     email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
#     phone = re.search(r"Phone[:\-]?\s*([\d\-\s\(\)]+)", text, re.IGNORECASE)
#     skills = re.search(r"Skills[:\-]?\s*(.+?)(Education|Experience|$)", text, re.IGNORECASE | re.DOTALL)
#     education = re.search(r"Education[:\-]?\s*(.+?)(Experience|$)", text, re.IGNORECASE | re.DOTALL)
#     experience = re.search(r"Experience[:\-]?\s*(.+)", text, re.IGNORECASE | re.DOTALL)

#     return {
#         #"Name": name.group(1).strip() if name else "Not found",
#         "Name": name,
#         "Email": email.group(0).strip() if email else "Not found",
#         "Phone": phone.group(1).strip() if phone else "Not found",
#         "Skills": skills.group(1).strip() if skills else "Not found",
#         "Education": education.group(1).strip() if education else "Not found",
#         "Experience": experience.group(1).strip() if experience else "Not found"
#     }



# st.title("📄 Resume Parser")

# uploaded_file = st.file_uploader("Upload your PDF resume", type=["pdf"])

# if uploaded_file:
#     st.success("File uploaded successfully!")
#     text = extract_text_from_pdf(uploaded_file)
#     parsed_data = extract_special_data(text)

#     with st.expander("📌 View Extracted Resume Info", expanded=True):
#         for key, value in parsed_data.items():
#             st.markdown(f"**{key}:** {value}")    

#     if st.button("📤 Upload to Weaviate"):
#         client = connect_to_weaviate()
#         if client.is_ready():
#             upload_to_weaviate(client, parsed_data)
#             st.success("✅ Resume uploaded to Weaviate!")
#         else:
#             st.error("❌ Failed to connect to Weaviate!")


