import uuid
import chromadb

from backend.config import (
    DOCS_DIR,
    CHROMA_DIR,
    COLLECTION_NAME
)

from backend.extract_text import extract_text
from backend.chunk_text import chunk_text
from backend.ollama_embed import get_embedding


def infer_document_type(file_path):
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


def main():

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    files = (
        list(DOCS_DIR.rglob("*.pdf")) +
        list(DOCS_DIR.rglob("*.docx")) +
        list(DOCS_DIR.rglob("*.txt")) +
        list(DOCS_DIR.rglob("*.md"))
    )

    print(f"Found {len(files)} files")

    total_chunks = 0

    for file_path in files:

        print(f"\nProcessing: {file_path.name}")

        text = extract_text(file_path)

        if not text.strip():
            print("No text found")
            continue

        chunks = chunk_text(text)

        print(f"Chunks: {len(chunks)}")

        document_type = infer_document_type(file_path)

        for i, chunk in enumerate(chunks):

            chunk_content = chunk["text"]

            embedding = get_embedding(chunk_content)

            collection.add(
                ids=[str(uuid.uuid4())],
                embeddings=[embedding],
                documents=[chunk_content],
                metadatas=[{
                    "source": file_path.name,
                    "path": str(file_path),
                    "chunk": i,
                    "file_type": file_path.suffix.lower(),
                    "document_type": document_type,
                    "section_hint": chunk["section_hint"],
                    "sensitivity": "public_test"
                }]
            )

            total_chunks += 1

    print(f"\nDone. Stored {total_chunks} chunks.")


if __name__ == "__main__":
    main()