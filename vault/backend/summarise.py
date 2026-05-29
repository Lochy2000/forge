import json
import re
import requests

from backend.config import OLLAMA_CHAT_URL, GENERATIVE_MODEL


# --- Ollama call ---

def _call_model(prompt: str) -> str:
    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": GENERATIVE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


# --- JSON extraction ---

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "Could not parse model response", "raw": text[:500]}


# --- Chunk formatting ---

def _format_chunks(chunks: list[dict], max_chunks: int = 5, max_chars: int = 500) -> str:
    top = sorted(chunks, key=lambda r: (r.get("distance") is None, r.get("distance")))[:max_chunks]
    parts = []
    for i, chunk in enumerate(top, 1):
        source = chunk.get("source", "unknown")
        text = chunk.get("content", "")[:max_chars]
        parts.append(f"[{i}] Source: {source}\n{text}")
    return "\n\n".join(parts)


# --- Compression functions ---

def compress_funder_requirements(chunks: list[dict], task: str) -> dict:
    if not chunks:
        return {"requirements": [], "scoring_criteria": [], "key_warnings": []}

    prompt = f"""You are helping prepare a grant application for this task: {task}

Extract the key requirements from these funder guidance chunks.
Respond with ONLY valid JSON in this exact format:
{{"requirements": ["requirement 1"], "scoring_criteria": ["criterion 1"], "key_warnings": ["warning 1"]}}

Chunks:
{_format_chunks(chunks)}"""

    return _extract_json(_call_model(prompt))


def compress_evidence(chunks: list[dict], task: str) -> dict:
    if not chunks:
        return {"evidence_points": []}

    prompt = f"""You are helping prepare a grant application for this task: {task}

Extract specific factual claims and evidence points with their sources.
Respond with ONLY valid JSON in this exact format:
{{"evidence_points": [{{"claim": "specific claim here", "source": "filename.pdf"}}]}}

Chunks:
{_format_chunks(chunks)}"""

    return _extract_json(_call_model(prompt))


def compress_style_examples(chunks: list[dict], task: str) -> dict:
    if not chunks:
        return {"patterns": [], "tone_observations": [], "structural_notes": []}

    prompt = f"""You are helping prepare a grant application for this task: {task}

Identify specific writing patterns and techniques from these successful grant sections.
Respond with ONLY valid JSON in this exact format:
{{"patterns": ["pattern 1"], "tone_observations": ["observation 1"], "structural_notes": ["note 1"]}}

Chunks:
{_format_chunks(chunks)}"""

    return _extract_json(_call_model(prompt))


def compress_content(chunks: list[dict], task: str) -> dict:
    if not chunks:
        return {"key_points": [], "supporting_context": []}

    prompt = f"""You are helping prepare a grant application for this task: {task}

Summarise the key information relevant to this task.
Respond with ONLY valid JSON in this exact format:
{{"key_points": ["point 1"], "supporting_context": ["context 1"]}}

Chunks:
{_format_chunks(chunks)}"""

    return _extract_json(_call_model(prompt))


# --- Full pack compression ---

def compress_context_pack(pack: dict) -> dict:
    task = pack.get("task", "")

    return {
        "task": task,
        "grant_scheme": pack.get("grant_scheme"),
        "section": pack.get("section"),
        "funder_requirements": compress_funder_requirements(pack.get("funder_requirements", []), task),
        "evidence": compress_evidence(pack.get("evidence", []), task),
        "style_examples": compress_style_examples(pack.get("style_examples", []), task),
        "content": compress_content(pack.get("content", []), task),
    }


# --- Markdown formatter for human review ---

def to_markdown(compressed: dict) -> str:
    lines = []
    lines.append("# Compressed Context Brief")
    lines.append(f"\n**Task:** {compressed.get('task', '')}")
    if compressed.get("grant_scheme"):
        lines.append(f"**Grant scheme:** {compressed['grant_scheme']}")
    if compressed.get("section"):
        lines.append(f"**Section:** {compressed['section']}")
    lines.append("\n---\n")

    funder = compressed.get("funder_requirements", {})
    lines.append("## Funder Requirements")
    for r in funder.get("requirements", []):
        lines.append(f"- {r}")
    if funder.get("scoring_criteria"):
        lines.append("\n**Scoring criteria:**")
        for c in funder["scoring_criteria"]:
            lines.append(f"- {c}")
    if funder.get("key_warnings"):
        lines.append("\n**Key warnings:**")
        for w in funder["key_warnings"]:
            lines.append(f"- {w}")
    lines.append("")

    evidence = compressed.get("evidence", {})
    lines.append("## Key Evidence")
    for point in evidence.get("evidence_points", []):
        lines.append(f"- {point.get('claim')} *(source: {point.get('source')})*")
    lines.append("")

    style = compressed.get("style_examples", {})
    lines.append("## Style Observations")
    for p in style.get("patterns", []):
        lines.append(f"- {p}")
    for o in style.get("tone_observations", []):
        lines.append(f"- {o}")
    if style.get("structural_notes"):
        lines.append("\n**Structural notes:**")
        for n in style["structural_notes"]:
            lines.append(f"- {n}")
    lines.append("")

    content = compressed.get("content", {})
    lines.append("## Key Content Points")
    for point in content.get("key_points", []):
        lines.append(f"- {point}")
    if content.get("supporting_context"):
        lines.append("\n**Supporting context:**")
        for c in content["supporting_context"]:
            lines.append(f"- {c}")
    lines.append("")

    return "\n".join(lines)
