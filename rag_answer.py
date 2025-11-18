import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Load FAISS + chunks (same as query.py)
index = faiss.read_index("faiss_index.bin")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)


def embed_query(query: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding


def retrieve_chunks(query, top_k=3):
    query_emb = embed_query(query)
    query_emb = np.array([query_emb]).astype("float32")

    distances, indices = index.search(query_emb, top_k)

    retrieved = []
    for idx in indices[0]:
        retrieved.append(chunks[idx]["text"])

    return retrieved


def build_rag_prompt(retrieved_chunks, question):
    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""
You are an assistant that answers questions using ONLY the information in the provided context.

CONTEXT:
{context}

QUESTION:
{question}

RULES:
- Answer ONLY using the context.
- If the answer is not in the context, say "I don't know."
- Be concise and clear.
"""

    return prompt.strip()

def answer_question(question):
    # 1. Retrieve top chunks
    retrieved = retrieve_chunks(question, top_k=3)

    # 2. Build RAG prompt
    prompt = build_rag_prompt(retrieved, question)

    # 3. Call OpenAI LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    return answer

if __name__ == "__main__":
    q = input("Ask a question: ")
    ans = answer_question(q)
    print("\n💬 Answer:\n")
    print(ans)
