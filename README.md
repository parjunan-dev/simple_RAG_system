Simple RAG System (Beginner-Friendly Guide)
This project demonstrates how to build a minimal Retrieval-Augmented Generation (RAG) pipeline from scratch using:

Python

OpenAI embeddings

FAISS (vector search)

Local documents (PDF, TXT, MD)

Basic fixed-size chunking

This setup is intentionally simple, transparent, and perfect for beginners who want to understand the fundamentals behind RAG systems.

🚀 What This RAG System Does
Loads your knowledge base documents

Extracts text from PDF, TXT, and MD files

Splits text into 500-character chunks with 50-character overlap

Creates embeddings using OpenAI text-embedding-3-small (1536 dims)

Stores embeddings in a FAISS L2 index

Accepts a user question

Retrieves the top-3 most relevant chunks via semantic search

Builds a structured RAG prompt using retrieved context

Generates a grounded answer using OpenAI gpt-4o-mini

This is the simplest full RAG pipeline you can build — no frameworks, no abstractions.

📂 1. Folder Structure
your-project/
│
├── data/ # Put your PDFs, TXT, MD files here
├── load_docs.py
├── chunker.py
├── embedder.py
├── build_index.py
├── query.py
├── rag_answer.py
├── requirements.txt
└── README.md
🔧 2. Setup
Create virtual environment
Bash

python3 -m venv .venv
source .venv/bin/activate
Install dependencies
Bash

pip install -r requirements.txt
Example requirements.txt

pypdf
pandas
python-dotenv
faiss-cpu
sentence-transformers
openai
numpy
Add .env file
Create a .env file:

Code snippet

OPENAI_API_KEY=your_api_key_here
📄 3. Prepare Your Data
Place all your KB documents inside:

data/

Supported formats in this beginner version:

.pdf

.txt

.md

🛠️ 4. Build the Embedding Index (One-Time Setup)
This step:

Loads all KB docs

Extracts text

Splits into chunks

Generates OpenAI embeddings

Builds the FAISS index

Run:

Bash

python build_index.py
If successful, you will see:

Total chunks: XXX
Index built and saved!
This generates:

faiss_index.bin

chunks.pkl

🔍 5. Test Retrieval Only
To confirm that semantic search works:

Bash

python query.py
Example query:

How do I create an AI Agent?

You should see the top-3 matching chunks printed.

🤖 6. Full RAG Answer Generation
This combines:

Retrieval

Context construction

LLM response

Run:

Bash

python rag_answer.py
Example:

Ask a question: How do I configure intents?

This uses gpt-4o-mini to answer only using the retrieved context — avoiding hallucinations.

🧠 Beginner Summary — How It Works
load_docs.py

Extracts text using pypdf or direct read.

chunker.py

Splits text into 500-character chunks (+50 overlap).

embedder.py

Generates OpenAI embeddings (text-embedding-3-small, 1536 dims).

build_index.py

Creates a FAISS L2 index and stores embeddings + metadata.

query.py

Embeds user query using the same OpenAI model.

Retrieves top-3 chunks.

rag_answer.py

Builds RAG prompt (context + question + rules).

Uses gpt-4o-mini to generate grounded answers.

This is the essential structure behind most real RAG applications.
