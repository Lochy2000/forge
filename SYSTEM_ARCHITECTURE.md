# System Architecture

# High-Level Architecture

```text
User
│
▼
OpenClaw Orchestration Layer
│
├── Requirement Extraction
├── Research Planning
├── Retrieval Context Builder
├── Public Research Agent
├── Writing Agent
├── Verification Agent
└── Editing Agent
│
▼
Retrieval & Memory Layer
│
├── ChromaDB
├── Embeddings
├── Metadata Indexing
└── Retrieval Context Generation
│
▼
Local Vault
│
├── Historical Grants
├── Guidance Documents
├── Templates
├── Research Notes
├── Company Information
└── Evidence Sources
```

---

# Core Technologies

## Local Processing

- Python
- Ollama
- ChromaDB
- Local filesystem storage

---

## AI Models

Potential providers:
- OpenAI
- Anthropic
- OpenRouter
- Ollama local models

---

## Orchestration

- OpenClaw

---

# Current Retrieval Pipeline

```text
Document
↓
Text Extraction
↓
Chunking
↓
Embedding Generation
↓
Vector Storage
↓
Metadata Indexing
↓
Semantic Retrieval
↓
Retrieval Context Generation
```

---

# Why Vector Search?

Traditional keyword search struggles with:
- different terminology
- grant phrasing variation
- semantic meaning
- broad contextual searches

Embeddings allow:
- meaning-based retrieval
- semantic similarity
- context-aware searches

Example:

```text
"environmental impact"
```

can retrieve:
- sustainability benefits
- emissions reductions
- biodiversity impacts
- waste reduction

without exact keyword matches.

---

# Metadata Strategy

Metadata is critical for:
- filtering
- retrieval quality
- security
- orchestration

Current metadata examples:

```json
{
  "source": "grant.pdf",
  "document_type": "grant_application",
  "section_hint": "environmental_impact",
  "sensitivity": "public_test"
}
```

Future metadata may include:
- grant success/failure
- company
- project type
- confidentiality level
- funding programme
- scoring category

---

# Retrieval Context Layer

The retrieval context layer:
- organises retrieved evidence
- groups relevant examples
- preserves source traceability
- reduces noisy context
- prepares evidence for AI reasoning

This is not simply summarisation.

It acts as:
- evidence orchestration
- context management
- retrieval structuring

---

# Long-Term Workflow

## 1. Requirement Analysis

Extract:
- scoring criteria
- sections
- eligibility
- risks
- evidence requirements

---

## 2. Retrieval

Retrieve:
- historical examples
- style patterns
- company evidence
- related guidance

---

## 3. Research

Collect:
- public evidence
- policy references
- market context
- supporting data

---

## 4. Drafting

Generate:
- structured responses
- aligned with scoring criteria
- using evidence-grounded context

---

## 5. Verification

Check:
- unsupported claims
- hallucinations
- missing evidence
- inconsistent statements

---

## 6. Editing

Improve:
- readability
- tone
- structure
- clarity
- conciseness

---

# Security Model

## Local-First Principle

Sensitive materials should remain local whenever possible.

---

## Controlled Cloud Usage

Cloud LLMs should only receive:
- approved retrieval context
- sanitised summaries
- non-sensitive evidence

---

## Human Review

Final outputs should remain reviewable and editable by humans before submission.