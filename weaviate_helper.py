# Connects to Weaviate and uploads resume data

#-----------------------------------------------------------


##from weaviate.connect import ConnectionParams
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
import os

# Load credentials from .env
load_dotenv()
print("✅ Loaded:", os.environ.get("WEAVIATE_URL"))

def connect_to_weaviate():
    client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.environ.get("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.environ.get("WEAVIATE_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.environ.get("OPENAI_API_KEY")}
    )

    print(client.is_ready())  #should print: `True`

    client.close()  #Free up resources


#def upload_to_weaviate(client, data):
    #get the "Resume" collection and insert the resume data
    #resume_collection = client.collections.get("Resume")
    #resume_collection.data.insert(data_object=data)


def upload_to_weaviate(client, parsed_data):
    import openai
    import uuid
    import os

    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create a single string for embedding
    combined_text = "\n".join([f"{k}: {v}" for k, v in parsed_data.items()])

  
    # Match your collection schema
    data = {
        "name": parsed_data["Name"],
        "email": parsed_data["Email"],
        "phone": parsed_data["Phone"],
        "skills": parsed_data["Skills"], #.split(", "),  # If comma-separated
        "education": parsed_data["Education"],
        "experience": parsed_data["Experience"],
    }

    #client.collections.get("Resume").data.insert(data_object=data)
    
    # Upload into your collection
    client.collections.get("MyFirstCollection").data.insert(
        uuid = uuid.uuid4(),
        properties = data,
        vector = vector
    )


