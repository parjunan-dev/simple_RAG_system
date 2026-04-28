# LEARN_THIS.md — RAG System Guide

This page answers the *why* and *how* behind every decision in this RAG system. Think of it as questions you should be able to answer after building this.

---

## **Core Concepts**

### Q: What is Retrieval-Augmented Generation (RAG)?

**Simple answer:**
You have documents. A user asks a question. Your system finds the relevant documents, gives them to an LLM, and the LLM answers based on those documents, not from memory.

**Why?**
- The LLM can answer questions about *your specific docs* (not just general knowledge)
- You can see *which docs* it used (transparent)
- Less hallucinating (it's grounded in what's actually written)

**Real example:** A customer service chatbot that answers questions about your contact center product's setup guides. User asks "How do I set up skill-based routing?" → bot finds your routing guide → bot answers from that guide.

---

### Q: Why use embeddings? Why not just search for keywords?

**The problem with keywords:**
- User asks: "How do I set up an automated agent?"
- Your docs say: "Configure voicebot"
- Keyword search fails (no word match)
- User gets no answer

**How embeddings fix it:**
- Convert text to numbers (a "vector")
- Similar meaning = similar vectors
- "Set up automated agent" and "Configure voicebot" get similar vectors → match found
- Works even if words are totally different

**When to use keywords instead:**
- Exact match matters (like looking for a specific product ID: "ABC-12345")
- Your docs are short and well-labeled (metadata search is better)

**For production:** Use both. Search by meaning (embeddings) AND by keywords. Together they're stronger.

---

### Q: Why split text into chunks?

**The problem:** Your PDF is 50 pages. User asks "How do I configure intents?" You can't feed all 50 pages to the LLM (too slow, too expensive, LLM gets confused).

**The solution:** Split into small pieces (chunks). When user asks a question, find the 3 most relevant chunks, only send those to the LLM.

