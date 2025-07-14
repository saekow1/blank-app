# To run: streamlit run streamlit_app.py
# Requirements:
# pip install streamlit PyPDF2 weaviate-client openai python-dotenv

import streamlit as st
import PyPDF2
import re
from weaviate_helper import connect_to_weaviate, upload_to_weaviate

st.set_page_config(page_title="Resume Parser & Search", layout="centered")

# Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["📄 Resume Parser", "🔍 Search Resumes"])

# --------------------------
# Resume Parsing Section
# --------------------------
if page == "📄 Resume Parser":
    st.title("📄 Resume Parser & Uploader")

    def extract_text_from_pdf(file):
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        return full_text

    def extract_special_data(text):
        import re

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = " ".join(lines)

        # Name: Just first two capitalized words
        name_line = lines[0] if lines else ""
        name_parts = re.findall(r"[A-Z][a-z]+", name_line)
        name = " ".join(name_parts[:2]) if name_parts else "Not found"

        # Email, Phone, LinkedIn
        email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", full_text)
        phone = re.search(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", full_text)
        linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_]+", full_text)
        linkedin = linkedin_match.group(0) if linkedin_match else "Not found"

        # Skill section: extract after SKILLS or ML/AI
        skill_match = re.search(r"(SKILLS|ML/AI)\s*[:\-]?\s*(.*?)((Development Tools|Technologies|Extra Activities|WORK EXPERIENCE|$))",
                                full_text, re.IGNORECASE | re.DOTALL)
        if skill_match:
            skills_text = skill_match.group(2)
            skills = [s.strip() for s in re.split(r",|\n|•|-", skills_text) if s.strip()]
        else:
            skills = []

        # Helper to extract blocks based on section headers
        def extract_block(label, text, stop_labels):
            stop_pattern = "|".join([re.escape(s) for s in stop_labels])
            regex = rf"{label}\s*[:\-]?\s*(.*?)(?={stop_pattern}|$)"
            pattern = re.compile(regex, re.IGNORECASE | re.DOTALL)
            match = pattern.search(text)
            if match:
                block = match.group(1).strip()
                lines = [line.strip("•- ") for line in block.split("\n") if line.strip()]
                return lines
            return []

        certifications = extract_block(
            label="CERTIFICATIONS",
            text=full_text,
            stop_labels=["PROJECTS", "WORK EXPERIENCE", "EXPERIENCE"]
        )

        experience = extract_block(
            label="WORK EXPERIENCE",
            text=full_text,
            stop_labels=["PROJECTS", "CERTIFICATIONS"]
        )

        projects = extract_block(
            label="PROJECTS",
            text=full_text,
            stop_labels=["CERTIFICATIONS", "EXPERIENCE", "EDUCATION"]
        )

        education = extract_block(
            label="EDUCATION",
            text=full_text,
            stop_labels=["CERTIFICATIONS", "PROJECTS"]
        )

        return {
            "Name": name,
            "Email": email.group(0) if email else "Not found",
            "Phone": phone.group(1) if phone else "Not found",
            "LinkedIn": linkedin or "Not found",
            "Skills": skills,
            "Education": education,
            "Certifications": certifications,
            "Experience": experience,
            "Projects": projects
        }

    uploaded_file = st.file_uploader("📤 Upload your PDF resume", type=["pdf"])

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        text = extract_text_from_pdf(uploaded_file)
        parsed_data = extract_special_data(text)

        with st.expander("📝 View Extracted Resume Info", expanded=True):
            st.markdown(f"**👤 Name:** {parsed_data['Name']}")
            st.markdown(f"**📧 Email:** {parsed_data['Email']}")
            st.markdown(f"**🔗 LinkedIn:** {parsed_data['LinkedIn']}")
            st.markdown(f"**📱 Phone:** {parsed_data['Phone']}")

            def show_list(title, items):
                st.markdown(f"**{title}:**")
                if items:
                    st.markdown("\n".join([f"- {item}" for item in items]))
                else:
                    st.markdown("_Not found_")

            show_list("🧠 Skills", parsed_data["Skills"])
            show_list("🎓 Education", parsed_data["Education"])
            show_list("📜 Certifications", parsed_data["Certifications"])
            show_list("💼 Experience", parsed_data["Experience"])
            show_list("🚀 Projects", parsed_data["Projects"])

        if st.button("🚀 Upload to Weaviate"):
            client = connect_to_weaviate()
            if client and client.is_ready():
                upload_to_weaviate(client, parsed_data)
                st.success("✅ Resume uploaded to Weaviate!")
            else:
                st.error("❌ Could not connect to Weaviate.")

# --------------------------
# Search Section
# --------------------------
elif page == "🔍 Search Resumes":
    st.title("🔍 Semantic Resume Search")

    search_query = st.text_input("Enter your search query (e.g. 'React developer with cloud experience'):")

    if st.button("🔎 Search"):
        if not search_query.strip():
            st.warning("Please enter a search query.")
        else:
            client = connect_to_weaviate()
            if client and client.is_ready():
                collection = client.collections.get("resume_profiles")
                results = collection.query.near_text(query=search_query, limit=5)

                if not results.objects:
                    st.info("No results found.")
                else:
                    st.markdown(f"### 🔍 Top Matches for: `{search_query}`")
                    for obj in results.objects:
                        props = obj.properties
                        st.markdown("----")
                        st.markdown(f"**👤 Name:** {props.get('name', 'N/A')}")
                        st.markdown(f"**📧 Email:** {props.get('email', 'N/A')}")
                        st.markdown(f"**📱 Phone:** {props.get('phone', 'N/A')}")
                        st.markdown(f"**🔗 LinkedIn:** {props.get('linkedin', 'N/A')}")
                        st.markdown(f"**🧠 Skills:**\n{props.get('skills', 'N/A')}")
                        st.markdown(f"**🎓 Education:**\n{props.get('education', 'N/A')}")
                        st.markdown(f"**📜 Certifications:**\n{props.get('certifications', 'N/A')}")
                        st.markdown(f"**💼 Experience:**\n{props.get('experience', 'N/A')}")
                        st.markdown(f"**🚀 Projects:**\n{props.get('projects', 'N/A')}")
            else:
                st.error("❌ Could not connect to Weaviate.")
