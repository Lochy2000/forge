from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DOCS_DIR = ROOT_DIR / "docs"
CHROMA_DIR = ROOT_DIR / "chroma_db"
OUTPUT_DIR = ROOT_DIR / "output"
MANIFEST_PATH = DOCS_DIR / "manifest.json"

COLLECTION_NAME = "grant_vault"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

EMBED_MODEL = "nomic-embed-text"
GENERATIVE_MODEL = "qwen2.5:3b"