**This project splits at 500 characters with 50-char overlap:**
- 500 chars ≈ 1–2 paragraphs (readable by LLM)
- 50-char overlap = overlap between chunks (so you don't lose context at boundaries)

**Why this works:**
- Simple (no fancy algorithms)
- Predictable (you know how big each chunk is)
- Works for most docs (guides, FAQs, instructions)

**When it breaks:**
- A table gets split in half (useless chunks)
- A story or chapter gets chopped mid-thought
- Code function gets split across chunks

**Better for specific cases:**
- Code docs? Chunk by function (one function = one chunk)
- Long stories? Chunk by section/chapter
- Tables? Keep together, don't split

---

## **Architecture Decisions**

### Q: Why FAISS for storage? What are the alternatives?

**This project uses FAISS (a local vector store):**
- ✅ Fast (search happens on your machine, no network)
- ✅ Free
- ✅ Good for demos
- ❌ Dies if computer crashes (no backup)
- ❌ Can't filter by date/author/source

**Alternative: PostgreSQL (database with vector support):**
- ✅ Survives crashes (saved to disk)
- ✅ Can filter by metadata ("only show docs from 2025")
- ✅ Handles millions of documents
- ❌ Slightly slower (network call)
- ❌ Need to manage a database

**Alternative: Pinecone (cloud service):**
- ✅ Fully managed (no setup)
- ✅ Infinitely scalable
- ❌ Pay per query
- ❌ Your data lives on their servers

**In an interview, you'd say:**
> *"I chose FAISS for this demo because it's simple and fast. For production at Cisco (handling thousands of queries daily), I'd use PostgreSQL so data is safe and searchable by metadata. For a consumer product, Pinecone makes sense because they handle scale."*

---

### Q: Why OpenAI embeddings?

**This project uses OpenAI's embedding model:**
- ✅ High quality (works well across domains)
- ✅ No GPU needed (runs online)
- ✅ Cheap ($0.02 per million tokens)
- ❌ Needs API key
- ❌ Depends on internet connection

**Alternative: sentence-transformers (free, local):**
- ✅ Free
- ✅ Runs on your machine (no API, no internet)
- ✅ Private (your docs don't leave your computer)
- ❌ Lower quality (not as good at finding matches)
- ❌ Slower on laptop (needs GPU to be fast)

**When to use local models:**
- Privacy-first systems (banking, healthcare)
- Offline environments (on-prem Webex deployments)
- Tight budgets

**When to use OpenAI:**
- Quick prototypes (this project)
- High quality matters more than cost
- Internet is available

---

### Q: Why retrieve 3 chunks? Why not 1 or 10?

**The trade-off:**
- 1 chunk: Fast, focused, but might miss nuance
- 3 chunks: Good balance (this project)
- 10 chunks: More complete picture, but LLM sees more noise

**Real decision:** It depends on:
- How good are your chunks? (Noisy chunks → retrieve fewer)
- How complex is the question? ("What is skill-based routing?" needs less context than "Compare skill-based vs. agent-based routing")
- How much can you afford to spend? (More chunks = more tokens = more money)

**How to pick:** Start with 3. If answers lack detail, try 5. If too slow, try 2. Measure quality and cost.

---

## **Hands-On: Build Your Own RAG**

### Use Case #1: Code Documentation

**Your docs:** Python functions and their docstrings (from your GitHub)

**Changes:**
1. Instead of splitting PDFs by character count, extract one chunk per function
2. Each chunk = function name + docstring + code
3. Rest stays the same (embeddings, retrieval, LLM answer)

**Why it's better than fixed-size chunks:**
- A function is a natural unit (you retrieve the whole function, not half)
- Cleaner boundaries

---

### Use Case #2: Cisco Product Knowledge Base

**Your docs:** Product admin guides, your own demo notes, architecture diagrams

**Changes:**
1. Tag each chunk with metadata: which doc, which version, which feature area
2. Switch from FAISS to PostgreSQL (so you can filter: "only from the latest guide")
3. Retrieve top-3, but prefer official docs over your notes

**Why this matters:**
- UOB/OCBC want to know *which* source the answer came from (official vs. your interpretation)
- You can update guides and only retrieve new versions

---

### Use Case #3: Logs or Chat History

**Your docs:** Webex contact center logs, chat transcripts, tickets

**Changes:**
1. Chunk by conversation (one support ticket = one chunk)
2. Add metadata: timestamp, customer ID, resolution status
3. Query: "Show me tickets similar to this one" (find past solutions)

**Why it works:**
- Chunking by conversation is natural (don't split conversations)
- Metadata helps: "only show resolved tickets from this month"

---

## **Common Problems & How to Fix Them**

### "My retrieval sucks"

**Checklist:**
1. Are chunks the right size? (Try 300 chars, then 700, see what works)
2. Are you retrieving too few chunks? (Try top-5 instead of top-3)
3. Do your documents actually answer the question? (If not, RAG can't help)
4. Try a different embedding model (maybe OpenAI's quality isn't right for your domain)

**How to test:** Create 10 test questions where you already know which chunks should match. See how many your system gets right.

---

### "The LLM is making stuff up"

**Root causes:**
1. You're retrieving the wrong chunks (see above)
2. Your prompt is weak (it's letting the LLM guess)

**Fix the prompt:**
```python
prompt = f"""
Answer the user's question using ONLY the information below.
If the answer is not in this information, say "I don't know".

Information:
{retrieved_chunks}

Question: {user_question}

Answer:
"""
```

The key: "ONLY" + "I don't know" forces the LLM to stick to your docs.

---

### "This is slow"

**Where's the time going?**
- Embedding the query: ~100ms
- Searching FAISS: ~5ms
- Calling the LLM: ~1–2 seconds ← Here's where 95% of time goes

**To speed up:**
- Use a faster LLM (gpt-4o-mini instead of gpt-4)
- Retrieve fewer chunks (top-2 instead of top-3)
- Cache results (if same question asked twice, reuse answer)

---

## **Interview Questions You Should Know**

1. **Why embeddings instead of keywords?** (Handle paraphrasing, synonyms)
2. **Why 500-character chunks?** (Good balance between context and speed)
3. **How would you make this system production-ready?** (Switch to PostgreSQL, add metadata filtering, eval framework)
4. **What would break at scale?** (FAISS can't save data safely, single machine limit)
5. **How do you know if your RAG works?** (Test with real questions, measure accuracy)
6. **Could you adapt this to [other use case]?** (Yes—code docs, logs, chat history, images)
7. **Why OpenAI embeddings?** (Good quality + cheap. Alternative: local models for privacy)
8. **Why retrieve 3 chunks instead of 1?** (Trade-off: 1 is fast but risky, 3 is balanced, more is slow)
9. **What if the LLM hallucinates?** (Retrieved chunks aren't relevant OR prompt isn't strict enough)
10. **How would you measure latency?** (LLM call dominates; everything else is <200ms)

---

## **Next Steps**

1. **Test your system** — Ask it 10 real questions. Do the answers make sense?
2. **Build for a new use case** — Apply this to code docs, Product knowledge base, or logs
3. **Add a web UI** — Make it clickable (Streamlit + chat interface)
4. **Measure quality** — Write code that scores retrieval accuracy

Then in an interview:

> *"I built a RAG system from scratch. I understand why embeddings work, how chunking affects quality, why I chose FAISS (and when I wouldn't), and how to adapt it to different use cases. I can measure if it's working and scale it to production."*

That's portfolio-grade.
