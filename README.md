# MementoManager: Local LLM Memory API

A high-performance, locally-hosted memory management module designed for use with LLM applications (chatbots, writing engines, agents). It combines semantic vector search (RAG) with a knowledge graph (GraphRAG) to provide deep, structured context retrieval.

## 🚀 Key Features
- **Hybrid Storage:** Uses **ChromaDB** for vector embeddings and **NetworkX** for entity-relationship mapping.
- **Auto-Extraction:** Automatically parses raw chat logs into structured facts and relationships using your local LLM.
- **RAG + GraphRAG:** Retrieval combines semantic similarity with graph-based neighbor traversal.
- **Optimized for RTX 3090:** Pre-configured for `llama-cpp-python` with CUDA acceleration.

---

## 🛠️ Setup & Installation

### 1. Requirements
- Python 3.10+
- NVIDIA GPU (RTX 3090 recommended) with CUDA drivers installed.
- CMake (for building llama-cpp-python).

### 2. Environment Setup
The setup process creates a virtual environment and compiles `llama-cpp-python` with CUDA support.
```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=86" .venv/bin/python -m pip install llama-cpp-python
.venv/bin/python -m pip install -r requirements.txt
```

### 3. Model Configuration
Place your GGUF model in the `models/` directory. The default configuration is set for:
`models/Magistral-Small-2509-Q4_K_M.gguf`

Edit the `.env` file to change the model path or GPU settings.

---

## 🏃 Scripts

### Start the API
Runs the FastAPI server on port **7087**.
```bash
./start_api.sh
```

### Run Tests
A comprehensive test suite for storage, API logic, and live LLM performance.
- `./run_tests.sh fast`: Run storage and mocked API tests (No GPU required).
- `./run_tests.sh live`: Run end-to-end tests using the actual LLM (Requires GPU).
- `./run_tests.sh all`: Run everything.

---

## 📡 API Endpoints

### 1. `POST /store/chat`
Sends raw text to the LLM to extract facts and relationships automatically.
- **Body:** `{ "text": "I live in London with my cat, Luna." }`
- **Result:** Extracts "User lives in London" (Fact) and "User -> owns -> Luna" (Relationship).

### 2. `POST /store/targeted`
Manually inject a specific piece of data.
- **Fact Body:** `{ "content": "The password to the safe is 1234", "type": "fact" }`
- **Relationship Body:** `{ "content": "Ty is married to Karen", "type": "relationship", "subject": "Ty", "relation": "married_to", "object": "Karen" }`

### 3. `POST /retrieve/all` (Context Search)
Returns a "brain dump" of everything semantically or relationally relevant to the query.
- **Body:** `{ "query": "What do you know about Ty's family?" }`

### 4. `POST /retrieve/targeted` (Answer Mode)
Uses the RAG pipeline to provide a concise, human-like answer to a specific question.
- **Body:** `{ "query": "What is Ty's wife's name?" }`
- **Response:** `{ "answer": "Her name is Karen." }`

---

## 🏗️ Architecture
- **Vector Brain (ChromaDB):** Stores text "chunks" and facts. High-speed semantic lookup.
- **Relational Brain (NetworkX):** Stores an entity-relationship graph (Subject -> Relation -> Object). Allows the API to "connect the dots" between people and concepts.
- **Extraction Layer:** Uses a custom prompt to turn unstructured chat data into clean JSON for storage.
- **Synthesis Layer:** Combines retrieved context into a final prompt for the LLM to generate natural responses.
