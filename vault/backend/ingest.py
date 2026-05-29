import hashlib
import json
import re
import chromadb

from backend.config import (
    DOCS_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    MANIFEST_PATH,
)

from backend.extract_text import extract_text
from backend.chunk_text import chunk_text
from backend.ollama_embed import get_embedding


_MANIFEST_DEFAULTS = {
    "grant_scheme": "unknown",
    "quality_signal": "unknown",
    "source_type": "unknown",
    "sensitivity": "internal",
}


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("Warning: manifest.json not found — using defaults for all documents")
        return {}
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def make_chunk_id(file_path, chunk_index: int) -> str:
    relative = file_path.relative_to(DOCS_DIR).as_posix()
    key = f"{relative}::{chunk_index}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]


def is_already_ingested(file_path, collection) -> bool:
    first_chunk_id = make_chunk_id(file_path, 0)
    result = collection.get(ids=[first_chunk_id])
    return len(result["ids"]) > 0


def get_manifest_entry(file_path, manifest: dict) -> dict:
    relative = file_path.relative_to(DOCS_DIR).as_posix()
    entry = manifest.get(relative, {})
    return {**_MANIFEST_DEFAULTS, **entry}


def infer_document_type(file_path) -> str:
    name = file_path.name.lower()

    if "guide" in name or "guidance" in name:
        return "grant_guidance"
    if "checklist" in name:
        return "grant_guidance"
    if "application" in name or "grant" in name:
        return "grant_application"
    if file_path.suffix.lower() in [".md", ".txt"]:
        return "notes"

    return "unknown"


def has_numbers(text: str) -> bool:
    patterns = [
        r"[£$€]\s*[\d,]+",
        r"[\d,]+\s*%",
        r"\d+\s*(kWh|MW|GW|kg|tonne|million|billion|km|mS|TRL)",
        r"\d{1,3}(,\d{3})+",
    ]
    return any(bool(re.search(p, text, re.IGNORECASE)) for p in patterns)


def infer_retrieval_intent(
    source_type: str,
    document_type: str,
    quality_signal: str,
    chunk_has_numbers: bool
) -> str:
    if source_type == "funder_published":
        return "funder_requirement"

    if document_type == "grant_application":
        if quality_signal == "successful":
            if chunk_has_numbers:
                return "factual_claim"
            return "style_example"
        if chunk_has_numbers:
            return "evidence"
        return "content"

    if document_type == "template":
        return "style_example"

    return "content"


def main():
    manifest = load_manifest()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    files = (
        list(DOCS_DIR.rglob("*.pdf")) +
        list(DOCS_DIR.rglob("*.docx")) +
        list(DOCS_DIR.rglob("*.txt")) +
        list(DOCS_DIR.rglob("*.md"))
    )

    # exclude manifest itself
    files = [f for f in files if f.name != "manifest.json"]

    print(f"Found {len(files)} files")

    total_chunks = 0

    skipped = 0

    for file_path in files:
        if is_already_ingested(file_path, collection):
            print(f"\nSkipping (already ingested): {file_path.name}")
            skipped += 1
            continue

        print(f"\nProcessing: {file_path.name}")

        text = extract_text(file_path)

        if not text.strip():
            print("No text found")
            continue

        chunks = chunk_text(text)
        print(f"Chunks: {len(chunks)}")

        doc_entry = get_manifest_entry(file_path, manifest)
        document_type = infer_document_type(file_path)

        for i, chunk in enumerate(chunks):
            chunk_text_content = chunk["text"]
            chunk_has_numbers = has_numbers(chunk_text_content)

            retrieval_intent = infer_retrieval_intent(
                source_type=doc_entry["source_type"],
                document_type=document_type,
                quality_signal=doc_entry["quality_signal"],
                chunk_has_numbers=chunk_has_numbers,
            )

            embedding = get_embedding(chunk_text_content)

            collection.upsert(
                ids=[make_chunk_id(file_path, i)],
                embeddings=[embedding],
                documents=[chunk_text_content],
                metadatas=[{
                    "source": file_path.name,
                    "path": str(file_path),
                    "chunk": i,
                    "file_type": file_path.suffix.lower(),
                    "document_type": document_type,
                    "section_hint": chunk["section_hint"],
                    "grant_scheme": doc_entry["grant_scheme"],
                    "quality_signal": doc_entry["quality_signal"],
                    "source_type": doc_entry["source_type"],
                    "sensitivity": doc_entry["sensitivity"],
                    "retrieval_intent": retrieval_intent,
                    "contains_numbers": str(chunk_has_numbers),
                }]
            )

            total_chunks += 1

    print(f"\nDone. Stored {total_chunks} new chunks. Skipped {skipped} already-ingested files.")


if __name__ == "__main__":
    main()
