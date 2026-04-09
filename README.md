# EzeeChatBot---API
# 🚀 AI RAG Chatbot Backend (Task 1)

## 📌 Overview

This project is a **production-ready Retrieval-Augmented Generation (RAG) chatbot backend** built using FastAPI.
It allows users to upload documents and ask questions, where answers are generated strictly from the uploaded content.

The system ensures **no hallucination**, uses **semantic search**, and supports **real-time streaming responses**.

---

## 🎯 Key Features

### ✅ Document Ingestion

* Upload text or URL-based content
* Automatic text extraction (HTML parsing supported)
* Intelligent chunking with overlap

### ✅ Embeddings & Storage

* Embeddings generated using **local models (Ollama)**
* Stored in **ChromaDB vector database**
* Each chatbot has isolated storage using `bot_id`

### ✅ Retrieval-Augmented Generation (RAG)

* Semantic similarity search (Top-K retrieval)
* Context-aware answer generation
* Strict grounding (answers only from document)

### ✅ No Hallucination Guarantee

If the answer is not found in the document, the system responds with:

> "I cannot find this information in the uploaded document."

---

### ✅ Streaming Responses

* Real-time token streaming (like ChatGPT typing)
* Improves user experience

---

### ✅ Performance & Stats Tracking

* Latency tracking (ms)
* Token usage estimation
* Cost tracking (set to 0 for Ollama)
* No-answer detection

---

## 🏗️ Architecture

```
User → FastAPI API
        ↓
   Chunking Service
        ↓
   Embedding Model (Ollama)
        ↓
   ChromaDB (Vector Store)
        ↓
   Retrieval (Top-K)
        ↓
   LLM (Ollama - llama3)
        ↓
   Response (Streaming)
```

---

##  Tech Stack

* **Backend:** FastAPI
* **LLM:** Ollama (llama3)
* **Embeddings:** nomic-embed-text (Ollama)
* **Vector DB:** ChromaDB
* **Language:** Python 3.11+

---

## Project Structure

```
ezeechatbot/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── upload.py
│   │   ├── chat.py
│   │   └── stats.py
│   └── services/
│       ├── chunker.py
│       ├── embedder.py
│       ├── vector_store.py
│       └── llm.py
├── requirements.txt
├── .env
└── README.md
```

---

##  Setup Instructions

### 1 Clone the repository

```
git clone <your-repo-link>
cd ezeechatbot
```

---

### 2 Create virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

---

### 3️ Install dependencies

```
pip install -r requirements.txt
pip install ollama
```

---

### 4️ Run Ollama server

```
ollama serve
```

---

### 5️ Pull required models

```
ollama pull llama3
ollama pull nomic-embed-text
```

---

### 6️ Environment variables (.env)

```
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3
EMBEDDING_MODEL=nomic-embed-text
CHROMA_PERSIST_DIR=./chroma_db
```

---

### 7️ Run FastAPI server

```
uvicorn app.main:app --reload
```

---

## API Endpoints

### 🔹 1. Upload Document

**POST** `/upload`

Request:

```
{
  "text": "Python is used in AI and ML."
}
```

Response:

```
{
  "bot_id": "unique-id"
}
```

---

### 2. Chat with Document
POST`/chat`

Request:

```
{
  "bot_id": "your-bot-id",
  "user_message": "What is Python used for?",
  "conversation_history": []
}
```

Response:

```
{
  "answer": "Python is used in AI and ML.",
  "sources": [...]
}
```

---

###  3. Stats API

**GET** `/stats/{bot_id}`

Returns:

* latency
* token usage
* cost estimation
* no-answer count

---

##  How It Works

1. User uploads document
2. Text is chunked into smaller pieces
3. Each chunk is converted into embeddings
4. Stored in ChromaDB
5. User asks a question
6. Top-K relevant chunks retrieved
7. LLM generates answer based only on context

---

##  Security Note

* Do NOT upload `.env` file
* API keys are not required (Ollama runs locally)

---

## ⭐ Conclusion

This project demonstrates:

* Real-world RAG pipeline
* Production-ready backend architecture
* Local LLM deployment (no API cost)
* Scalable and modular design

---

