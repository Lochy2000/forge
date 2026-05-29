import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    OLLAMA_EMBED_URL,
    OLLAMA_CHAT_URL,
    EMBED_MODEL,
    GENERATIVE_MODEL,
)
from backend.retrieval_engine import build_context_pack, _get_collection
from backend.search import search_vault, format_results
from backend.summarise import compress_context_pack


app = FastAPI(
    title="Grant Vault API",
    version="1.0.0",
    description="Local-first retrieval API for the grant writing vault.",
)


# --- Request models ---

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    where_filter: dict | None = None


class ContextPackRequest(BaseModel):
    task: str
    grant_scheme: str | None = None
    section: str | None = None


# --- Health ---

@app.get("/health")
def health():
    status = {"status": "ok", "models": {"embed": EMBED_MODEL, "generative": GENERATIVE_MODEL}}

    try:
        r = requests.get("http://localhost:11434", timeout=3)
        status["ollama"] = "ok" if r.status_code == 200 else "unreachable"
    except Exception:
        status["ollama"] = "unreachable"

    try:
        collection = _get_collection()
        status["vault_chunks"] = collection.count()
    except Exception:
        status["vault_chunks"] = "unavailable"

    return status


# --- Stats ---

@app.get("/stats")
def stats():
    try:
        collection = _get_collection()
        total = collection.count()

        if total == 0:
            return {"total_chunks": 0, "grant_schemes": [], "document_types": [], "source_types": []}

        all_meta = collection.get(include=["metadatas"])["metadatas"]

        grant_schemes = sorted(set(m.get("grant_scheme", "unknown") for m in all_meta))
        document_types = sorted(set(m.get("document_type", "unknown") for m in all_meta))
        source_types = sorted(set(m.get("source_type", "unknown") for m in all_meta))
        sources = sorted(set(m.get("source", "unknown") for m in all_meta))

        return {
            "total_chunks": total,
            "grant_schemes": grant_schemes,
            "document_types": document_types,
            "source_types": source_types,
            "sources": sources,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Search ---

@app.post("/search")
def search(req: SearchRequest):
    try:
        raw = search_vault(
            query=req.query,
            n_results=req.n_results,
            where_filter=req.where_filter,
        )
        results = format_results(raw)
        return {"query": req.query, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Context pack (retrieval only, fast) ---

@app.post("/context-pack")
def context_pack(req: ContextPackRequest):
    try:
        pack = build_context_pack(
            task=req.task,
            grant_scheme=req.grant_scheme,
            section=req.section,
        )
        total = sum(len(pack[k]) for k in ["content", "style_examples", "funder_requirements", "evidence"])
        return {"total_chunks": total, **pack}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Compressed brief (retrieval + qwen2.5:3b, slow ~2 min) ---

@app.post("/brief")
def brief(req: ContextPackRequest):
    """
    Retrieves and compresses a context pack into a structured brief.
    Calls qwen2.5:3b locally — expect ~2 minutes response time.
    Set client timeout to at least 300 seconds.
    """
    try:
        pack = build_context_pack(
            task=req.task,
            grant_scheme=req.grant_scheme,
            section=req.section,
        )
        compressed = compress_context_pack(pack)
        return compressed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
