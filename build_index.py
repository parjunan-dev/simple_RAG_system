import os
import pickle
import faiss

from load_docs import load_documents
from chunker import chunk_text
from embedder import embed_texts


def build_faiss_index(data_folder="data", chunk_size=500, overlap=50):
    print("🔹 Loading documents...")
    docs = load_documents(data_folder)

    all_chunks = []
    chunk_sources = []  # store (filename, chunk_text)

    # 1. Chunk all documents
    for doc in docs:
        chunks = chunk_text(doc["text"], chunk_size=chunk_size, overlap=overlap)
        for ch in chunks:
            all_chunks.append(ch)
            chunk_sources.append({
                "filename": doc["filename"],
                "text": ch
            })

    print(f"🔹 Total chunks: {len(all_chunks)}")

    # 2. Embed all chunks
    print("🔹 Creating embeddings...")
    embeddings = embed_texts(all_chunks)

    dim = len(embeddings[0])  # number of dimensions (1536)
    index = faiss.IndexFlatL2(dim)

    # Convert to float32 matrix for FAISS
    import numpy as np
    matrix = np.array(embeddings).astype("float32")

    # 3. Add to FAISS
    print("🔹 Adding embeddings to FAISS index...")
    index.add(matrix)

    # 4. Save index + metadata
    faiss.write_index(index, "faiss_index.bin")

    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunk_sources, f)

    print("✅ Index built and saved!")
    print("   - faiss_index.bin")
    print("   - chunks.pkl")


if __name__ == "__main__":
    build_faiss_index()
