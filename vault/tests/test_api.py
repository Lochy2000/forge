"""
API endpoint test suite.

Requires the vault API server to be running:
    uvicorn backend.api:app --reload --port 8100

Run from the vault directory:
    python -m tests.test_api
"""

import io
import json
import requests

BASE_URL = "http://localhost:8100"
TEST_FILENAME = "api-test-document.md"

TEST_FILE_CONTENT = b"""# API Test Document
This is a test grant document uploaded via the API endpoint.
The project demonstrates innovation in renewable energy technology.
We are seeking funding to develop a novel approach to grid-scale energy storage.
The team has significant expertise in electrochemistry and battery technology.
"""


def _ok(label: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    print(f"  {status}  {label}")
    if not condition and detail:
        print(f"         {detail}")
    return condition


def check_server():
    try:
        requests.get(BASE_URL, timeout=3)
        return True
    except Exception:
        return False


# --- Test 1: Health ---

def test_health():
    print("\n" + "=" * 60)
    print("TEST 1: GET /health")
    print("=" * 60)

    r = requests.get(f"{BASE_URL}/health", timeout=10)
    data = r.json()

    _ok("status 200", r.status_code == 200)
    _ok("status field is ok", data.get("status") == "ok")
    _ok("ollama field present", "ollama" in data)
    _ok("vault_chunks present", "vault_chunks" in data)
    _ok("models present", "models" in data)

    print(f"\n  ollama: {data.get('ollama')}")
    print(f"  vault_chunks: {data.get('vault_chunks')}")
    print(f"  models: {data.get('models')}")


# --- Test 2: Stats ---

def test_stats():
    print("\n" + "=" * 60)
    print("TEST 2: GET /stats")
    print("=" * 60)

    r = requests.get(f"{BASE_URL}/stats", timeout=10)
    data = r.json()

    _ok("status 200", r.status_code == 200)
    _ok("total_chunks present", "total_chunks" in data)
    _ok("grant_schemes present", "grant_schemes" in data)
    _ok("sources present", "sources" in data)
    _ok("vault has chunks", data.get("total_chunks", 0) > 0,
        "vault may be empty — run ingest first")

    print(f"\n  total_chunks: {data.get('total_chunks')}")
    print(f"  grant_schemes: {data.get('grant_schemes')}")
    print(f"  document_types: {data.get('document_types')}")
    print(f"  sources ({len(data.get('sources', []))} files): {data.get('sources', [])[:3]}...")


# --- Test 3: Search ---

def test_search():
    print("\n" + "=" * 60)
    print("TEST 3: POST /search")
    print("=" * 60)

    payload = {
        "query": "innovation beyond state of the art",
        "n_results": 3,
    }
    r = requests.post(f"{BASE_URL}/search", json=payload, timeout=30)
    data = r.json()

    _ok("status 200", r.status_code == 200)
    _ok("results field present", "results" in data)
    _ok("returns results", len(data.get("results", [])) > 0)
    _ok("result has source field", "source" in data.get("results", [{}])[0])
    _ok("result has distance field", "distance" in data.get("results", [{}])[0])

    print(f"\n  result_count: {data.get('result_count')}")
    for r_item in data.get("results", [])[:2]:
        print(f"  - {r_item.get('source')}  dist={r_item.get('distance', 0):.1f}")

    print("\n  Filter test (funder_requirement only):")
    payload_filtered = {
        "query": "what does the funder want to see",
        "n_results": 3,
        "where_filter": {"is_funder_requirement": "true"},
    }
    r2 = requests.post(f"{BASE_URL}/search", json=payload_filtered, timeout=30)
    data2 = r2.json()
    _ok("filtered search returns results", len(data2.get("results", [])) > 0)
    all_funder = all(
        res.get("is_funder_requirement") == "true"
        for res in data2.get("results", [])
    )
    _ok("all results are funder_requirement", all_funder)


# --- Test 4: Context pack ---

def test_context_pack():
    print("\n" + "=" * 60)
    print("TEST 4: POST /context-pack")
    print("=" * 60)

    payload = {
        "task": "write the innovation section for an Innovate UK clean tech grant",
        "grant_scheme": "innovate_uk",
        "section": "innovation",
    }
    r = requests.post(f"{BASE_URL}/context-pack", json=payload, timeout=60)
    data = r.json()

    _ok("status 200", r.status_code == 200)
    _ok("total_chunks present", "total_chunks" in data)
    _ok("content field present", "content" in data)
    _ok("style_examples field present", "style_examples" in data)
    _ok("funder_requirements field present", "funder_requirements" in data)
    _ok("evidence field present", "evidence" in data)

    print(f"\n  total_chunks: {data.get('total_chunks')}")
    for section in ["content", "style_examples", "funder_requirements", "evidence"]:
        print(f"  {section}: {len(data.get(section, []))} chunks")


# --- Test 5: Chunk lookup ---

def test_chunk_lookup():
    print("\n" + "=" * 60)
    print("TEST 5: GET /chunk")
    print("=" * 60)

    # Get a known source from stats first
    r = requests.get(f"{BASE_URL}/stats", timeout=10)
    sources = r.json().get("sources", [])

    if not sources:
        print("  SKIP  no sources in vault")
        return

    source = sources[0]
    print(f"  Testing with source: {source}")

    # Look up chunk 0 from that source
    r = requests.get(f"{BASE_URL}/chunk", params={"source": source, "index": 0}, timeout=10)
    data = r.json()

    _ok("status 200", r.status_code == 200, str(data))
    _ok("content field present", "content" in data)
    _ok("metadata field present", "metadata" in data)
    _ok("source matches", data.get("source") == source)
    _ok("chunk index matches", data.get("chunk") == 0)

    print(f"\n  content preview: {data.get('content', '')[:100]}...")

    # Test 404 for non-existent chunk
    r2 = requests.get(
        f"{BASE_URL}/chunk",
        params={"source": "nonexistent.pdf", "index": 0},
        timeout=10,
    )
    _ok("404 for missing chunk", r2.status_code == 404)


# --- Test 6: Ingest ---

def test_ingest():
    print("\n" + "=" * 60)
    print("TEST 5: POST /ingest")
    print("=" * 60)

    files = {"file": (TEST_FILENAME, io.BytesIO(TEST_FILE_CONTENT), "text/markdown")}
    data = {
        "grant_scheme": "unknown",
        "quality_signal": "unknown",
        "source_type": "internal",
        "sensitivity": "public",
    }

    r = requests.post(f"{BASE_URL}/ingest", files=files, data=data, timeout=120)
    result = r.json()

    _ok("status 200", r.status_code == 200, str(result))
    _ok("filename matches", result.get("filename") == TEST_FILENAME)
    _ok("chunks stored or skipped", "chunks" in result)
    _ok("metadata returned", "metadata" in result)

    print(f"\n  filename: {result.get('filename')}")
    print(f"  chunks: {result.get('chunks')}")
    print(f"  skipped: {result.get('skipped')}")
    print(f"  relative_path: {result.get('relative_path')}")


# --- Test 6: Delete ---

def test_delete():
    print("\n" + "=" * 60)
    print("TEST 6: DELETE /ingest/{filename}")
    print("=" * 60)

    r = requests.delete(
        f"{BASE_URL}/ingest/{TEST_FILENAME}",
        params={"delete_file": True},
        timeout=15,
    )
    result = r.json()

    _ok("status 200", r.status_code == 200, str(result))
    _ok("chunks_removed > 0", result.get("chunks_removed", 0) > 0)
    _ok("file_deleted true", result.get("file_deleted") is True)

    print(f"\n  chunks_removed: {result.get('chunks_removed')}")
    print(f"  manifest_key_removed: {result.get('manifest_key_removed')}")
    print(f"  file_deleted: {result.get('file_deleted')}")

    # Confirm gone from vault
    r2 = requests.post(
        f"{BASE_URL}/search",
        json={"query": "api test document renewable energy", "n_results": 5},
        timeout=30,
    )
    results = r2.json().get("results", [])
    still_present = any(res.get("source") == TEST_FILENAME for res in results)
    _ok("document no longer in search results", not still_present)


# --- Run all ---

if __name__ == "__main__":
    print("\nGrant Vault — API Test Suite")
    print(f"Target: {BASE_URL}")
    print("Make sure the server is running: uvicorn backend.api:app --reload --port 8100\n")

    if not check_server():
        print(f"ERROR: Cannot reach {BASE_URL}")
        print("Start the server first: uvicorn backend.api:app --reload --port 8100")
        exit(1)

    print("Server is up. Running tests...\n")

    test_health()
    test_stats()
    test_search()
    test_context_pack()
    test_chunk_lookup()
    test_ingest()
    test_delete()

    print("\n" + "=" * 60)
    print("Done. Check output above for any FAIL results.")
    print("Interactive API docs: http://localhost:8100/docs")
    print("=" * 60)
