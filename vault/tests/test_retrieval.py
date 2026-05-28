"""
End-to-end retrieval test.

Run from the vault directory:
    python -m tests.test_retrieval

Tests three things:
1. Section hint accuracy  — does detect_section tag chunks correctly?
2. Distance distribution  — what is the range of distances across the vault?
3. Relevance             — do top results match the query intent?
"""

from backend.chunk_text import detect_section
from backend.search import search_vault


# ─── Test 1: Section hint accuracy ───────────────────────────────────────────

def test_section_hints():
    print("\n" + "=" * 60)
    print("TEST 1: Section hint accuracy")
    print("=" * 60)

    cases = [
        ("Carbon emissions will be reduced by switching to renewable energy sources", "environmental_impact"),
        ("The market opportunity is estimated at £50 million across the UK clean energy sector", "market_need"),
        ("The project faces supply chain risks that could delay membrane manufacturing by 6 weeks", "risk_mitigation"),
        ("Dr Sarah Chen holds a PhD in electrochemistry and leads the technical team", "team_capability"),
        ("The project cannot be self-funded at this stage as commercial finance is unavailable", "funding_justification"),
        ("Work Package 1 covers membrane scale-up with a milestone at month 6", "project_management"),
        ("Innovation beyond the current state of the art in vanadium flow battery technology", "innovation"),
    ]

    passed = 0

    for text, expected in cases:
        actual = detect_section(text)
        status = "PASS" if actual == expected else "FAIL"
        if actual == expected:
            passed += 1
        print(f"  {status}  expected={expected:<25} got={actual:<25}")
        print(f"       text: {text[:70]}")

    print(f"\n  Result: {passed}/{len(cases)} correct")
    return passed, len(cases)


# ─── Test 2: Distance distribution ───────────────────────────────────────────

def test_distance_distribution():
    print("\n" + "=" * 60)
    print("TEST 2: Distance distribution")
    print("=" * 60)

    queries = [
        "environmental impact of clean technology",
        "innovation beyond state of the art",
        "market opportunity for energy storage",
        "risk mitigation strategy",
        "team capability and expertise",
    ]

    all_distances = []

    for query in queries:
        try:
            results = search_vault(query, n_results=5)
            distances = results["distances"][0]
            all_distances.extend(distances)
            avg = sum(distances) / len(distances)
            print(f"  Query: {query[:50]}")
            print(f"    min={min(distances):.1f}  max={max(distances):.1f}  avg={avg:.1f}")
        except Exception as e:
            print(f"  ERROR on query '{query}': {e}")

    if all_distances:
        overall_avg = sum(all_distances) / len(all_distances)
        print(f"\n  Overall — min={min(all_distances):.1f}  max={max(all_distances):.1f}  avg={overall_avg:.1f}")
        print("\n  Interpretation:")
        if overall_avg < 150:
            print("  Good — distances suggest reasonable semantic matches")
        elif overall_avg < 250:
            print("  Moderate — some relevant results but corpus may need more targeted documents")
        else:
            print("  High — distances suggest poor semantic matching, corpus likely needs improvement")


# ─── Test 3: Relevance check ─────────────────────────────────────────────────

def test_relevance():
    print("\n" + "=" * 60)
    print("TEST 3: Relevance check")
    print("=" * 60)
    print("For each result, ask: is this chunk actually useful for the query?")
    print("Score mentally: 0=irrelevant  1=tangential  2=relevant  3=highly relevant\n")

    queries = [
        ("Environmental impact section for clean tech grant", {"section_hint": "environmental_impact"}),
        ("Why public funding is needed for this project", None),
        ("Innovation beyond state of the art in energy storage", None),
    ]

    for query, filter_ in queries:
        print(f"\n  Query: '{query}'")
        if filter_:
            print(f"  Filter: {filter_}")
        print(f"  {'-' * 50}")

        try:
            results = search_vault(query, n_results=3, where_filter=filter_)
            docs = results["documents"][0]
            metadata = results["metadatas"][0]
            distances = results["distances"][0]

            for i, (doc, meta, dist) in enumerate(zip(docs, metadata, distances), 1):
                print(f"\n  Result {i} — source={meta.get('source')}  chunk={meta.get('chunk')}  dist={dist:.1f}")
                print(f"  section_hint={meta.get('section_hint')}  doc_type={meta.get('document_type')}")
                print(f"  Text: {doc[:200]}...")

        except Exception as e:
            print(f"  ERROR: {e}")


# ─── Run all tests ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nGrant Vault — End-to-End Retrieval Test")
    print("Make sure Ollama is running before executing this script.")
    print("Run from vault directory: python -m tests.test_retrieval\n")

    hint_passed, hint_total = test_section_hints()
    test_distance_distribution()
    test_relevance()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Section hints: {hint_passed}/{hint_total} correct")
    print("\nNext steps based on results:")
    print("  - If section hints fail: fix detect_section() in chunk_text.py")
    print("  - If distances are high (>250 avg): add more relevant documents to vault")
    print("  - If relevance results are wrong document types: re-ingest with reset_db first")
    print()
