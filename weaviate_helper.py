# Connects to Weaviate and uploads resume data

import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv
import os
import uuid

# Load credentials from .env
load_dotenv()
print("✅ Loaded:", os.environ.get("WEAVIATE_URL"))

def connect_to_weaviate():
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ.get("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.environ.get("WEAVIATE_API_KEY")),
        headers={"X-OpenAI-Api-Key": os.environ.get("OPENAI_API_KEY")}
    )

    if client.is_ready():
        print("✅ Connected to Weaviate!")
    else:
        print("❌ Failed to connect to Weaviate!")

    return client

def ensure_collection_exists(client):
    collection_name = "resume_profiles"
    if not client.collections.exists(collection_name):
        print("⚠️ Creating collection 'resume_profiles'")
        client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            properties=[
                Property(name="name", data_type=DataType.TEXT),
                Property(name="email", data_type=DataType.TEXT),
                Property(name="phone", data_type=DataType.TEXT),
                Property(name="linkedin", data_type=DataType.TEXT),
                Property(name="skills", data_type=DataType.TEXT),
                Property(name="education", data_type=DataType.TEXT),
                Property(name="certifications", data_type=DataType.TEXT),
                Property(name="experience", data_type=DataType.TEXT),
                Property(name="projects", data_type=DataType.TEXT),
            ]
        )

def upload_to_weaviate(client, parsed_data):
    ensure_collection_exists(client)

    data = {
        "name": parsed_data["Name"],
        "email": parsed_data["Email"],
        "phone": parsed_data["Phone"],
        "linkedin": parsed_data["LinkedIn"],
        "skills": ", ".join(parsed_data.get("Skills", [])),
        "education": "\n".join(parsed_data.get("Education", [])),
        "certifications": "\n".join(parsed_data.get("Certifications", [])),
        "experience": "\n".join(parsed_data.get("Experience", [])),
        "projects": "\n".join(parsed_data.get("Projects", [])),
    }

    client.collections.get("resume_profiles").data.insert(
        uuid=uuid.uuid4(),
        properties=data
    )

    print("✅ Uploaded resume to Weaviate")
