"""
Builds and queries a local, in-memory Chroma vector store using
HuggingFace sentence-transformer embeddings (fully local, free).
This version is generic — it accepts any list of text documents,
not just PDFs, so it can build a fresh, session-scoped store
from user-uploaded data.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import EMBEDDING_MODEL_NAME

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embeddings


def build_vector_store_from_docs(documents: list[dict]) -> Chroma:
    """
    documents: [{"source": ..., "chunk": ..., ...}, ...]
    Builds an IN-MEMORY store (no persist_directory) — this store
    lives only for the current session, never written to disk.
    """
    if not documents:
        raise ValueError("No documents provided to build the vector store.")

    texts = [d["chunk"] for d in documents]
    metadatas = [{"source": d["source"]} for d in documents]

    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=get_embeddings(),
        metadatas=metadatas,
        # no persist_directory -> stays in memory, cleared when session ends
    )
    return vector_store


def query_vector_store(store: Chroma, query: str, k: int = 5) -> list[dict]:
    """Semantic search over an already-built store."""
    results = store.similarity_search(query, k=k)
    return [{"text": r.page_content, "source": r.metadata.get("source")} for r in results]