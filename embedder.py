import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # loads .env automatically

client = OpenAI()

def embed_texts(text_list):
    """
    Takes a list of text chunks and returns a list of embeddings.
    Each embedding is a vector (list of numbers).
    """
    embeddings = []

    for text in text_list:
        response = client.embeddings.create(
            model="text-embedding-3-small",  
            input=text
        )
        vector = response.data[0].embedding
        embeddings.append(vector)
    
    return embeddings


if __name__ == "__main__":
    # quick test
    sample_chunks = ["Hello world!", "Webex AI Agent Studio supports skills-based routing."]
    vectors = embed_texts(sample_chunks)
    print(f"Generated {len(vectors)} embeddings.")
    print(f"Each vector has {len(vectors[0])} dimensions.")
