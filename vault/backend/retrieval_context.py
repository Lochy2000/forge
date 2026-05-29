from datetime import datetime
from pathlib import Path

from backend.config import OUTPUT_DIR
from backend.retrieval_engine import build_context_pack


def format_context_pack(pack: dict) -> str:
    task = pack["task"]
    grant_scheme = pack.get("grant_scheme") or "not specified"
    section = pack.get("section") or "not specified"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("# Retrieval Context Pack")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Task: {task}")
    lines.append(f"Grant scheme: {grant_scheme}")
    lines.append(f"Section: {section}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Key Caution Rules")
    lines.append("")
    lines.append("- Do not treat retrieved examples as company facts.")
    lines.append("- Do not claim measured outcomes unless the source explicitly supports them.")
    lines.append("- Do not turn general grant guidance into specific performance claims.")
    lines.append("- Preserve source references so claims can be checked later.")
    lines.append("")
    lines.append("---")
    lines.append("")

    sections = {
        "Content": pack.get("content", []),
        "Style Examples": pack.get("style_examples", []),
        "Funder Requirements": pack.get("funder_requirements", []),
        "Evidence": pack.get("evidence", []),
    }

    total_unique = sum(len(v) for v in sections.values())
    lines.append(f"Total retrieved chunks: {total_unique}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for section_name, items in sections.items():
        lines.append(f"## {section_name}")
        lines.append("")

        if not items:
            lines.append("No results found.")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue

        for index, item in enumerate(items, start=1):
            lines.append(f"### Result {index}")
            lines.append("")
            lines.append(f"- Source: `{item['source']}`")
            lines.append(f"- Chunk: `{item['chunk']}`")
            lines.append(f"- Document type: `{item['document_type']}`")
            lines.append(f"- Section hint: `{item['section_hint']}`")
            lines.append(f"- Retrieval intent: `{item.get('retrieval_intent', 'unknown')}`")
            lines.append(f"- Grant scheme: `{item.get('grant_scheme', 'unknown')}`")
            lines.append(f"- Distance: `{item['distance']}`")
            lines.append("")
            lines.append("```text")
            lines.append(item["content"][:1800])
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## Suggested Next Steps")
    lines.append("")
    lines.append("- Use content results to identify relevant evidence for this task.")
    lines.append("- Use style examples to understand how similar sections are written.")
    lines.append("- Use funder requirements to check what the funder explicitly wants.")
    lines.append("- Use evidence results to ground specific claims in retrieved facts.")
    lines.append("- Do not pass all raw chunks to a cloud model — compress first.")
    lines.append("")

    return "\n".join(lines)


def save_retrieval_context(task: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(
        char.lower() if char.isalnum() else "_"
        for char in task[:60]
    ).strip("_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"retrieval_context_{timestamp}_{safe_name}.md"
    file_path.write_text(content, encoding="utf-8")

    return file_path


def main():
    print("Retrieval Context Builder")
    print("Type 'exit' to quit.")

    while True:
        task = input("\nTask/query: ").strip()

        if task.lower() == "exit":
            break

        grant_scheme = input("Grant scheme (enter to skip): ").strip() or None
        section = input("Section hint (enter to skip): ").strip() or None

        pack = build_context_pack(task, grant_scheme=grant_scheme, section=section)
        content = format_context_pack(pack)
        output_path = save_retrieval_context(task, content)

        total = sum(len(pack[k]) for k in ["content", "style_examples", "funder_requirements", "evidence"])
        print(f"\nContext pack created — {total} chunks across 4 retrieval types")
        print(output_path)


if __name__ == "__main__":
    main()
