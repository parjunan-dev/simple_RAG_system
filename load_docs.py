import os
from pypdf import PdfReader

def load_documents(data_folder="data"):
    documents = []

    for filename in os.listdir(data_folder):
        filepath = os.path.join(data_folder, filename)

        if filename.lower().endswith(".pdf"):
            text = load_pdf(filepath)
        elif filename.lower().endswith((".txt", ".md")):
            text = load_text(filepath)
        else:
            # skip unsupported files for v1
            continue

        documents.append({
            "filename": filename,
            "text": text
        })

    return documents

def load_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def load_text(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    docs = load_documents()
    for d in docs:
        print(f"{d['filename']} — {len(d['text'])} chars")
