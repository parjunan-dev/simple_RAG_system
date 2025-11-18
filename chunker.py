def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)
        start = end - overlap  # step back slightly for context overlap

    return chunks

if __name__ == "__main__":
    sample = "abcdefghijklmnopqrstuvwxyz" * 10
    c = chunk_text(sample)
    print(f"Created {len(c)} chunks.")
