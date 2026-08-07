import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key)
    if not value:
        try:
            import streamlit as st
            if key in st.secrets:
                value = str(st.secrets[key])
        except Exception:
            pass
    if not value:
        value = default
    if required and not value:
        raise ValueError(f"Missing: {key}. Please set it in .env file or Streamlit Secrets.")
    return value or ""

def get_groq_api_key() -> str:
    key = get_env_var("GROQ_API_KEY", required=False)
    if key:
        os.environ["GROQ_API_KEY"] = key
    return key

def get_tavily_api_key() -> str:
    key = get_env_var("TAVILY_API_KEY", required=False)
    if key:
        os.environ["TAVILY_API_KEY"] = key
    return key

GROQ_API_KEY = get_groq_api_key()
TAVILY_API_KEY = get_tavily_api_key()

MODEL_NAME = get_env_var("MODEL_NAME", default="llama-3.3-70b-versatile")
MAX_SEARCH_RESULTS = int(get_env_var("MAX_SEARCH_RESULTS", default="5"))
MAX_REVISIONS = int(get_env_var("MAX_REVISIONS", default="2"))

CHROMA_PERSIST_DIR = get_env_var("CHROMA_PERSIST_DIR", default="./chroma_db")
EMBEDDING_MODEL = get_env_var("EMBEDDING_MODEL", default="sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(get_env_var("CHUNK_SIZE", default="1000"))
CHUNK_OVERLAP = int(get_env_var("CHUNK_OVERLAP", default="200"))
