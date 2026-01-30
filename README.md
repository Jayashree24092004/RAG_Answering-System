# RAG-Based Document Question Answering System (Free Stack)

A complete **Retrieval‑Augmented Generation (RAG)** system that allows users to upload a document (PDF) and ask questions based on its content. The system uses **semantic search + reranking + local answer synthesis** and runs entirely on **free tiers** (no paid LLM required).

---

## Table of Contents

* [Features](#features)
* [System Architecture](#system-architecture)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [How the System Works](#how-the-system-works)
* [Chunking Strategy](#chunking-strategy)
* [Retrieval Failure Case](#retrieval-failure-case)
* [Metrics Tracked](#metrics-tracked)
* [Setup Instructions](#setup-instructions)
* [How to Run](#how-to-run)
* [Usage](#usage)
* [Limitations](#limitations)
* [Future Improvements](#future-improvements)


---

## Features

* Upload PDF documents
* Automatic text extraction & chunking
* Embedding generation using Cohere (free tier)
* Vector storage and similarity search using Pinecone (free tier)
* Reranking of retrieved chunks using Cohere
* Local answer generation (no paid LLM)
* Simple web UI using Streamlit

---

## System Architecture

High‑level pipeline:

```
User → Streamlit UI → PDF Upload
                ↓
        Text Extraction (PyMuPDF)
                ↓
           Chunking (1000 chars)
                ↓
        Embeddings (Cohere API)
                ↓
        Vector Store (Pinecone)
                ↓
          Similarity Search
                ↓
            Re‑ranking (Cohere)
                ↓
      Local Answer Synthesis
                ↓
            Final Answer
```

---

## Tech Stack

| Layer             | Technology                    |
| ----------------- | ----------------------------- |
| UI                | Streamlit                     |
| Language          | Python                        |
| Document Parsing  | PyMuPDF (fitz)                |
| Embeddings        | Cohere – `embed-english-v3.0` |
| Vector Database   | Pinecone (serverless)         |
| Reranking         | Cohere – `rerank-v3.5`        |
| Answer Generation | Local Python logic            |
| APIs Used         | Cohere, Pinecone              |

---

## Project Structure

```
project-root/
│
├── src/
│   ├── app.py          # Streamlit UI
│   ├── vectorstore.py  # Document processing + vector DB logic
│   └── chatbot.py      # Answer generation logic
│
├── requirements.txt
└── README.md
```

---

## How the System Works

### 1. Document Ingestion

* User uploads a PDF file
* Text is extracted using PyMuPDF

### 2. Chunking

* Text is split into chunks of ~1000 characters
* Ensures semantic continuity while staying embedding‑friendly

### 3. Embedding Generation

* Each chunk is converted into a vector using Cohere embeddings

### 4. Vector Storage

* Vectors are stored in Pinecone

### 5. Query Handling

* User question is embedded
* Similar vectors are retrieved from Pinecone
* Retrieved chunks are reranked using Cohere

### 6. Answer Generation (Free)

* Top chunks are merged
* Important sentences are selected using keyword scoring
* Final answer is synthesized locally

---

## Chunking Strategy

**Chunk size:** 1000 characters

### Why 1000?

* Maintains contextual coherence
* Avoids cutting off sentences
* Reduces number of vectors
* Improves retrieval quality
* Efficient for embedding APIs

### Alternatives considered

| Chunk Size | Result             |
| ---------- | ------------------ |
| 300–500    | Too little context |
| 1000       | Balanced (chosen)  |
| 2000+      | Noisy retrieval    |

---

## Retrieval Failure Case

**Question:**

> What model architecture is used?

**Document contains:**

> We trained a Random Forest classifier...

**Failure:**

* Vector search retrieves training‑related chunks
* Keyword‑based generator fails to infer “architecture” concept

**Reason:**

* Semantic similarity does not guarantee conceptual matching
* No reasoning LLM is used

**Mitigation ideas:**

* Increase rerank candidates
* Use paragraph‑based chunking
* Integrate a local LLM (Ollama / LLaMA)

---

## Metrics Tracked

### End‑to‑end latency

| Stage             | Avg Time   |
| ----------------- | ---------- |
| PDF parsing       | 300–500 ms |
| Embedding         | 1–2 s      |
| Pinecone search   | 150 ms     |
| Reranking         | 200 ms     |
| Answer generation | < 50 ms    |

**Total:** ~2–3 seconds

---

## Setup Instructions

### 1. Clone repository

```bash
git clone https://github.com/Jayashree24092004/RAG_Answering-System/tree/main
cd project
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API keys (Free)

* Cohere: [https://dashboard.cohere.com](https://dashboard.cohere.com)
* Pinecone: [https://www.pinecone.io](https://www.pinecone.io)

---

## How to Run

```bash
streamlit run src/app.py
```

Open browser at:

```
http://localhost:8501
```

---

## Usage

1. Enter Cohere & Pinecone API keys
2. Upload a PDF file
3. Enter a question
4. Click Submit
5. View answer

---

## Limitations

* Only PDF supported (TXT can be added easily)
* Local answer generator is not as fluent as ChatGPT
* No background ingestion job
* No FastAPI endpoint
* No rate limiting

---

## Future Improvements

* Add TXT/DOCX support
* Add FastAPI backend
* Background job processing (Celery / RQ)
* Pydantic request validation
* Redis caching
* Local LLM integration (Ollama, LLaMA, Mistral)
* Source highlighting in UI
* Multi‑document support

---

