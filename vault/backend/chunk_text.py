import re


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    text = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def detect_section(text: str) -> str:
    lower = text.lower()

    section_keywords = {
        "risk": "risk_mitigation",
        "mitigation": "risk_mitigation",
        "environment": "environmental_impact",
        "emissions": "environmental_impact",
        "carbon": "environmental_impact",
        "market": "market_need",
        "self-fund": "funding_justification",
        "cannot be funded": "funding_justification",
        "public fund": "funding_justification",
        "funding": "funding_justification",
        "commercial": "commercialisation",
        "impact": "impact",
        "benefit": "impact",
        "innovation": "innovation",
        "cost": "finance",
        "budget": "finance",
        "team": "team_capability",
        "management": "project_management",
        "work package": "project_management",
        "milestone": "project_management",
    }

    for keyword, section in section_keywords.items():
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