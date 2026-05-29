import chromadb

from backend.config import CHROMA_DIR, COLLECTION_NAME
from backend.ollama_embed import get_embedding


def search_vault(
    query: str,
    n_results: int = 5,
    where_filter: dict | None = None
):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    query_embedding = get_embedding(query)

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
    }

    if where_filter:
        query_args["where"] = where_filter

    return collection.query(**query_args)


def format_results(results: dict) -> list[dict]:
    docs = results["documents"][0]
    metadata = results["metadatas"][0]
    distances = results.get("distances", [[None] * len(docs)])[0]

    formatted = []

    for i, doc in enumerate(docs):
        formatted.append({
            "content": doc,
            "source": metadata[i].get("source"),
            "chunk": metadata[i].get("chunk"),
            "document_type": metadata[i].get("document_type"),
            "section_hint": metadata[i].get("section_hint"),
            "sensitivity": metadata[i].get("sensitivity"),
            "retrieval_intent": metadata[i].get("retrieval_intent"),
            "grant_scheme": metadata[i].get("grant_scheme"),
            "quality_signal": metadata[i].get("quality_signal"),
            "source_type": metadata[i].get("source_type"),
            "contains_numbers": metadata[i].get("contains_numbers"),
            "distance": distances[i],
        })

    return formatted


def print_results(results: dict):
    formatted = format_results(results)

    for i, item in enumerate(formatted):
        print("\n" + "=" * 80)
        print(f"Result {i + 1}")
        print(f"Source: {item['source']}")
        print(f"Document type: {item['document_type']}")
        print(f"Section hint: {item['section_hint']}")
        print(f"Chunk: {item['chunk']}")
        print(f"Distance: {item['distance']}")
        print("-" * 80)
        print(item["content"][:1400])


def main():
    print("Grant Vault Search")
    print("Type 'exit' to quit.")
    print("\nFilter types:")
    print("1 = grant guidance only")
    print("2 = grant applications only")
    print("3 = environmental impact only")
    print("4 = risk mitigation only")
    print("5 = no filter")

    while True:
        query = input("\nSearch query: ").strip()

        if query.lower() == "exit":
            break

        filter_choice = input("Choose filter type [1-5]: ").strip()

        where_filter = None

        if filter_choice == "1":
            where_filter = {"document_type": "grant_guidance"}
        elif filter_choice == "2":
            where_filter = {"document_type": "grant_application"}
        elif filter_choice == "3":
            where_filter = {"section_hint": "environmental_impact"}
        elif filter_choice == "4":
            where_filter = {"section_hint": "risk_mitigation"}

        results = search_vault(
            query=query,
            n_results=5,
            where_filter=where_filter
        )

        print_results(results)


if __name__ == "__main__":
    main()