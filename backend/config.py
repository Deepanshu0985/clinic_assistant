import os

# --- Model Configuration ---
LLM_MODEL = "mistral:7b" 
# LLM_MODEL = "llama3:8b" 
EMBEDDING_MODEL = "nomic-embed-text"

# --- RAG / Vector DB Configuration ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")