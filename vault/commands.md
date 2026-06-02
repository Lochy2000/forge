# Grant Vault — Commands

## Start the vault (recommended)

```powershell
cd vault
.\start.ps1
```

Handles Ollama, model checks, venv activation, and API startup in one command.

---

## Manual startup (if needed)

```powershell
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Vault API (from vault/ with venv active)
.\venv\Scripts\Activate.ps1
uvicorn backend.api:app --port 8100
```

---

## First-time setup

```powershell
# Pull required models
ollama pull nomic-embed-text
ollama pull qwen2.5:3b

# Install Python dependencies
pip install -r requirements.txt

# Ingest documents
python -m backend.ingest
```

---

## Testing

```powershell
# All retrieval tests (needs Ollama + vault ingested)
python -m tests.test_retrieval

# Summarisation tests (needs Ollama only)
python -m tests.test_summarise

# API tests (needs vault API running on port 8100)
python -m tests.test_api
```

---

## Vault management

```powershell
# Re-ingest after adding new documents
python -m backend.ingest

# Wipe and re-ingest from scratch
python -m backend.reset_db
python -m backend.ingest

# Interactive search
python -m backend.search

# Build a retrieval context pack (with optional compression)
python -m backend.retrieval_context
```

---

## API endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | Check vault and Ollama status |
| /stats | GET | What is loaded in the vault |
| /search | POST | Semantic search |
| /context-pack | POST | Intent-based retrieval |
| /brief | POST | Retrieval + compression (~2 min) |
| /chunk | GET | Get specific chunk by source + index |
| /ingest | POST | Upload new document |
| /ingest/{filename} | DELETE | Remove document |

Interactive docs: http://localhost:8100/docs
