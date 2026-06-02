import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from backend.config import (
    DOCS_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBED_MODEL,
    GENERATIVE_MODEL,
)
from backend.retrieval_engine import build_context_pack, _get_collection
from backend.search import search_vault, format_results
from backend.summarise import compress_context_pack
from backend.ingest import (
    load_manifest,
    update_manifest,
    remove_from_manifest,
    ingest_file,
)


app = FastAPI(
    title="Grant Vault API",
    version="1.0.0",
    description="Local-first retrieval API for the grant writing vault.",
)

UPLOADS_DIR = DOCS_DIR / "uploads"


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
    status = {
        "status": "ok",
        "models": {"embed": EMBED_MODEL, "generative": GENERATIVE_MODEL},
    }

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
            return {"total_chunks": 0, "grant_schemes": [], "document_types": [], "source_types": [], "sources": []}

        all_meta = collection.get(include=["metadatas"])["metadatas"]

        return {
            "total_chunks": total,
            "grant_schemes": sorted(set(m.get("grant_scheme", "unknown") for m in all_meta)),
            "document_types": sorted(set(m.get("document_type", "unknown") for m in all_meta)),
            "source_types": sorted(set(m.get("source_type", "unknown") for m in all_meta)),
            "sources": sorted(set(m.get("source", "unknown") for m in all_meta)),
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
        return {"query": req.query, "result_count": len(results), "results": results}

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


# --- Compressed brief (retrieval + qwen2.5:3b, ~2 min) ---

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


# --- Get a specific chunk by source and index ---

@app.get("/chunk")
def get_chunk(source: str, index: int):
    """
    Retrieve a specific chunk by source filename and chunk index.
    Used by the verification agent to check exact source text for a cited claim.
    Example: GET /chunk?source=my-grant.pdf&index=5
    """
    try:
        collection = _get_collection()
        results = collection.get(
            where={"$and": [{"source": source}, {"chunk": index}]},
            include=["documents", "metadatas"],
        )
        if not results["ids"]:
            raise HTTPException(
                status_code=404,
                detail=f"Chunk {index} from '{source}' not found in vault",
            )
        return {
            "id": results["ids"][0],
            "source": source,
            "chunk": index,
            "content": results["documents"][0],
            "metadata": results["metadatas"][0],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Ingest a new document ---

@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    grant_scheme: str = Form("unknown"),
    quality_signal: str = Form("unknown"),
    source_type: str = Form("unknown"),
    sensitivity: str = Form("internal"),
):
    allowed_types = {".pdf", ".docx", ".txt", ".md"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' not supported. Allowed: {allowed_types}",
        )

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOADS_DIR / file.filename

    content = await file.read()
    file_path.write_bytes(content)

    relative = file_path.relative_to(DOCS_DIR).as_posix()
    entry = {
        "grant_scheme": grant_scheme,
        "quality_signal": quality_signal,
        "source_type": source_type,
        "sensitivity": sensitivity,
    }
    update_manifest(relative, entry)

    try:
        collection = _get_collection()
        manifest = load_manifest()
        result = ingest_file(file_path, collection, manifest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "filename": file.filename,
        "relative_path": relative,
        "metadata": entry,
        **result,
    }


# --- Remove a document ---

@app.delete("/ingest/{filename}")
def remove_document(filename: str, delete_file: bool = False):
    try:
        collection = _get_collection()
        existing = collection.get(where={"source": filename}, include=[])
        ids = existing["ids"]

        if not ids:
            raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")

        collection.delete(ids=ids)

        removed_key = remove_from_manifest(filename)

        file_deleted = False
        if delete_file:
            for match in DOCS_DIR.rglob(filename):
                match.unlink()
                file_deleted = True
                break

        return {
            "filename": filename,
            "chunks_removed": len(ids),
            "manifest_key_removed": removed_key,
            "file_deleted": file_deleted,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
