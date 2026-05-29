"""
Standalone summarisation test.

Tests the compression layer in isolation — no vault, no ingest, no Chroma required.
Only needs Ollama running with qwen2.5:3b.

Run from the vault directory:
    python -m tests.test_summarise
"""

import json
import time
import requests

from backend.summarise import (
    _extract_json,
    _format_chunks,
    compress_funder_requirements,
    compress_evidence,
    compress_style_examples,
    compress_content,
    compress_context_pack,
    to_markdown,
)
from backend.config import OLLAMA_CHAT_URL, GENERATIVE_MODEL


# --- Sample chunks (no vault needed) ---

SAMPLE_STYLE_CHUNKS = [
    {
        "source": "innovate-uk-clean-tech-application-example.md",
        "chunk": 1,
        "distance": 265.9,
        "content": (
            "Existing commercial VRFB systems use Nafion-based membranes with known degradation pathways. "
            "Academic literature has identified sulfonated polyether ether ketone (SPEEK) as a promising "
            "alternative, but laboratory synthesis has not been scaled beyond 10g batches. "
            "GreenFlux has developed a proprietary continuous flow synthesis process that produces SPEEK "
            "membranes at 500kg/batch with consistent proton conductivity above 80 mS/cm. "
            "This represents a step-change beyond the current state of the art."
        ),
        "is_style_example": "true",
        "grant_scheme": "innovate_uk",
    },
    {
        "source": "innovate-uk-clean-tech-application-example.md",
        "chunk": 3,
        "distance": 304.7,
        "content": (
            "Each 10 MWh GreenFlux system displaces approximately 1,850 tonnes of CO2 per year "
            "compared to gas peaking plants. Across a projected 200 UK installations by 2032, "
            "this represents a cumulative emissions reduction of 370,000 tonnes per year — "
            "equivalent to removing 80,000 cars from UK roads annually."
        ),
        "is_style_example": "true",
        "grant_scheme": "innovate_uk",
    },
]

SAMPLE_FUNDER_CHUNKS = [
    {
        "source": "innovate-uk-smart-grant-guidance-example.md",
        "chunk": 2,
        "distance": 290.6,
        "content": (
            "Applicants must demonstrate clear innovation beyond the current state of the art. "
            "Describe what currently exists, why it is inadequate, and precisely how your solution "
            "advances beyond it. Vague claims of novelty will not score well. "
            "Quantified comparisons are strongly preferred."
        ),
        "is_funder_requirement": "true",
        "grant_scheme": "innovate_uk",
    },
    {
        "source": "Business-Connect-Good-Application-Guide_2024.pdf",
        "chunk": 15,
        "distance": 209.0,
        "content": (
            "A clear need for support. Essentially you are explaining why public money should be "
            "used on your project. Ideally by demonstrating that the project cannot proceed without "
            "public funding and that there is a clear market failure preventing private investment."
        ),
        "is_funder_requirement": "true",
        "grant_scheme": "innovate_uk",
    },
]

SAMPLE_EVIDENCE_CHUNKS = [
    {
        "source": "innovate-uk-clean-tech-application-example.md",
        "chunk": 2,
        "distance": 340.6,
        "content": (
            "Our £150/kWh target removes the cost barrier and opens a serviceable addressable market "
            "of £4.2 billion in the UK alone by 2030. Current Nafion-based systems cost £220-£260/kWh. "
            "The 500 kWh pilot system will validate manufacturing costs at scale."
        ),
        "is_evidence": "true",
        "is_factual_claim": "true",
        "grant_scheme": "innovate_uk",
    },
]

SAMPLE_CONTENT_CHUNKS = [
    {
        "source": "grant-checklist.md",
        "chunk": 0,
        "distance": 300.7,
        "content": (
            "Before submitting your grant application, ensure you have clearly described the problem "
            "your project addresses, the innovation involved, the market opportunity, and why your "
            "team is best placed to deliver. Evidence all claims where possible."
        ),
        "is_content": "true",
        "grant_scheme": "unknown",
    },
]

SAMPLE_PACK = {
    "task": "Write the innovation section for an Innovate UK clean tech grant application",
    "grant_scheme": "innovate_uk",
    "section": "innovation",
    "content": SAMPLE_CONTENT_CHUNKS,
    "style_examples": SAMPLE_STYLE_CHUNKS,
    "funder_requirements": SAMPLE_FUNDER_CHUNKS,
    "evidence": SAMPLE_EVIDENCE_CHUNKS,
}


# --- Test 1: Ollama connection ---

def test_ollama_connection():
    print("\n" + "=" * 60)
    print("TEST 1: Ollama connection")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:11434", timeout=5)
        print(f"  PASS  Ollama is running (status {response.status_code})")
        print(f"  Model: {GENERATIVE_MODEL}")
        return True
    except Exception as e:
        print(f"  FAIL  Cannot reach Ollama: {e}")
        print("  Start Ollama with: ollama serve")
        return False


