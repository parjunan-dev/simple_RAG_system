# 🚀 RAG Knowledge Base Setup Guide

This guide outlines the steps for installing dependencies, preparing your data, and running the scripts to build and test your **Retrieval-Augmented Generation (RAG)** system.

---

## 1. ⚙️ Install Dependencies

Install all required Python packages using `pip`.

```bash
pip install -r requirements.txt
````

**Example `requirements.txt` contents:**

```text
pypdf
pandas
python-dotenv
faiss-cpu
sentence-transformers
openai
numpy
```

-----

## 2\. 🔑 Add `.env` File

Create a file named **`.env`** in your project's root directory and add your OpenAI API key.

```bash
# .env file content
OPENAI_API_KEY=your_api_key_here
```

-----

## 3\. 📄 Prepare Your Data

Place all your Knowledge Base (KB) documents inside a directory named **`data/`**.

  * **Required directory structure:** `/data/`
  * **Supported formats:** `.pdf`, `.txt`, `.md`

-----

## 🛠️ Build and Test the System

## 4\. 🧠 Build the Embedding Index (One-Time Setup)

This step loads documents, splits them, generates embeddings, and builds the FAISS index.

  * **Run the script:**
    ```bash
    python build_index.py
    ```
  * **Expected output on success:**
    ```
    Total chunks: XXX
    Index built and saved!
    ```

-----

## 5\. 🔍 Test Retrieval Only (Semantic Search)

Run this to confirm that semantic search is working.

  * **Run the script:**
    ```bash
    python query.py
    ```
  * **Example query:** `How do I create an AI Agent?`

-----

## 6\. 🤖 Full RAG Answer Generation

This combines retrieval and the LLM (`gpt-4o-mini`) to generate a grounded answer.

  * **Run the script:**
    ```bash
    python rag_answer.py
    ```
  * **Example interaction:** `Ask a question: How do I configure intents?`

-----

## 💡 Beginner Summary — How It Works

| Script | Function | Key Technology |
| :--- | :--- | :--- |
| `load_docs.py` | Text Extraction | `pypdf` |
| `chunker.py` | Text Splitting | 500-character chunks (+50 overlap) |
| `embedder.py` | Embedding Generation | OpenAI `text-embedding-3-small` |
| `build_index.py` | Index Creation | **FAISS L2 index** |
| `rag_answer.py` | Answer Generation | **`gpt-4o-mini`** |
