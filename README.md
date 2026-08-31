# 🔬 Multi-Agent Research Orchestrator (MARO)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React + Vite](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Multi-Provider LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20Gemini%20%7C%20OpenAI%20%7C%20Anthropic%20%7C%20Ollama-purple.svg)](https://github.com/langchain-ai)
[![ChromaDB RAG](https://img.shields.io/badge/RAG-ChromaDB-green.svg)](https://www.trychroma.com/)
[![FastMCP](https://img.shields.io/badge/protocol-FastMCP-teal.svg)](https://github.com/jlowin/fastmcp)
[![Tests Passing](https://img.shields.io/badge/tests-62%20passed%20%28100%25%29-success.svg)](https://pytest.org/)

An enterprise-grade, autonomous, self-correcting multi-agent AI research pipeline that collaborates to formulate multi-angle queries, cross-examine evidence from the web and vector databases, verify claims against sources with automated revision gates, and synthesize publication-ready Markdown reports with inline citations.

---

## 🌟 Key Features

### 🤖 4 Specialized AI Agents
- **Researcher Agent 🟣**: Generates 3 diverse query angles, searches the web (Tavily API with automatic DuckDuckGo fallback), and retrieves semantic context from ChromaDB RAG.
- **Analyst Agent 🔵**: Synthesizes raw findings into key themes, flags source contradictions, highlights consensus points, and identifies knowledge gaps.
- **Fact-Checker Agent 🟡**: Performs claim-by-claim verification against source citations. Automatically triggers self-correcting revision loops if claims lack proof or contradict evidence.
- **Writer Agent 🟢**: Synthesizes a publication-ready Markdown research report with executive summaries, cited references, and stores session memory in ChromaDB.

### 🔄 Self-Correcting Revision Loop
If the Fact Checker flags unverified claims or critical gaps, the pipeline routes back to the Researcher with targeted feedback for up to 2 revision cycles before final publication.

### 🌐 Dual Full-Stack Frontends
1. **Modern React + Vite SPA (`frontend/`)**:
   - Dynamic real-time LangGraph DAG visualization with pulsing node glow and state transitions.
   - Live Server-Sent Events (SSE) streaming execution console.
   - Interactive citation drawer with domain badges and source links.
   - RAG Knowledge Base Sandbox with drag-and-drop PDF ingestion & similarity scoring.
   - Benchmark Arena with side-by-side metric comparison visualizers.
   - Multi-format report exporter: Markdown (`.md`), HTML, JSON, and BibTeX (`.bib`).
2. **Streamlit Workspace (`app.py`)**:
   - Clean dark workspace with Mermaid workflow diagrams and real-time polling.

### 🧠 Multi-Provider LLM Support & Intelligent Fallbacks
- **Groq**: Ultra-fast LPU inference (`llama-3.3-70b-versatile`)
- **Google Gemini**: Large context reasoning (`gemini-2.0-flash`, `gemini-1.5-pro`)
- **OpenAI**: GPT-4o intelligence
- **Anthropic**: Claude Sonnet analytical writing
- **Ollama**: 100% private, local offline models (`llama3.1`, `mistral`)
- **Web Search**: Tavily Search API with automatic DuckDuckGo fallback (works out of the box with zero setup).

---

## 🚀 Quick Start

### 1. Clone & Environment Setup

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-research-orchestrator.git
cd multi-agent-research-orchestrator

# Create & activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` with your preferred provider key:

```env
# Set provider (auto, groq, gemini, openai, anthropic, ollama)
LLM_PROVIDER=auto

# Provider Keys (at least one):
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional Search Key (DuckDuckGo fallback is active by default):
TAVILY_API_KEY=your_tavily_key
```

### 3. Start the Backend Server

```bash
cd backend
python manage.py migrate
python manage.py runserver
```
The Django REST API runs on `http://127.0.0.1:8000/api`.

### 4. Start the Modern React Frontend

```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser!

*(Alternatively, to run the Streamlit UI: `streamlit run app.py`)*

---

## 📡 REST API Specifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/health/` | No | System health check and provider availability |
| `GET` | `/api/stats/` | No | Platform overview (total runs, sources, RAG chunks, revisions) |
| `POST` | `/api/auth/register/` | No | Register new user account |
| `POST` | `/api/auth/login/` | No | Authenticate user & retrieve Token |
| `POST` | `/api/auth/logout/` | Yes | Invalidate user session token |
| `GET` | `/api/auth/profile/` | Yes | Get authenticated user details |
| `POST` | `/api/research/jobs/` | Yes | Queue autonomous multi-agent research job |
| `GET` | `/api/research/jobs/` | Yes | Paginated list of research runs |
| `GET` | `/api/research/sessions/<id>/` | Yes | Full report, evidence sources, and QA scorecard |
| `DELETE` | `/api/research/sessions/<id>/` | Yes | Delete research session |
| `GET` | `/api/research/sessions/<id>/export/` | No | Export report as `markdown`, `html`, `json`, or `bibtex` |
| `POST` | `/api/research/stream/` | Yes | Real-time Server-Sent Events (SSE) agent stream |
| `GET/POST` | `/api/research/<id>/tags/` | Yes | Get or add organizational tags |
| `POST` | `/api/research/documents/` | Yes | Ingest PDFs into ChromaDB vector knowledge base |
| `GET` | `/api/rag/stats/` | No | ChromaDB collection chunk counts & model info |
| `POST` | `/api/rag/search/` | No | Semantic vector similarity search sandbox |
| `POST` | `/api/research/benchmark/` | No | Run single vs multi-agent empirical benchmark |
| `GET` | `/api/benchmark/history/` | No | Historical benchmark evaluations |

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Full-Stack Client Layer                        │
│  ┌─────────────────────────────────────┐  ┌──────────────────────────┐  │
│  │   React + Vite Modern SPA Frontend  │  │   Streamlit Workspace    │  │
│  │   - Live Agent DAG Visualizer       │  │   - Quick Dashboard      │  │
│  │   - SSE Streaming Terminal          │  │   - Multi-tab View       │  │
│  │   - RAG Knowledge Sandbox           │  │   - PDF Ingestion        │  │
│  │   - Benchmark Arena & Analytics     │  │                          │  │
│  │   - Multi-Format Report Exporter    │  │                          │  │
│  └──────────────────┬──────────────────┘  └─────────────┬────────────┘  │
└─────────────────────┼───────────────────────────────────┼───────────────┘
                      │ REST API + SSE Streaming          │
┌─────────────────────▼───────────────────────────────────▼───────────────┐
│                    Django REST Framework Backend                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ Auth & Users │ │ Research Jobs│ │ SSE Streaming│ │ RAG & Stats    │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────────┘  │
└─────────────────────┬───────────────────────────────────┬───────────────┘
                      │                                   │
┌─────────────────────▼─────────────┐       ┌─────────────▼───────────────┐
│    LangGraph Multi-Agent Engine   │       │     ChromaDB Vector Store   │
│  ┌───────────┐     ┌───────────┐  │       │  - Research Papers (PDFs)   │
│  │Researcher ├────►│  Analyst  │  │       │  - Past Session Memory      │
│  └─────▲─────┘     └─────┬─────┘  │       │  - Semantic Similarity RAG  │
│        │                 │        │       └─────────────────────────────┘
│        │ (Revision Loop) │        │
│  ┌─────┴─────┐     ┌─────▼─────┐  │
│  │FactChecker│◄────┤  Writer   │  │
│  └───────────┘     └───────────┘  │
└─────────────────────┬─────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────────────┐
│                   Multi-Provider LLM & Search Layer                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────┐  │
│  │  Groq   │ │ Gemini  │ │ OpenAI  │ │Anthropic │ │  Ollama  │ │Fast │  │
│  │(Llama3) │ │ (2.0/1.5│ │ (GPT-4o)│ │ (Claude) │ │ (Local)  │ │ MCP │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────┘ └──────────┘ └─────┘  │
│  Web Search: Tavily API  +  DuckDuckGo / Open Search Fallback           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Comprehensive Automated Testing

Execute the complete 62-test verification suite:

```bash
cd backend
python -m pytest -v
```

```
============================== 62 passed in 18.4s ==============================
```

---

## 🔌 FastMCP Server (Claude Desktop / Cursor IDE)

Integrate MARO tools directly into Claude Desktop or Cursor:

```bash
python mcp_server.py
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research-orchestrator": {
      "command": "python",
      "args": ["/path/to/multi-agent-research-orchestrator/mcp_server.py"],
      "env": {
        "GROQ_API_KEY": "your_key",
        "GEMINI_API_KEY": "your_key",
        "TAVILY_API_KEY": "your_key"
      }
    }
  }
}
```

---

## 📜 License

MIT License © 2026 Multi-Agent Research Orchestrator Team
