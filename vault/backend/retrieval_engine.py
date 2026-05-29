import chromadb

from backend.config import CHROMA_DIR, COLLECTION_NAME
from backend.ollama_embed import get_embedding
from backend.search import format_results


# --- Collection helper ---

def _get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME)


# --- Dynamic n_results ---

def _dynamic_n_results(collection) -> int:
    total = collection.count()
    target = min(max(int(total * 0.15), 10), 40)
    return min(target, total)


# --- Relative distance filtering ---

def _filter_by_distance(
    results: list[dict],
    tolerance: float = 1.4,
    min_results: int = 3
) -> list[dict]:
    if not results:
        return results

    distances = [r["distance"] for r in results if r["distance"] is not None]

    if not distances:
        return results

    best = min(distances)
    threshold = best * tolerance
    filtered = [r for r in results if r["distance"] is None or r["distance"] <= threshold]

    if len(filtered) < min_results:
        sortable = [r for r in results if r["distance"] is not None]
        return sorted(sortable, key=lambda r: r["distance"])[:min_results]

    return filtered


# --- Where filter builder ---

def _build_where(*conditions) -> dict | None:
    active = [c for c in conditions if c is not None]
    if not active:
        return None
    if len(active) == 1:
        return active[0]
    return {"$and": active}


# --- Rule-based query expansion ---

_EXPANSIONS = {
    "environmental": [
        "carbon emissions sustainability impact",
        "environmental benefits evidence grant",
    ],
    "innovation": [
        "novel technology beyond state of the art",
        "technical advancement over existing solutions",
    ],
    "risk": [
        "risk mitigation contingency strategy",
        "project risks management plan",
    ],
    "market": [
        "market opportunity commercial potential route to market",
        "target customers demand evidence",
    ],
    "team": [
        "team expertise capability delivery",
        "key personnel skills experience",
    ],
    "fund": [
        "why public funding is needed additionality",
        "market failure grant justification",
    ],
    "impact": [
        "project outcomes expected benefits",
        "measurable impact success metrics",
    ],
    "budget": [
        "project costs financial breakdown value for money",
        "cost justification grant budget",
    ],
    "style": [
        "grant writing structure and tone example",
        "how to write a grant section",
    ],
}


def expand_query(query: str) -> list[str]:
    queries = [query]
    lower = query.lower()
    for keyword, variants in _EXPANSIONS.items():
        if keyword in lower:
            for v in variants:
                if v not in queries:
                    queries.append(v)
    return queries[:4]


# --- Core search with expansion and filtering ---

def _search(
    query: str,
    where_filter: dict | None = None,
    collection=None
) -> list[dict]:
    if collection is None:
        collection = _get_collection()

    n = _dynamic_n_results(collection)
    queries = expand_query(query)

    best_by_chunk: dict[tuple, dict] = {}

    for q in queries:
        embedding = get_embedding(q)
        args = {
            "query_embeddings": [embedding],
            "n_results": n,
        }
        if where_filter:
            args["where"] = where_filter

        try:
            raw = collection.query(**args)
            formatted = format_results(raw)
        except Exception:
            continue

        for item in formatted:
            key = (item["source"], item["chunk"])
            if key not in best_by_chunk or (
                item["distance"] is not None
                and best_by_chunk[key]["distance"] is not None
                and item["distance"] < best_by_chunk[key]["distance"]
            ):
                best_by_chunk[key] = item

    results = list(best_by_chunk.values())
    filtered = _filter_by_distance(results)
    return sorted(filtered, key=lambda r: (r["distance"] is None, r["distance"]))


# --- Intent-based retrieval functions ---

def retrieve_content(
    query: str,
    section: str | None = None,
    grant_scheme: str | None = None,
    collection=None
) -> list[dict]:
    """Writing agent: relevant content for a specific section."""
    where = _build_where(
        {"retrieval_intent": "content"},
        {"section_hint": section} if section else None,
        {"grant_scheme": grant_scheme} if grant_scheme else None,
    )
    return _search(query, where_filter=where, collection=collection)


def retrieve_style_examples(
    query: str = "",
    section: str | None = None,
    grant_scheme: str | None = None,
    collection=None
) -> list[dict]:
    """Writing and editing agent: how good grants write a specific section."""
    where = _build_where(
        {"retrieval_intent": "style_example"},
        {"section_hint": section} if section else None,
        {"grant_scheme": grant_scheme} if grant_scheme else None,
    )
    search_query = query or f"grant writing style example {section or 'application section'}"
    return _search(search_query, where_filter=where, collection=collection)


def retrieve_funder_requirements(
    query: str = "",
    grant_scheme: str | None = None,
    section: str | None = None,
    collection=None
) -> list[dict]:
    """Requirements and verification agent: what the funder explicitly wants."""
    where = _build_where(
        {"retrieval_intent": "funder_requirement"},
        {"grant_scheme": grant_scheme} if grant_scheme else None,
        {"section_hint": section} if section else None,
    )
    search_query = query or f"funder requirements criteria scoring {section or ''}"
    return _search(search_query, where_filter=where, collection=collection)


def retrieve_evidence(
    query: str,
    collection=None
) -> list[dict]:
    """Research and verification agent: factual claims with numbers and evidence."""
    where = {"retrieval_intent": {"$in": ["factual_claim", "evidence"]}}
    return _search(query, where_filter=where, collection=collection)


def build_context_pack(
    task: str,
    grant_scheme: str | None = None,
    section: str | None = None
) -> dict:
    """Full context pack combining all retrieval types for orchestration."""
    collection = _get_collection()

    return {
        "task": task,
        "grant_scheme": grant_scheme,
        "section": section,
        "content": retrieve_content(task, section=section, grant_scheme=grant_scheme, collection=collection),
        "style_examples": retrieve_style_examples(query=task, section=section, grant_scheme=grant_scheme, collection=collection),
        "funder_requirements": retrieve_funder_requirements(query=task, grant_scheme=grant_scheme, section=section, collection=collection),
        "evidence": retrieve_evidence(task, collection=collection),
    }
