# LEARN_THIS.md — RAG System Guide

This page answers the *why* and *how* behind every decision in this RAG system. Think of it as questions you should be able to answer after building this.

---

## **Core Concepts**

### Q: What is Retrieval-Augmented Generation (RAG)?

**The short answer:**
RAG is a pattern where you retrieve relevant context from a document database, then feed that context + user question to an LLM. Instead of the LLM guessing from training data, it grounds its answer in *your actual documents*.

**Why it matters:**
- Reduces hallucinations (LLM sticks to your docs)
- Works on proprietary/recent data (no retraining needed)
- Scalable (add more docs, same system)
- Transparent (you can see *which* docs informed the answer)

**Real use case:** Customer service bot for your company's docs. User asks "How do I configure intents?" → system retrieves your intent guide → bot answers from that guide, not generic training data.

---

### Q: Why embeddings? Why not just keyword search?

**The problem with keyword search:**
- "How do I set up voicebot?" matches nothing if your docs say "configure automated agent"
- Synonym/semantic mismatch kills relevance
- Poor on questions phrased differently than your docs

**How embeddings fix it:**
- Convert text → vector (1536 dimensions for OpenAI `text-embedding-3-small`)
- Vectors capture *meaning*, not just words
- "How do I set up voicebot?" and "Configure automated agent" → similar vectors → match found
- Can find semantically related content even with zero keyword overlap

**When to use keyword instead:**
- Exact match is critical (legal doc references, product IDs)
- Your docs are highly structured/tagged already
- Speed is more important than semantic accuracy

We use embeddings because semantic search handles paraphrasing and synonyms. For a production system, we'd use hybrid search: embeddings for semantic matching (handling paraphrasing), combined with BM25 keyword scoring (ensuring exact terms appear). This avoids irrelevant-but-semantically-similar results while catching paraphrased questions.
---

### Q: What's the difference between chunking strategies?

**This project uses: Fixed-size chunks (500 chars, 50-char overlap)**

**Why that choice:**
- Simple to implement (no dependencies)
- Predictable retrieval behavior
- Works for most documents (FAQs, guides, documentation)
- Avoids empty or tiny chunks

**When it breaks:**
- Long-form narrative (chapters lose context mid-chunk)
- Tables/structured data (splits rows)
- Code blocks (splits functions)

**Better alternatives:**

| Strategy | Use case | Trade-off |
|----------|----------|-----------|
| **Semantic chunking** | Topic-coherent splits | More complex (needs clustering), slower |
| **Recursive (hierarchy)** | Long docs with sections | Preserves document structure, but overhead |
| **Sentence-aware** | Conversational docs | Varies chunk size, harder to predict |
| **Page-based** | PDFs where page ≈ topic | Rigid, loses content that spans pages |

**Hands-on alternative:** Build a semantic chunker using the same embeddings—split text where embedding distance > threshold. You'd detect natural breaks in meaning without hard cutoffs.

---

## **Architecture Decisions**

### Q: Why FAISS and not [PostgreSQL / Pinecone / Weaviate]?

**FAISS (this project):**
- ✅ In-process, zero network latency
- ✅ Tiny footprint (good for demos, local dev)
- ❌ Single-threaded, not distributed
- ❌ No persistence/durability beyond pickle
- ❌ No metadata filtering

**PostgreSQL + pgvector:**
- ✅ Durable, handles metadata queries
- ✅ SQL filtering ("chunks from doc X with score > 0.8")
- ✅ Scalable
- ❌ Network latency
- ❌ Overkill for a demo

**Pinecone / Weaviate (managed vector DBs):**
- ✅ Fully managed, scales infinitely
- ✅ Built-in metadata, filtering, reranking
- ❌ Cloud dependency, API rate limits
- ❌ Cost per query

**Your decision tree in an interview:**
> *"For a prototype or internal tool, FAISS is perfect. For a customer-facing system at Cisco handling 1000s of queries daily, I'd migrate to pgvector + PostgreSQL for durability and metadata filtering. For a multi-tenant SaaS, Pinecone or Weaviate."*

---

### Q: How does the embedding model choice affect results?

**This project uses: OpenAI `text-embedding-3-small` (1536 dims)**

**Why OpenAI over sentence-transformers?**
- Slightly better semantic quality (trained on massive web data)
- API-based (no GPU needed locally)
- Battle-tested at scale

**Why NOT `text-embedding-3-large`?**
- Overkill for most RAG (small is 99% as good)
- Costs 2x, slower
- Harder to store/search (more dimensions)

**Alternative: `sentence-transformers/all-MiniLM-L6-v2`**
- Free, runs locally (no API key)
- Smaller vectors (384 dims), faster search
- ~10% lower quality, but often "good enough"
- Portfolio move: *"I chose OpenAI for this demo, but for a privacy-first system (WxCC on-prem), I'd use sentence-transformers to avoid external API calls."*

**How to experiment:**
```python
# In embedder.py, swap the model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(text_chunks)
```
Then rebuild your index and compare retrieval quality.

---

### Q: Why retrieve top-3 chunks? Why not top-1 or top-10?

**Trade-offs:**

| Count | Pros | Cons |
|-------|------|------|
| **1** | Focused, concise context | Miss nuance, risk low quality |
| **3** (this project) | Balanced—covers multiple angles | Slight verbosity in LLM context |
| **10+** | More coverage | Token bloat, LLM attention dilution |

**The real answer:** It depends on:
- **Context window size** (gpt-4o-mini has 128k tokens; you can afford more)
- **Chunk quality** (if your chunks are noisy, retrieve fewer)
- **Question complexity** ("How does X work?" needs more context than "What is X?")

