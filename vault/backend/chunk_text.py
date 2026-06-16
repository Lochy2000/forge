import re


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    text = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


_HEADING_PATTERNS = [
    (r"innovation|technical approach|state of the art|novel", "innovation"),
    (r"market need|market opportunity|route to market|commerciali", "market_need"),
    (r"team capability|team and|key personnel|project team", "team_capability"),
    (r"environmental impact|environmental benefit|net zero|carbon|sustainability", "environmental_impact"),
    (r"risk mitigation|risk management|risk register", "risk_mitigation"),
    (r"need for public fund|public funding|additionality|grant justif", "funding_justification"),
    (r"financial summary|value for money|budget|project cost", "finance"),
    (r"project management|work package|milestone|deliverable|gantt", "project_management"),
    (r"wider impact|economic impact|social impact|benefit", "impact"),
    (r"commerciali|route to market|exploitation", "commercialisation"),
]

_KEYWORD_SECTION = {
    "risk": "risk_mitigation",
    "mitigation": "risk_mitigation",
    "emissions": "environmental_impact",
    "carbon": "environmental_impact",
    "self-fund": "funding_justification",
    "cannot be funded": "funding_justification",
    "public fund": "funding_justification",
    "funding": "funding_justification",
    "innovation": "innovation",
    "novel": "innovation",
    "market": "market_need",
    "commercial": "commercialisation",
    "budget": "finance",
    "team": "team_capability",
    "work package": "project_management",
    "milestone": "project_management",
    "impact": "impact",
    "benefit": "impact",
}


def detect_section(text: str) -> str:
    lower = text.lower()

    # Pass 1 — find markdown headings (## Heading) and use the last one
    headings = re.findall(r"#{1,4}\s+(.+)", lower)
    for heading in reversed(headings):
        for pattern, section in _HEADING_PATTERNS:
            if re.search(pattern, heading):
                return section

    # Pass 2 — keyword scan on full chunk text
    for keyword, section in _KEYWORD_SECTION.items():
        if keyword in lower:
            return section

    return "general"


def chunk_text(
    text: str,
    max_chars: int = 1600,
    overlap_sentences: int = 2
) -> list[dict]:
    text = normalise_text(text)
    sentences = split_into_sentences(text)

    chunks = []
    current = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        if current_size + sentence_size > max_chars and current:
            chunk_value = " ".join(current).strip()

            chunks.append({
                "text": chunk_value,
                "section_hint": detect_section(chunk_value)
            })

            overlap = current[-overlap_sentences:] if overlap_sentences else []
            current = overlap.copy()
            current_size = sum(len(s) for s in current)

        current.append(sentence)
        current_size += sentence_size

    if current:
        chunk_value = " ".join(current).strip()

        chunks.append({
            "text": chunk_value,
            "section_hint": detect_section(chunk_value)
        })

    return chunks