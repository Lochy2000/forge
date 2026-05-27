from pathlib import Path
from pypdf import PdfReader
from docx import Document


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def read_docx(path: Path) -> str:
    doc = Document(str(path))

    return "\n".join(
        [p.text for p in doc.paragraphs if p.text.strip()]
    )


def read_txt(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return read_pdf(path)

    if suffix == ".docx":
        return read_docx(path)

    if suffix in [".txt", ".md"]:
        return read_txt(path)

    return ""