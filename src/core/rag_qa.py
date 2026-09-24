"""
Orchestrates the RAG pipeline for user-uploaded CSVs:
ingest -> embed -> store -> retrieve -> generate.
"""

from src.ingestion.csv_loader import csv_to_documents
from src.ingestion.vector_store import build_vector_store_from_docs, query_vector_store
from src.llm.groq_client import call_llm
from src.llm.prompts import RAG_QA_SYSTEM_PROMPT, build_rag_qa_prompt


def ingest_csv(uploaded_file):
    """Step 1-2: CSV -> documents -> embedded vector store."""
    documents = csv_to_documents(uploaded_file)
    store = build_vector_store_from_docs(documents)
    return store, len(documents)


def ask_question(store, question: str, k: int = 5) -> dict:
    """Step 3-4: retrieve relevant rows, then generate a grounded answer."""
    retrieved = query_vector_store(store, question, k=k)

    if not retrieved:
        return {"answer": "No relevant data found for that question.", "sources": []}

    chunks = [r["text"] for r in retrieved]
    prompt = build_rag_qa_prompt(question, chunks)
    answer = call_llm(RAG_QA_SYSTEM_PROMPT, prompt)

    return {"answer": answer.strip(), "sources": chunks}