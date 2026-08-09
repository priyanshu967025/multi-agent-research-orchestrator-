"""
📚 RAG Vector Store Manager
────────────────────────────
Handles PDF ingestion, chunking, embedding, and retrieval using
ChromaDB (persistent) + HuggingFace embeddings (free, local).

Three core functions:
1. ingest_documents() — Upload PDFs → chunk → embed → store in ChromaDB
2. retrieve_context() — Semantic search over stored documents
3. store_research_session() — Save past research results for memory
"""

import os
import hashlib
from typing import Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# ── Embedding Model (singleton — loaded once, reused) ─────────────────
_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the HuggingFace embedding model (lazy singleton)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


# ── Vector Store Access ───────────────────────────────────────────────
def get_vectorstore(collection_name: str = "research_docs") -> Chroma:
    """
    Get or create a persistent ChromaDB vector store.

    Args:
        collection_name: Name of the ChromaDB collection.
                         "research_docs" for uploaded PDFs,
                         "past_research" for session memory.
    """
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


# ── PDF Ingestion ─────────────────────────────────────────────────────
def ingest_documents(file_paths: list[str]) -> dict:
    """
    Load PDFs, chunk them, embed, and store in ChromaDB.

    Args:
        file_paths: List of absolute paths to PDF files.

    Returns:
        dict with 'chunks_added' count and 'files_processed' list.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks = []
    files_processed = []

    for file_path in file_paths:
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            # Add file metadata to each document
            file_name = os.path.basename(file_path)
            for doc in docs:
                doc.metadata["source_file"] = file_name

            # Split into chunks
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)
            files_processed.append(file_name)
        except Exception as e:
            files_processed.append(f"{os.path.basename(file_path)} (ERROR: {e})")

    if all_chunks:
        # Generate unique IDs based on content hash to avoid duplicates
        ids = []
        for chunk in all_chunks:
            content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()
            ids.append(content_hash)

        vectorstore = get_vectorstore("research_docs")
        vectorstore.add_documents(documents=all_chunks, ids=ids)

    return {
        "chunks_added": len(all_chunks),
        "files_processed": files_processed,
    }


def ingest_from_streamlit_uploads(uploaded_files) -> dict:
    """
    Process Streamlit uploaded files and ingest into ChromaDB.

    Args:
        uploaded_files: List of Streamlit UploadedFile objects.

    Returns:
        dict with ingestion results.
    """
    import tempfile

    temp_paths = []
    try:
        for uploaded_file in uploaded_files:
            # Write to temp file (PyPDFLoader needs file path)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf", prefix=f"{uploaded_file.name}_"
            ) as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_paths.append(tmp.name)

        result = ingest_documents(temp_paths)
    finally:
        # Clean up temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except OSError:
                pass

    return result


# ── Semantic Retrieval ────────────────────────────────────────────────
def retrieve_context(
    query: str,
    collection_name: str = "research_docs",
    k: int = 5,
) -> list[str]:
    """
    Retrieve the most relevant chunks from ChromaDB for a given query.

    Args:
        query: The search query.
        collection_name: Which collection to search.
        k: Number of results to return.

    Returns:
        List of relevant text chunks with source metadata.
    """
    vectorstore = get_vectorstore(collection_name)

    # Check if collection has documents
    try:
        results = vectorstore.similarity_search(query, k=k)
    except Exception:
        return []

    if not results:
        return []

    formatted = []
    for doc in results:
        source = doc.metadata.get("source_file", doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page", "")
        source_info = f"[RAG Source: {source}"
        if page != "":
            source_info += f", Page {int(page) + 1}"
        source_info += "]"
        formatted.append(f"{source_info}\n{doc.page_content}")

    return formatted


# ── Research Session Memory ──────────────────────────────────────────
def store_research_session(topic: str, research_data: list[str], report: str) -> int:
    """
    Store a completed research session's data and report for future retrieval.
    This creates persistent memory — future research can reference past sessions.

    Args:
        topic: The research topic.
        research_data: Raw research results from the session.
        report: The final generated report.

    Returns:
        Number of chunks stored.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # Create documents from the report and research data
    documents = []

    # Store the final report
    if report:
        report_doc = Document(
            page_content=report,
            metadata={"source": f"Past Research: {topic}", "type": "report"},
        )
        documents.append(report_doc)

    # Store key research data points
    for i, data in enumerate(research_data[:10]):  # Cap at 10 to avoid bloat
        doc = Document(
            page_content=data,
            metadata={
                "source": f"Past Research: {topic}",
                "type": "research_data",
                "index": i,
            },
        )
        documents.append(doc)

    if documents:
        chunks = text_splitter.split_documents(documents)
        ids = [
            hashlib.md5(f"{topic}_{i}_{c.page_content[:50]}".encode()).hexdigest()
            for i, c in enumerate(chunks)
        ]

        vectorstore = get_vectorstore("past_research")
        vectorstore.add_documents(documents=chunks, ids=ids)
        return len(chunks)

    return 0


# ── Utility Functions ─────────────────────────────────────────────────
def get_collection_stats() -> dict:
    """Get document counts for all collections."""
    stats = {}
    for name in ["research_docs", "past_research"]:
        try:
            vs = get_vectorstore(name)
            # ChromaDB collection count
            collection = vs._collection
            stats[name] = collection.count()
        except Exception:
            stats[name] = 0
    return stats


def clear_collection(collection_name: str = "research_docs") -> bool:
    """Clear all documents from a collection."""
    try:
        vs = get_vectorstore(collection_name)
        collection = vs._collection
        # Get all IDs and delete
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)
        return True
    except Exception:
        return False
