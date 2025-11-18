import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # loads .env automatically
client = OpenAI()

def embed_query(query):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding

# 1. Load FAISS index
index = faiss.read_index("faiss_index.bin")

# 2. Load chunks
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

def search(query, top_k=3):
    query_emb = [embed_query(query)]  # embed using same model as index

    import numpy as np
    query_emb = np.array(query_emb).astype("float32")

    distances, indices = index.search(query_emb, top_k)

    results = []
    for score, idx in zip(distances[0], indices[0]):
        chunk_text = chunks[idx]["text"]
        results.append((score, chunk_text))

    return results


if __name__ == "__main__":
    user_q = input("Ask a question: ")
    results = search(user_q)

    print("\n🔎 Top matches:\n")
    for i, (score, text) in enumerate(results, 1):
        print(f"Result #{i} (distance: {score:.4f})")
        print(text[:400])   # show first 400 chars
        print("-" * 60)