**Production approach:**
- Start with top-3, measure answer quality + cost
- If answers lack nuance → try top-5
- If cost is high → drop to top-2
- Use your eval framework (mentioned in Tier 1) to measure impact

---

## **Hands-On: Build Your Own RAG**

### Alternative Use Case #1: Code Documentation Bot

**Your docs:** Python function docstrings + GitHub issues (your WxCC widget repo)

**Chunks:** One function per chunk (or semantic boundaries around classes)

**Query:** "How do I customize the agent desktop layout?"

**Changes:**
1. `load_docs.py` → Parse Python AST instead of PDFs; extract docstring + function signature
2. `chunker.py` → Skip it; each function is one logical unit
3. Everything else → Same (embeddings, retrieval, RAG answer)

**Code sketch:**
```python
import ast

def extract_functions(file_path):
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            source = ast.get_source_segment(...)  # Get function code
            chunks.append(f"{node.name}\n{docstring}\n{source}")
    return chunks
```

---

### Alternative Use Case #2: Cisco Webex Knowledge Base (WxCC context)

**Your docs:** Cisco WxCC admin guide PDFs, your own demos, architecture diagrams (as text)

**Chunks:** Semantic chunking by feature area (Skills, Flows, Reporting, etc.)

**Query:** "How do I set up skill-based routing?"

**Changes:**
1. Add metadata to chunks: `{"source": "admin_guide.pdf", "section": "Skills", "doc_version": "12.1"}`
2. Swap FAISS → PostgreSQL + pgvector for filtering
3. Add metadata filtering: *"Only retrieve from latest doc version"*
4. Add re-ranking: After retrieval, score chunks by metadata relevance (e.g., prefer official docs over your notes)

**Why this matters for your portfolio:** This is *exactly* what UOB/OCBC would want—a RAG system that doesn't just find chunks, but understands *which* chunks are authoritative.

---

### Alternative Use Case #3: Multi-Modal RAG (Images + Text)

**Your docs:** PDFs with tables, diagrams, screenshots

**Chunks:** Extract text + encode images separately using CLIP embeddings

**Query:** "What does the WxCC architecture diagram show?"

**Changes:**
1. `load_docs.py` → Use `PyPDF2` + `pdf2image` to extract images
2. `embedder.py` → Add CLIP model for image embeddings; merge text + image embeddings in same vector space
3. `query.py` → Search across both; retrieve images + text together
4. `rag_answer.py` → Pass retrieved images + text to gpt-4o (which understands images)

**Why it's hard:** Aligning image + text in the same embedding space is non-trivial. But it's a killer differentiator for a portfolio.

---

## **Common Mistakes & How to Avoid Them**

### "My retrieval is terrible"

**Debug checklist:**
1. Are your chunks too large? (>800 chars → try 400)
2. Are your chunks too small? (<100 chars → too fragmented)
3. Are you retrieving top-1? (Try top-5; see if quality improves)
4. Is your embedding model overtrained on different data? (Switch model, re-embed)
5. Are your documents *actually* relevant? (If docs don't answer the question, RAG can't help)

**Quick fix:** Build a eval set of 10 (question, expected_chunk_id) pairs. Score retrieval quality. Fix worst cases first.

---

### "The LLM answer is hallucinating"

**Root causes:**
1. Retrieved chunks are irrelevant (see above)
2. Chunks are too vague or incomplete
3. Prompt doesn't force the LLM to stay grounded

**Fix your prompt in `rag_answer.py`:**
```python
prompt = f"""
You are a helpful assistant. Answer the user's question using ONLY the context below.
If the context doesn't contain the answer, say "I don't know" instead of guessing.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:
"""
```

The `ONLY` + `I don't know` instruction is powerful.

---

### "Embeddings are expensive"

**Numbers:**
- OpenAI `text-embedding-3-small`: $0.02 per 1M tokens (~500K chunks)
- Your first run: $0.01–$0.05
- Re-indexing (rare): Same

**This is cheap.** But in an interview:
> *"If cost were a concern—say, indexing 1M documents—I'd cache embeddings, batch API calls, or switch to a local model (sentence-transformers) to run on-device."*

---

## **Interview Questions You Should Be Able to Answer**

1. **Why did you chunk at 500 characters?** (Trade-off explanation)
2. **How would you improve retrieval quality?** (Semantic chunking, re-ranking, hybrid search)
3. **What breaks in your system at scale?** (FAISS single-threading, no persistence, metadata filtering)
4. **How would you measure if your RAG works?** (Eval framework: precision, recall, faithfulness)
5. **Why OpenAI embeddings vs. local?** (Quality vs. privacy/cost; you pick based on context)
6. **How would you add metadata filtering?** (Migrate to pgvector + SQL)
7. **What's the difference between your chunks overlapping by 50 chars?** (Preserves context at boundaries; avoids duplicate answers)
8. **If a query returned bad results, how'd you debug?** (Check chunks, embedding quality, retrieval top-k, prompt design)
9. **Could you adapt this to [use case X]?** (Yes, sketch it: code docs, images, logs, etc.)
10. **What's the latency breakdown?** (Embedding query: ~50ms, FAISS search: ~5ms, LLM call: ~1–2s. LLM dominates.)

---

## **Next Steps**

After reading this, go build:

1. **Your eval harness** — 10 test questions, measure if retrieved chunks are correct
2. **Your alternative use case** — Copy this structure, swap the docs
3. **Your web UI** — Streamlit interface to show it off (see `streamlit/README` later)

Then, in an interview, you don't just say *"I built a RAG system."* You say:

> *"I built a RAG system from scratch, understand the trade-offs at every layer (chunking, embeddings, retrieval, reranking), can measure its quality with an eval framework, and can adapt it to different domains—code, images, documents—depending on the use case."*

That's portfolio-grade.
