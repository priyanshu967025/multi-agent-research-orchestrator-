# 📡 Multi-Agent Research Orchestrator — REST API Specification

Base URL: `http://localhost:8000/api` or `https://your-domain.com/api`

---

## 1. Authentication Endpoints

### 🔑 User Registration
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "researcher_alex",
  "email": "alex@example.com",
  "password": "SecurePassword123"
}
```
**Response (201 Created):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "researcher_alex",
    "email": "alex@example.com"
  }
}
```

### 🔓 User Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "researcher_alex",
  "password": "SecurePassword123"
}
```
**Response (200 OK):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "researcher_alex"
  }
}
```

---

## 2. Research & Live Streaming Endpoints

### ⚡ Live Server-Sent Events (SSE) Execution
```http
POST /api/research/stream/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
  "topic": "Quantum error correction thresholds in surface codes"
}
```
**Response (200 OK — text/event-stream):**
```text
data: {"stage": "queued", "message": "Starting research pipeline..."}

data: {"stage": "researcher", "message": "Formulated 3 search angles: Quantum error correction, Surface code thresholds, Physical qubit overhead"}

data: {"stage": "analyst", "message": "Extracted 4 consensus themes and 2 contradiction points across 12 sources."}

data: {"stage": "fact_checker", "message": "Audit complete: 8/8 claims verified (Quality score: 9.2/10)."}

data: {"stage": "writer", "message": "Synthesized 2,800-word cited report with 8 references."}

data: {"stage": "completed", "message": "Done", "session_id": 42}

data: [DONE]
```

### 📥 Export Research Report
```http
GET /api/research/sessions/42/export/?format=markdown
```
**Formats supported**: `markdown`, `html`, `bibtex`, `json`.

---

## 3. RAG Knowledge & Vector Sandbox

### 📄 Upload PDFs into ChromaDB
```http
POST /api/research/documents/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: multipart/form-data

files: [paper1.pdf, paper2.pdf]
```
**Response (201 Created):**
```json
{
  "status": "success",
  "chunks_added": 84,
  "files_processed": 2
}
```

### 📊 ChromaDB Collection Statistics
```http
GET /api/rag/stats/
```
**Response (200 OK):**
```json
{
  "collections": {
    "research_docs": 128,
    "past_research": 45
  },
  "total_indexed_documents": 173,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```
