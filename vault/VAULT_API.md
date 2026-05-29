# Grant Vault — API Contract

**Base URL:** `http://localhost:8100`

**Start the vault:**
```powershell
ollama serve                                        # terminal 1
uvicorn backend.api:app --port 8100                 # terminal 2 (vault/ dir, venv active)
```

---

## Endpoints

### GET /health — instant
Check vault and Ollama are up before making any other call.
```json
// response
{ "status": "ok", "ollama": "ok", "vault_chunks": 82, "models": { "embed": "nomic-embed-text", "generative": "qwen2.5:3b" } }
```
Abort if `ollama` is not `"ok"` or `vault_chunks` is 0.

---

### GET /stats — instant
What is currently loaded in the vault.
```json
// response
{ "total_chunks": 82, "grant_schemes": ["innovate_uk", "communities_fund"], "document_types": ["grant_application", "grant_guidance"], "sources": ["file.pdf"] }
```

---

### POST /search — fast (~2s)
Raw semantic search. Supports metadata filtering.
```json
// request
{ "query": "innovation beyond state of the art", "n_results": 5, "where_filter": { "is_funder_requirement": "true" } }

// response
{ "query": "...", "result_count": 3, "results": [ { "content": "...", "source": "file.pdf", "chunk": 1, "distance": 265.9, "grant_scheme": "innovate_uk", "is_style_example": "true", "is_funder_requirement": "false", "is_evidence": "true" } ] }
```
Note: boolean metadata fields are stored as strings — use `"true"` / `"false"` in filters, not booleans.

---

### POST /context-pack — fast (~5s)
Intent-based retrieval grouped by type. Primary endpoint for writing agents.
```json
// request
{ "task": "write the innovation section", "grant_scheme": "innovate_uk", "section": "innovation" }

// response
{ "total_chunks": 14, "content": [...], "style_examples": [...], "funder_requirements": [...], "evidence": [...] }
```
Each group contains chunk objects with the same shape as `/search` results.

---

### POST /brief — slow (~2 min)
Retrieval + local compression via qwen2.5:3b. Set client timeout to 300s.
```json
// request — same shape as /context-pack
{ "task": "write the innovation section", "grant_scheme": "innovate_uk" }

// response
{
  "funder_requirements": { "requirements": [...], "scoring_criteria": [...], "key_warnings": [...] },
  "evidence": { "evidence_points": [{ "claim": "...", "source": "file.pdf" }] },
  "style_examples": { "patterns": [...], "tone_observations": [...], "structural_notes": [...] },
  "content": { "key_points": [...], "supporting_context": [...] }
}
```
Only call this when a compressed summary is needed. Do not call on every request.

---

### POST /ingest — varies (depends on file size)
Upload a document. Saved to `vault/docs/uploads/`, added to manifest, ingested into ChromaDB.
```
// request — multipart/form-data
file:           (binary)
grant_scheme:   innovate_uk | communities_fund | unknown
quality_signal: successful | unsuccessful | unknown
source_type:    funder_published | applicant_written | internal
sensitivity:    public | internal | confidential
```
```json
// response
{ "filename": "my-grant.pdf", "chunks": 14, "skipped": false }
```
Supported file types: `.pdf` `.docx` `.txt` `.md`

---

### DELETE /ingest/{filename}?delete_file=false — instant
Remove a document from the vault.
```json
// response
{ "filename": "my-grant.pdf", "chunks_removed": 14, "file_deleted": false }
```
Returns 404 if filename not found in vault.

---

## Errors
```json
{ "detail": "error message" }
```
`400` bad input — `404` not found — `500` internal (check Ollama is running)

---

## Interactive docs
`http://localhost:8100/docs` — available while server is running.
