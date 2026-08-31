"""Multi-model provider abstraction.

Supports Groq, OpenAI, Anthropic, and Ollama. The active provider is selected
via the ``LLM_PROVIDER`` env var (default ``auto``). When set to ``auto`` the
system tries providers in priority order until one succeeds.
"""
from __future__ import annotations

import os
import logging
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Load .env from workspace root and backend folder
_root_dir = Path(__file__).resolve().parent.parent
load_dotenv(_root_dir / ".env")
load_dotenv()

logger = logging.getLogger(__name__)

PROVIDER_PRIORITY = ["groq", "gemini", "openai", "anthropic", "ollama"]

_KEY_ENV = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "ollama": None,
}

_DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-20b",
    "gemini": "gemini-2.0-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
    "ollama": "llama3.1",
}

_builders: dict[str, Any] = {}


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _has_key(provider: str) -> bool:
    if provider == "gemini":
        return bool(_env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY"))
    key_env = _KEY_ENV.get(provider)
    return key_env is None or bool(_env(key_env))


def _detect() -> str:
    requested = _env("LLM_PROVIDER", "auto").lower()
    if requested in PROVIDER_PRIORITY:
        return requested
    for p in PROVIDER_PRIORITY:
        if _has_key(p):
            return p
    return "ollama"


def get_llm(model: str | None = None, temperature: float = 0.3) -> Any:
    """Return a LangChain chat model using the active provider."""
    provider = _detect()
    if not model:
        model = _env("MODEL_NAME", "") or _DEFAULT_MODELS[provider]

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=temperature, groq_api_key=_env("GROQ_API_KEY"))
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, temperature=temperature, api_key=_env("OPENAI_API_KEY"))
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, temperature=temperature, api_key=_env("ANTHROPIC_API_KEY"))
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, temperature=temperature, base_url=_env("OLLAMA_BASE_URL", "http://localhost:11434"))

    raise RuntimeError(f"Unsupported provider: {provider}")


def get_llm_with_fallback(model: str | None = None, temperature: float = 0.3) -> Any:
    """Try the active provider; on failure fall through to the next."""
    active = _detect()
    to_try = [active] + [p for p in PROVIDER_PRIORITY if p != active]
    last_error: Exception | None = None
    for p in to_try:
        if not _has_key(p):
            continue
        try:
            m = model or _env("MODEL_NAME", "") or _DEFAULT_MODELS[p]
            if p == "groq":
                from langchain_groq import ChatGroq
                return ChatGroq(model=m, temperature=temperature, groq_api_key=_env("GROQ_API_KEY"))
            elif p == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                api_key = _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")
                return ChatGoogleGenerativeAI(model=m, temperature=temperature, google_api_key=api_key)
            elif p == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model=m, temperature=temperature, api_key=_env("OPENAI_API_KEY"))
            elif p == "anthropic":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(model=m, temperature=temperature, api_key=_env("ANTHROPIC_API_KEY"))
            elif p == "ollama":
                from langchain_ollama import ChatOllama
                return ChatOllama(model=m, temperature=temperature, base_url=_env("OLLAMA_BASE_URL", "http://localhost:11434"))
        except Exception as exc:
            last_error = exc
            logger.warning("Provider %s failed: %s", p, exc)
    raise RuntimeError("No LLM provider available. Set at least one API key.") from last_error


def get_provider() -> str:
    """Return the name of the active provider."""
    return _detect()


def provider_info() -> dict:
    """Return a snapshot of available providers and the active one."""
    active = _detect()
    return {
        "active_provider": active,
        "model": _env("MODEL_NAME", "") or _DEFAULT_MODELS.get(active, "unknown"),
        "available": {p: _has_key(p) for p in PROVIDER_PRIORITY},
    }
