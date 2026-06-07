import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "unofficial-guide"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 5

# --- Documents ---
DOCS_PATH = "./documents"

# --- Chunking ---
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
MIN_CHUNK_LENGTH = 50
