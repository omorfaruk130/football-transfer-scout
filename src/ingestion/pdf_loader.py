"""
Extracts and chunks text from scouting report PDFs (data/raw_pdfs/)
for ingestion into the vector store.
"""

import pdfplumber
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import RAW_PDFS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a single PDF file."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def load_all_pdfs() -> list[dict]:
    """
    Read every PDF in data/raw_pdfs/ and return raw docs as
    [{"source": filename, "text": full_text}, ...]
    """
    if not RAW_PDFS_DIR.exists():
        return []

    docs = []
    for pdf_file in RAW_PDFS_DIR.glob("*.pdf"):
        text = extract_text_from_pdf(pdf_file)
        if text.strip():
            docs.append({"source": pdf_file.name, "text": text})

    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    """
    Split each document's text into overlapping chunks.
    Returns [{"source": filename, "chunk": text, "chunk_id": int}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunked = []
    for doc in docs:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked.append(
                {"source": doc["source"], "chunk": chunk, "chunk_id": i}
            )

    return chunked