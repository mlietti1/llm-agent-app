import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
VECTOR_SIZE = 384  # must match the embedding model's output size
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.55"))
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
EMBED_CACHE_DIR = os.getenv("EMBED_CACHE_DIR") or None
LLM_FALLBACK_MODEL = os.getenv(
    "LLM_FALLBACK_MODEL", "gemini-flash-lite-latest")
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "4"))
