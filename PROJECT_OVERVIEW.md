# Project Overview

## Purpose

This project aims to build a local-first AI-assisted grant writing orchestration system capable of:

- understanding grant requirements
- retrieving relevant historical grant knowledge
- researching public information
- drafting structured grant responses
- verifying claims and evidence
- maintaining consistent grant-writing style
- reducing hallucinations
- protecting sensitive company information

The system is not intended to be a simple chatbot.

Instead, it is designed as a controlled orchestration platform using:
- retrieval systems
- vector databases
- local memory
- AI model routing
- verification workflows
- structured reasoning pipelines

---

# Core Design Philosophy

The project avoids directly training models on confidential grants.

Instead, it uses:
- Retrieval-Augmented Generation (RAG)
- embeddings
- semantic retrieval
- structured context orchestration

This allows:
- safer handling of private data
- easier updates to knowledge
- traceable evidence usage
- lower infrastructure costs
- stronger hallucination control

---

# Long-Term Goal

The intended end-state is an orchestration system capable of semi-autonomous grant generation.

Example workflow:

```text
Grant brief uploaded
↓
Requirement extraction
↓
Research planning
↓
Private vault retrieval
↓
Public evidence gathering
↓
Draft generation
↓
Claim verification
↓
Style editing
↓
Final review
```

The system should support:
- iterative drafting
- evidence-grounded writing
- modular AI workflows
- human review checkpoints
- multiple LLM providers
- local/private processing

---

# Why Local-First?

Grant writing often involves:
- commercial strategy
- internal financial information
- technical IP
- unpublished research
- customer data
- deployment plans

A core requirement is therefore:

```text
Private source documents should remain local whenever possible.
```

Cloud LLMs should only receive:
- approved summaries
- retrieval context
- non-sensitive guidance
- controlled evidence packs

---

# Current Development Stage

The current implementation focuses on the foundational retrieval layer.

Implemented so far:
- local document ingestion
- PDF/DOCX parsing
- semantic chunking
- embeddings via Ollama
- ChromaDB vector storage
- metadata-based retrieval
- structured retrieval context generation

This forms the memory system for later orchestration.

---

# Planned System Layers

## 1. Vault Layer

Stores:
- grants
- guidance
- templates
- research notes
- company documentation

Uses:
- ChromaDB
- embeddings
- metadata indexing

---

## 2. Retrieval Layer

Responsible for:
- semantic retrieval
- metadata filtering
- evidence grouping
- retrieval context generation

---

## 3. Research Layer

Responsible for:
- public research
- policy analysis
- funding landscape analysis
- evidence gathering
- citation tracking

---

## 4. Writing Layer

Responsible for:
- section drafting
- structure generation
- style consistency
- scoring alignment
- word count management

---

## 5. Verification Layer

Responsible for:
- claim checking
- hallucination reduction
- evidence validation
- unsupported claim detection
- consistency checking

---

## 6. Editing Layer

Responsible for:
- readability
- grant tone
- clarity
- grammar
- conciseness
- final polish

---

# OpenClaw Integration

OpenClaw is intended to act as the orchestration framework.

OpenClaw will:
- coordinate workflows
- call retrieval tools
- manage model routing
- execute research tasks
- trigger verification flows
- coordinate editing stages

The retrieval/database layer remains separate and protected.

---

# Key Principles

## Evidence Over Guessing

The system should retrieve and reason over evidence rather than invent information.

---

## Modular Workflows

Each stage should remain independently testable and replaceable.

---

## Human Oversight

The system should assist and accelerate grant writing, not remove human review entirely.

---

## Controlled Context

Large language models should receive:
- relevant
- structured
- traceable
- minimal necessary context

rather than entire raw document stores.

---

# Intended Outcome

The final project aims to become:

```text
A secure local-first AI grant orchestration platform
```

capable of:
- accelerating grant workflows
- maintaining writing consistency
- reducing repetitive work
- improving evidence handling
- reducing hallucinations
- supporting detailed multi-stage drafting pipelines