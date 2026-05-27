# Grant Vault Backend

## Overview

This backend is the foundation of a local-first AI grant writing system.

The current system focuses on one core problem:

> How can grant documents be stored, searched, and retrieved semantically without training a model directly on sensitive company data?

Instead of fine-tuning a model on private grant applications, this backend uses a Retrieval-Augmented Generation (RAG) approach.

The system:

```text
Documents
→ text extraction
→ chunking
→ embeddings
→ vector storage
→ semantic retrieval
```

This allows the project to:
- search grants by meaning rather than keywords
- retrieve relevant examples and evidence
- keep private data local
- support larger external LLMs safely later on
- reduce hallucinations by grounding responses in stored evidence

---

# Current Architecture

```text
vault/
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── extract_text.py
│   ├── chunk_text.py
│   ├── ollama_embed.py
│   ├── ingest.py
│   ├── search.py
│   └── reset_db.py
│
├── chroma_db/
│
├── docs/
│
└── output/
```

---

# Core Concepts

## What is RAG?

RAG stands for:

```text
Retrieve
→ Augment
→ Generate
```

Instead of relying on a model's memory alone, the system retrieves relevant document chunks first and provides them as context to the AI.

This is important because:
- grants require factual accuracy
- unsupported claims are dangerous
- private company information should remain local
- funder requirements vary heavily between applications

---

# Why Embeddings?

Embeddings convert text into numerical vectors representing semantic meaning.

Example:

```text
"environmental impact"
```

and:

```text
"carbon reduction benefits"
```

will produce similar vectors even though the wording differs.

This allows semantic search rather than simple keyword matching.

---

# Why a Vector Database?

Traditional databases search exact text.

A vector database searches meaning.

ChromaDB stores:
- text chunks
- embedding vectors
- metadata

This enables:
- semantic retrieval
- similarity search
- contextual memory
- scalable knowledge storage

---

# Current Workflow

## 1. Documents are added to `/docs`

Supported formats:
- PDF
- DOCX
- TXT
- Markdown

These can include:
- grant applications
- guidance documents
- templates
- writing examples
- checklists

---

## 2. `extract_text.py`

Responsible for:
- reading files
- extracting raw text

Uses:
- `pypdf`
- `python-docx`

The goal is to convert all supported documents into plain text.

---

## 3. `chunk_text.py`

Large documents are split into smaller chunks.

Why?

LLMs and embeddings work better on smaller sections of text.

Current implementation:
- simple character chunking
- overlapping chunks

Example:

```text
chunk size: 1200
overlap: 200
```

Overlap helps preserve context between chunks.

---

## 4. `ollama_embed.py`

Handles local embeddings through Ollama.

Current embedding model:

```text
nomic-embed-text
```

The script:
- sends text to Ollama
- receives embedding vectors
- returns them to the pipeline

This keeps embeddings fully local.

---

## 5. `ingest.py`

Main ingestion pipeline.

Responsible for:

```text
documents
→ extraction
→ chunking
→ embedding
→ vector storage
```

Process:
1. scan `/docs`
2. extract text
3. split into chunks
4. generate embeddings
5. store in ChromaDB

Stored data includes:
- chunk text
- embedding vector
- metadata

---

## 6. `search.py`

Performs semantic retrieval.

Workflow:

```text
user query
→ query embedding
→ vector similarity search
→ retrieve relevant chunks
```

This allows searches like:

```text
"risk mitigation examples"
```

without requiring exact wording matches.

---

## 7. `reset_db.py`

Deletes the local ChromaDB database.

Useful during:
- testing
- re-ingestion
- chunking experiments
- metadata changes

---

# Why Local First?

The system is intentionally local-first because grant writing often involves:
- sensitive company data
- commercial strategy
- private financial information
- confidential technical details

The long-term architecture aims to ensure:
- raw documents remain local
- only approved summaries leave the system
- cloud LLMs never directly access the vault

---

# Current Limitations

The current version is intentionally simple.

Limitations:
- basic chunking only
- no reranking
- minimal metadata
- no structured retrieval
- no claim verification
- no summarisation layer
- no OpenClaw integration yet

---

# Planned Next Steps

## Better Chunking
Move from character chunking to:
- heading-aware chunking
- section-aware chunking
- grant-question-aware chunking

---

## Metadata Expansion

Future metadata examples:

```json
{
  "grant_type": "Innovate UK",
  "section": "Environmental Benefits",
  "success": true,
  "sensitivity": "private"
}
```

This will improve retrieval quality significantly.

---

## Safe Context Packs

Future retrieval will produce structured outputs such as:

```text
APPROVED FACTS
STYLE EXAMPLES
SUPPORTED CLAIMS
DO NOT CLAIM
RISK FLAGS
```

This becomes the bridge between:
- private vault
- external LLMs

---

## OpenClaw Integration

Planned architecture:

```text
OpenClaw
→ retrieval skill
→ safe context generation
→ writing agents
→ verification agents
```

OpenClaw will orchestrate workflows, while the vault remains the protected knowledge layer.

---

# Long-Term Goal

The long-term aim is to create:

```text
A secure local-first automated grant writing assistant
```

capable of:
- understanding grant requirements
- retrieving relevant company knowledge
- generating structured drafts
- verifying claims
- maintaining consistent grant-writing style
- reducing hallucinations
- protecting sensitive information

without requiring expensive fine-tuning pipelines.