"""
End-to-end retrieval test suite.

Run from the vault directory:
    python -m tests.test_retrieval

Tests:
1. Section hint accuracy
2. Distance distribution
3. Relevance check
4. Metadata fields — are new fields present on stored chunks?
5. Intent-based retrieval — does each function return the right type of content?
6. Dynamic n_results — does it scale with vault size?
7. Distance filtering — does relative filtering work?
"""

from backend.chunk_text import detect_section
from backend.search import search_vault
from backend.retrieval_engine import (
    _get_collection,
    _dynamic_n_results,
    _filter_by_distance,
    expand_query,
    retrieve_content,
    retrieve_style_examples,
    retrieve_funder_requirements,
    retrieve_evidence,
)


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
            print("  Moderate — some relevant results but corpus may need more documents")
        else:
            print("  High — test corpus mismatch expected; will improve with real documents")


# ─── Test 3: Relevance check ─────────────────────────────────────────────────

def test_relevance():
    print("\n" + "=" * 60)
    print("TEST 3: Relevance check")
    print("=" * 60)
    print("Score each result: 0=irrelevant  1=tangential  2=relevant  3=highly relevant\n")

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


# ─── Test 4: Metadata fields ──────────────────────────────────────────────────

def test_metadata_fields():
    print("\n" + "=" * 60)
    print("TEST 4: Metadata fields")
    print("=" * 60)
    print("Checking new fields are present on stored chunks.")

    required_fields = [
        "source", "chunk", "document_type", "section_hint",
        "grant_scheme", "quality_signal", "source_type",
        "sensitivity", "retrieval_intent", "contains_numbers",
    ]

    try:
        results = search_vault("grant funding", n_results=3)
        metadatas = results["metadatas"][0]

        passed = 0

        for field in required_fields:
            present = all(field in m for m in metadatas)
            status = "PASS" if present else "FAIL"
            if present:
                passed += 1
            sample = metadatas[0].get(field, "MISSING") if metadatas else "no results"
            print(f"  {status}  {field:<20} sample={sample}")

        print(f"\n  Result: {passed}/{len(required_fields)} fields present")
        return passed, len(required_fields)

    except Exception as e:
        print(f"  ERROR: {e}")
        return 0, len(required_fields)


# ─── Test 5: Intent-based retrieval ──────────────────────────────────────────

def test_intent_retrieval():
    print("\n" + "=" * 60)
    print("TEST 5: Intent-based retrieval")
    print("=" * 60)

    checks = [
        ("retrieve_content", retrieve_content("grant project overview", section=None), "content"),
        ("retrieve_style_examples", retrieve_style_examples(query="how to write environmental section"), "style_example"),
        ("retrieve_funder_requirements", retrieve_funder_requirements(query="what funder wants to see"), "funder_requirement"),
        ("retrieve_evidence", retrieve_evidence("carbon emissions reduction 50%"), None),
    ]

    for fn_name, results, expected_intent in checks:
        count = len(results)
        print(f"\n  {fn_name}() → {count} results")

        if not results:
            print("  WARNING: no results returned")
            continue

        for r in results[:2]:
            intent = r.get("retrieval_intent", "unknown")
            scheme = r.get("grant_scheme", "unknown")
            dist = r.get("distance")
            dist_str = f"{dist:.1f}" if dist is not None else "None"
            print(f"    intent={intent:<20} scheme={scheme:<15} dist={dist_str}  source={r.get('source')}")

        if expected_intent:
            intents = [r.get("retrieval_intent") for r in results]
            matched = sum(1 for i in intents if i == expected_intent)
            print(f"  Intent match: {matched}/{len(results)} results have intent={expected_intent}")


# ─── Test 6: Dynamic n_results ────────────────────────────────────────────────

def test_dynamic_n_results():
    print("\n" + "=" * 60)
    print("TEST 6: Dynamic n_results")
    print("=" * 60)

    collection = _get_collection()
    total = collection.count()
    n = _dynamic_n_results(collection)

    print(f"  Vault size: {total} chunks")
    print(f"  Dynamic n_results: {n}")
    print(f"  Coverage: {n/total*100:.1f}% of vault" if total > 0 else "  Empty vault")

    expected_min = min(max(int(total * 0.15), 10), 40)
    expected_min = min(expected_min, total)
    status = "PASS" if n == expected_min else "FAIL"
    print(f"  {status}  expected={expected_min}  got={n}")


# ─── Test 7: Distance filtering ───────────────────────────────────────────────

def test_distance_filtering():
    print("\n" + "=" * 60)
    print("TEST 7: Distance filtering")
    print("=" * 60)

    mock_results = [
        {"source": "a.pdf", "chunk": 0, "distance": 100.0, "content": ""},
        {"source": "b.pdf", "chunk": 0, "distance": 120.0, "content": ""},
        {"source": "c.pdf", "chunk": 0, "distance": 200.0, "content": ""},
        {"source": "d.pdf", "chunk": 0, "distance": 350.0, "content": ""},
        {"source": "e.pdf", "chunk": 0, "distance": 500.0, "content": ""},
    ]

    filtered = _filter_by_distance(mock_results, tolerance=1.4, min_results=3)
    threshold = 100.0 * 1.4

    print(f"  Input: {len(mock_results)} results")
    print(f"  Best distance: 100.0  Threshold (x1.4): {threshold}")
    print(f"  After filtering: {len(filtered)} results")

    for r in filtered:
        status = "KEEP" if r["distance"] <= threshold else "OVER"
        print(f"    {status}  dist={r['distance']}  source={r['source']}")

    within_threshold = [r for r in mock_results if r["distance"] <= threshold]
    expected_count = max(len(within_threshold), 3)  # min_results=3 guarantee
    status = "PASS" if len(filtered) == expected_count else "FAIL"
    print(f"\n  {status}  expected={expected_count} kept (min_results=3 applied)  got={len(filtered)}")


# ─── Test 8: Query expansion ─────────────────────────────────────────────────

def test_query_expansion():
    print("\n" + "=" * 60)
    print("TEST 8: Query expansion")
    print("=" * 60)

    cases = [
        ("environmental impact section", True),
        ("innovation beyond state of the art", True),
        ("something completely unrelated", False),
    ]

    for query, should_expand in cases:
        expanded = expand_query(query)
        did_expand = len(expanded) > 1
        status = "PASS" if did_expand == should_expand else "FAIL"
        print(f"\n  {status}  query='{query}'")
        print(f"    expanded to {len(expanded)} queries:")
        for q in expanded:
            print(f"      - {q}")


# ─── Run all tests ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nGrant Vault — Full Retrieval Test Suite")
    print("Make sure Ollama is running and vault is ingested before running.")
    print("Run from vault directory: python -m tests.test_retrieval\n")

    hint_passed, hint_total = test_section_hints()
    test_distance_distribution()
    test_relevance()
    meta_passed, meta_total = test_metadata_fields()
    test_intent_retrieval()
    test_dynamic_n_results()
    test_distance_filtering()
    test_query_expansion()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Section hints:   {hint_passed}/{hint_total} correct")
    print(f"  Metadata fields: {meta_passed}/{meta_total} present")
    print("")
    print("Next steps:")
    print("  - If metadata fields fail: reset_db and re-ingest")
    print("  - If intent retrieval returns 0 results: check retrieval_intent values in stored chunks")
    print("  - If distances are high: expected with test corpus, will improve with real documents")
    print()
