from datetime import datetime
from pathlib import Path

from backend.config import OUTPUT_DIR
from backend.search import search_vault, format_results


def deduplicate_results(results: list[dict]) -> list[dict]:
    seen = set()
    unique = []

    for item in results:
        key = (
            item.get("source"),
            item.get("chunk"),
            item.get("content")[:120]
        )

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


def run_context_searches(task: str) -> dict:
    """
    Runs several targeted retrieval searches for one grant-writing task.
    This is not the final agent workflow yet.
    It is the local retrieval/context layer that OpenClaw can later call.
    """

    searches = [
        {
            "label": "General relevant context",
            "query": task,
            "filter": None,
            "n_results": 5,
        },
        {
            "label": "Grant guidance",
            "query": task,
            "filter": {"document_type": "grant_guidance"},
            "n_results": 5,
        },
        {
            "label": "Grant application examples",
            "query": task,
            "filter": {"document_type": "grant_application"},
            "n_results": 5,
        },
    ]

    lower_task = task.lower()

    if any(word in lower_task for word in ["environment", "carbon", "emissions", "sustainability"]):
        searches.append({
            "label": "Environmental impact context",
            "query": task,
            "filter": {"section_hint": "environmental_impact"},
            "n_results": 5,
        })

    if any(word in lower_task for word in ["risk", "mitigation", "uncertainty"]):
        searches.append({
            "label": "Risk mitigation context",
            "query": task,
            "filter": {"section_hint": "risk_mitigation"},
            "n_results": 5,
        })

    grouped_results = {}

    for search in searches:
        raw_results = search_vault(
            query=search["query"],
            n_results=search["n_results"],
            where_filter=search["filter"]
        )

        grouped_results[search["label"]] = format_results(raw_results)

    return grouped_results


def build_retrieval_context(task: str) -> str:
    grouped_results = run_context_searches(task)

    all_items = []

    for items in grouped_results.values():
        all_items.extend(items)

    unique_items = deduplicate_results(all_items)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    lines.append("# Retrieval Context Pack")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append("")
    lines.append("## Task")
    lines.append("")
    lines.append(task)
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This pack organises retrieved grant evidence and guidance for one specific writing or research task. "
        "It is designed to support later planning, drafting, checking, and OpenClaw orchestration without sending the full document vault to a model."
    )
    lines.append("")

    lines.append("## Retrieval Summary")
    lines.append("")
    lines.append(f"Total unique retrieved chunks: {len(unique_items)}")
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

    for group_name, items in grouped_results.items():
        lines.append(f"## {group_name}")
        lines.append("")

        if not items:
            lines.append("No results found.")
            lines.append("")
            continue

        for index, item in enumerate(items, start=1):
            lines.append(f"### Result {index}")
            lines.append("")
            lines.append(f"- Source: `{item['source']}`")
            lines.append(f"- Chunk: `{item['chunk']}`")
            lines.append(f"- Document type: `{item['document_type']}`")
            lines.append(f"- Section hint: `{item['section_hint']}`")
            lines.append(f"- Sensitivity: `{item['sensitivity']}`")
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
    lines.append("- Use this pack to identify useful evidence, style patterns, and missing information.")
    lines.append("- Do not pass all raw chunks to a cloud model unless needed.")
    lines.append("- For cloud writing, compress this pack into a smaller brief first.")
    lines.append("- For verification, keep the exact source/chunk references.")
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

        context = build_retrieval_context(task)
        output_path = save_retrieval_context(task, context)

        print("\nRetrieval context created:")
        print(output_path)


if __name__ == "__main__":
    main()