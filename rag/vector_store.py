import os
import tempfile
from config.setting import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings

def get_vectorstore(collection_name: str = "research_docs") -> Chroma:
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )

def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

def ingest_documents(file_paths: list[str]) -> dict:
    vectorstore = get_vectorstore("research_docs")
    splitter = get_splitter()
    total_chunks = 0
    processed = []

    for path in file_paths:
        if not os.path.exists(path):
            continue
        loader = PyPDFLoader(path)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        if chunks:
            vectorstore.add_documents(documents=chunks)
            total_chunks += len(chunks)
            processed.append(os.path.basename(path))

    return {"chunks_added": total_chunks, "files_processed": processed}

def ingest_from_streamlit_uploads(uploaded_files) -> dict:
    temp_paths = []
    for uf in uploaded_files:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(uf.read())
        tmp.close()
        temp_paths.append(tmp.name)

    result = ingest_documents(temp_paths)

    for p in temp_paths:
        try:
            os.unlink(p)
        except Exception:
            pass

    return result

def retrieve_context(query: str, collection_name: str = "research_docs", k: int = 5) -> list[str]:
    try:
        vs = get_vectorstore(collection_name)
        results = vs.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
    except Exception:
        return []

def store_research_session(topic: str, research_data: list[str], report: str) -> int:
    splitter = get_splitter()
    vs = get_vectorstore("past_research")

    combined = f"TOPIC: {topic}\n\nREPORT:\n{report}\n\nSOURCES:\n" + "\n---\n".join(research_data[:5])
    from langchain_core.documents import Document
    docs = [Document(page_content=combined, metadata={"topic": topic, "type": "research_session"})]
    chunks = splitter.split_documents(docs)

    if chunks:
        vs.add_documents(documents=chunks)

    return len(chunks)

def get_collection_stats() -> dict:
    stats = {}
    for name in ["research_docs", "past_research"]:
        try:
            vs = get_vectorstore(name)
            collection = vs._collection
            stats[name] = collection.count()
        except Exception:
            stats[name] = 0
    return stats

def clear_collection(collection_name: str):
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        client.delete_collection(collection_name)
    except Exception:
        pass