# --- Test 2: JSON extraction ---

def test_json_extraction():
    print("\n" + "=" * 60)
    print("TEST 2: JSON extraction")
    print("=" * 60)

    cases = [
        ('{"key": "value"}', True, "direct JSON"),
        ('```json\n{"key": "value"}\n```', True, "code block"),
        ('Here is the result:\n{"key": "value"}\nDone.', True, "inline JSON"),
        ("This is not JSON at all", False, "no JSON"),
    ]

    passed = 0
    for text, should_succeed, label in cases:
        result = _extract_json(text)
        success = "error" not in result
        status = "PASS" if success == should_succeed else "FAIL"
        if success == should_succeed:
            passed += 1
        print(f"  {status}  {label}: {result}")

    print(f"\n  Result: {passed}/{len(cases)} correct")


# --- Test 3: Chunk formatting ---

def test_chunk_formatting():
    print("\n" + "=" * 60)
    print("TEST 3: Chunk formatting")
    print("=" * 60)

    formatted = _format_chunks(SAMPLE_STYLE_CHUNKS, max_chunks=2, max_chars=100)
    lines = formatted.split("\n")
    print(f"  Chunks formatted: {len([l for l in lines if l.startswith('[')])} entries")
    print(f"  Preview:\n{formatted[:300]}")
    print("  PASS" if "[1]" in formatted and "[2]" in formatted else "  FAIL")


# --- Test 4: Individual compression functions ---

def test_compression_functions():
    print("\n" + "=" * 60)
    print("TEST 4: Individual compression functions")
    print("=" * 60)

    task = SAMPLE_PACK["task"]

    functions = [
        ("compress_funder_requirements", compress_funder_requirements, SAMPLE_FUNDER_CHUNKS,
         ["requirements", "scoring_criteria", "key_warnings"]),
        ("compress_evidence",            compress_evidence,            SAMPLE_EVIDENCE_CHUNKS,
         ["evidence_points"]),
        ("compress_style_examples",      compress_style_examples,      SAMPLE_STYLE_CHUNKS,
         ["patterns", "tone_observations", "structural_notes"]),
        ("compress_content",             compress_content,             SAMPLE_CONTENT_CHUNKS,
         ["key_points", "supporting_context"]),
    ]

    for fn_name, fn, chunks, expected_keys in functions:
        print(f"\n  {fn_name}()")
        start = time.time()
        result = fn(chunks, task)
        elapsed = time.time() - start

        has_error = "error" in result
        has_keys = all(k in result for k in expected_keys)

        status = "PASS" if has_keys and not has_error else "FAIL"
        print(f"  {status}  ({elapsed:.1f}s)")

        if has_error:
            print(f"  ERROR: {result}")
        else:
            print(f"  Keys present: {list(result.keys())}")
            for k in expected_keys:
                items = result.get(k, [])
                if items:
                    print(f"  {k}[0]: {str(items[0])[:120]}")


# --- Test 5: Full pack compression ---

def test_full_compression():
    print("\n" + "=" * 60)
    print("TEST 5: Full pack compression")
    print("=" * 60)

    start = time.time()
    compressed = compress_context_pack(SAMPLE_PACK)
    elapsed = time.time() - start

    expected_sections = ["funder_requirements", "evidence", "style_examples", "content"]
    all_present = all(s in compressed for s in expected_sections)
    any_errors = any("error" in compressed.get(s, {}) for s in expected_sections)

    status = "PASS" if all_present and not any_errors else "FAIL"
    print(f"  {status}  Full compression took {elapsed:.1f}s")

    for section in expected_sections:
        data = compressed.get(section, {})
        if "error" in data:
            print(f"  {section}: ERROR — {data['error']}")
        else:
            total_items = sum(len(v) for v in data.values() if isinstance(v, list))
            print(f"  {section}: {total_items} items extracted")

    return compressed


# --- Test 6: Markdown output ---

def test_markdown_output(compressed: dict):
    print("\n" + "=" * 60)
    print("TEST 6: Markdown output")
    print("=" * 60)

    md = to_markdown(compressed)
    has_headers = "## Funder Requirements" in md and "## Key Evidence" in md
    status = "PASS" if has_headers else "FAIL"
    print(f"  {status}  Markdown generated ({len(md)} chars)")
    print("\n" + "-" * 40)
    print(md[:800])
    print("-" * 40)


# --- Run all tests ---

if __name__ == "__main__":
    print("\nGrant Vault — Summarisation Test Suite")
    print("Needs: Ollama running with qwen2.5:3b")
    print("Does NOT need: vault ingested, ChromaDB, or any other component\n")

    ollama_ok = test_ollama_connection()
    test_json_extraction()
    test_chunk_formatting()

    if not ollama_ok:
        print("\nSkipping model tests — Ollama not available.")
    else:
        test_compression_functions()
        compressed = test_full_compression()
        test_markdown_output(compressed)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("Full JSON output:")
        print(json.dumps(compressed, indent=2)[:1500])
