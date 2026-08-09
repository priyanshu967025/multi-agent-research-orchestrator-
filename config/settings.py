"""
Centralized configuration — loads .env and exposes settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_env_var(key: str, default: str | None = None, required: bool = False) -> str:
    """Get an environment variable with optional default and requirement check."""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(
            f"Missing required environment variable: {key}\n"
            f"Please set it in your .env file. See .env.example for reference."
        )
    return value or ""


# ── API Keys ──────────────────────────────────────────────────────────
GROQ_API_KEY = get_env_var("GROQ_API_KEY", default="gsk-placeholder", required=False)
TAVILY_API_KEY = get_env_var("TAVILY_API_KEY", default="tvly-placeholder", required=False)

# ── Model Configuration ──────────────────────────────────────────────
MODEL_NAME = get_env_var("MODEL_NAME", default="llama-3.3-70b-versatile")
MAX_SEARCH_RESULTS = int(get_env_var("MAX_SEARCH_RESULTS", default="5"))
MAX_REVISIONS = int(get_env_var("MAX_REVISIONS", default="2"))

# ── RAG Configuration ────────────────────────────────────────────────
CHROMA_PERSIST_DIR = get_env_var("CHROMA_PERSIST_DIR", default="./chroma_db")
EMBEDDING_MODEL = get_env_var("EMBEDDING_MODEL", default="sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(get_env_var("CHUNK_SIZE", default="1000"))
CHUNK_OVERLAP = int(get_env_var("CHUNK_OVERLAP", default="200"))

# ── Set keys in environment (required by LangChain integrations) ─────
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY



