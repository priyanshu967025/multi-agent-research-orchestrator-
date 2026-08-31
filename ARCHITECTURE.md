# 🏛️ Multi-Agent Research Orchestrator — Architectural Blueprint

This document provides a deep technical specification of the Multi-Agent Research Orchestrator (MARO) architecture, state machine semantics, vector retrieval pipelines, and verification gate algorithms.

---

## 1. Executive Architecture Overview

```
[ Client Layer: React 18 + Three.js 3D WebGL / Streamlit ]
                         │
                         ▼ (HTTP REST + Server-Sent Events SSE)
[ API Gateway: Django REST Framework + Token Auth + WhiteNoise ]
                         │
                         ├────────────────────────────────────────┐
                         ▼                                        ▼
           [ LangGraph Orchestration Engine ]           [ ChromaDB Vector Space ]
                         │                                 • research_docs (PDFs)
                         ▼                                 • past_research (Memory)
        ┌──────────────────────────────────┐
        │  01. Researcher Agent            │
        │      • 3 Angle Search (Tavily/DDG│
        │      • ChromaDB Dense Retrieval  │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  02. Analyst Agent               │
        │      • Theme & Pattern Synthesis │
        │      • Contradiction Matrix      │
        └────────────────┬─────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  03. Fact-Checker QA Gate        │
        │      • Claim-by-Claim Audit      │
        │      • Confidence Scoring (1-10) │
        └────────┬─────────────────────────┘
                 │
        ┌────────┴────────┐
        │ Quality < 5.0?  │──── (Yes: Re-route Loop #N) ────► [ Back to Researcher ]
        │ >30% Unverified?│
        └────────┬────────┘
                 │ (Pass)
                 ▼
        ┌──────────────────────────────────┐
        │  04. Writer Agent                │
        │      • Cited Markdown Synthesis  │
        │      • Vector Memory Persistence │
        └──────────────────────────────────┘
```

---

## 2. LangGraph State Schema & Reduction Semantics

The core execution graph is parameterized by a typed state dictionary (`ResearchState`):

```python
from typing import TypedDict, Annotated, List
import operator

class ResearchState(TypedDict):
    topic: str
    research_data: Annotated[List[str], operator.add]
    rag_context: Annotated[List[str], operator.add]
    analysis: str
    fact_check_result: str
    fact_check_passed: bool
    revision_count: int
    final_report: str
    messages: Annotated[List[str], operator.add]
    current_agent: str
```

### State Reducers:
- **`operator.add` for `research_data` & `rag_context`**: Ensures that subsequent search cycles accumulate new evidence without overwriting existing source data.
- **`operator.add` for `messages`**: Maintains a chronological audit trail of agent transitions for SSE streaming clients.

---

## 3. The 4-Agent Pipeline Breakdown

### 🔬 Node 1: Researcher (`agents/researcher.py`)
- **Query Strategy**: Uses LLM to formulate 3 orthogonal search queries (technical definition, real-world applications, criticisms/trade-offs).
- **Hybrid Retrieval**:
  - Web Search: **Tavily API** with automatic **DuckDuckGo** (`duckduckgo_search`) fallback.
  - Local RAG: Semantic vector search against ChromaDB (`k=5` chunks from uploaded PDFs, `k=3` chunks from past session memory).

### 📊 Node 2: Analyst (`agents/analyst.py`)
- **Theme Synthesis**: Extracts 3–5 foundational pillars from compiled search evidence.
- **Contradiction Matrix**: Cross-examines conflicting viewpoints and rates source credibility.
- **Knowledge Gaps**: Formulates unanswered questions and limits of current consensus.

### 🛡️ Node 3: Fact-Checker QA Gate (`agents/fact_checker.py`)
- **Claim Audit**: Parses the draft analysis and verifies every individual factual assertion against source snippets.
- **Verdict Scoring**:
  - `VERIFIED`: Directly substantiated by cited source text.
  - `PARTIALLY_VERIFIED`: Inferred with moderate confidence.
  - `UNVERIFIED`: Lacks direct empirical support.
  - `CONTRADICTED`: Conflicted by trusted source material.
- **Self-Correction Trigger**: If quality score $< 5.0$ or $> 30\%$ claims are unverified, graph conditional edge returns to Researcher (up to `MAX_REVISIONS = 2`).

### ✍️ Node 4: Writer (`agents/writer.py`)
- **Publication Synthesizer**: Generates executive summaries, table of contents, technical deep-dives, and numbered IEEE/APA style inline references (`[1]`, `[2]`).
- **Memory Storage**: Automatically embeds the completed report into ChromaDB (`past_research` collection) so future queries can recall past findings.

---

## 4. Dual-Collection ChromaDB Vector Architecture

```
ChromaDB Persistent Storage (./rag/chroma_db)
├── Collection 1: "research_docs"
│   └── Ingested user PDFs (SentenceTransformers: all-MiniLM-L6-v2)
│       └── Chunk Size: 1000 chars | Overlap: 200 chars
│
└── Collection 2: "past_research"
    └── Historical verified reports and synthetic research memory
        └── Chunk Size: 1000 chars | Overlap: 200 chars
```

---

## 5. Multi-Provider LLM Failover Matrix

The provider router ([`config/providers.py`](file:///d:/GEN%20AI%20PROJECT%20CV/Multi%20Agent%20Research%20Orchestrator/config/providers.py)) detects available credentials and provides automated failover:

$$\text{Priority}: \text{Groq} \longrightarrow \text{Gemini} \longrightarrow \text{OpenAI} \longrightarrow \text{Anthropic} \longrightarrow \text{Ollama}$$

- **Lazy Package Loading**: Imports provider dependencies on-demand to prevent missing-package runtime crashes.
- **Token Protection**: Proactive context budgeting ensures prompts stay comfortably beneath rate-limit tiers.
