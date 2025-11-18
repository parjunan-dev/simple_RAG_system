# **Simple RAG System (Beginner-Friendly Guide)**

This project shows how to build a **minimal Retrieval-Augmented Generation (RAG)** pipeline from scratch using:

* **Python**
* **OpenAI embeddings**
* **FAISS** (vector search)
* **Local documents** (PDF, TXT, MD)
* **Basic chunking + retrieval**

The goal is to help any beginner understand the *core fundamentals* of RAG without heavy frameworks.

---

## **What This RAG System Does**

1. Loads your knowledge-base documents
2. Extracts text (PDF, TXT, MD)
3. Splits text into 500-character chunks
4. Creates embeddings using OpenAI
5. Stores them in a FAISS index
6. Takes a user question
7. Retrieves the top-3 most relevant chunks
8. Builds a “context + question” RAG prompt
9. Generates a grounded answer using `gpt-4o-mini`

This is the minimal workflow behind most real RAG systems.

---

# 🧩 **1. Folder Structure**

```
your-project/
    data/                # Put PDFs, TXT, MD files here
    load_docs.py
    chunker.py
    embedder.py
    build_index.py
    query.py
    rag_answer.py
    requirements.txt
    README.md
```

---

# **2. Setup**

### Create venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install requirements

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should contain:

```
pypdf
pandas
python-dotenv
faiss-cpu
sentence-transformers
openai
numpy
```

### Add `.env`

```
OPENAI_API_KEY=your_key_here
```

---

# **3. Prepare Your Data**

Place your documents inside:

```
data/
```

Supported formats (for this beginner version):

* `.pdf`
* `.txt`
* `.md`

---

# **4. Build the Index (One-Time Operation)**

This step:

* loads the docs
* chunks them
* creates embeddings
* saves the FAISS index

Run:

```bash
python build_index.py
```

You will see:

```
Total chunks: XXX
Index built and saved!
```

This generates:

* `faiss_index.bin`
* `chunks.pkl`

---

# **5. Test Retrieval Only**

Retrieve the top-3 matching chunks:

```bash
python query.py
```

Example query:

```
How do I create an AI Agent?
```

This prints the retrieved chunk texts.

---

# **6. Full RAG Answer**

This:

* retrieves relevant chunks
* builds a context block
* asks `gpt-4o-mini` to answer using ONLY that context

Run:

```bash
python rag_answer.py
```

Example:

```
Ask a question: How do I configure intents?
```

---

# **How This RAG Works (Beginner Summary)**

1. **load_docs.py**
   Extract text from PDFs / TXT / MD.

2. **chunker.py**
   Split text into **500-character chunks** with **50-character overlap**.

3. **embedder.py**
   Create embeddings using
   **OpenAI `text-embedding-3-small` (1536 dims)**.

4. **build_index.py**
   Store embeddings in a **FAISS L2** index.

5. **query.py**
   Embed the user query with the **same model** and find top-3 closest chunks.

6. **rag_answer.py**
   Build a structured RAG prompt and generate a grounded answer with **gpt-4o-mini**.

That's it — the simplest end-to-end RAG.

---

# **You’re Done**

You now have a working RAG pipeline built **entirely from scratch**, with:

* no LangChain
* no heavy abstractions
* complete transparency
* fundamentals you can port anywhere (Webex, internal tools, custom agents, etc.)
