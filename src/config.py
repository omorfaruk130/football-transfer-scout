import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PLAYERS_CSV_PATH = DATA_DIR / "players_fc24.csv"
RAW_PDFS_DIR = DATA_DIR / "raw_pdfs"
CHROMA_PERSIST_DIR = str(DATA_DIR / "chroma_db")

# --- Groq / LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME = "openai/gpt-oss-120b"
LLM_TEMPERATURE = 0.2  # low temp: we want consistent structured output, not creativity

# --- Embeddings ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- Text splitting (for PDF scouting reports) ---
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Add it to your .env file: GROQ_API_KEY=your_key_here"
    )