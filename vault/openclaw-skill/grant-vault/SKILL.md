---
name: grant-vault
description: "Retrieve grant knowledge, evidence, style examples, and funder requirements from the local grant vault before writing any grant section."
metadata: {"openclaw":{"emoji":"🗄️"}}
---

# Grant Vault

The grant vault is a local knowledge base of grant documents, guidance, and successful applications. Always query it before drafting any grant section. It runs as a local API at `http://localhost:8100`.

## Before anything else — check health

```
GET http://localhost:8100/health
```

If `ollama` is not `"ok"` or `vault_chunks` is 0, stop and tell the user the vault is not running. Do not attempt to write grant content without vault context.

## Primary retrieval — use this for most tasks

```
POST http://localhost:8100/context-pack
{
  "task": "<describe the grant writing task>",
  "grant_scheme": "<scheme or omit>",
  "section": "<section hint or omit>"
}
```

Valid `grant_scheme` values: `innovate_uk` `communities_fund` `horizon_europe` `internal` `unknown`

Valid `section` values: `innovation` `environmental_impact` `risk_mitigation` `market_need` `funding_justification` `team_capability` `project_management` `finance` `impact` `commercialisation`

The response contains four groups — use each for a different purpose:

| Group | Use for |
|---|---|
| `funder_requirements` | What the funder explicitly wants — check this first |
| `style_examples` | How successful applications write this section — imitate the structure and tone |
| `evidence` | Specific facts and numbers with sources — cite these directly |
| `content` | General relevant context — background and supporting information |

## Compressed brief — use when you need a concise summary

```
POST http://localhost:8100/brief
{
  "task": "<describe the grant writing task>",
  "grant_scheme": "<scheme or omit>"
}
```

This calls a local LLM to compress the context. **Expect ~2 minutes.** Only use when you need a pre-summarised brief rather than raw chunks. Set request timeout to 300 seconds.

Response shape:
```json
{
  "funder_requirements": { "requirements": [...], "scoring_criteria": [...], "key_warnings": [...] },
  "evidence": { "evidence_points": [{ "claim": "...", "source": "filename" }] },
  "style_examples": { "patterns": [...], "tone_observations": [...], "structural_notes": [...] },
  "content": { "key_points": [...], "supporting_context": [...] }
}
```

## Targeted search — use when you need specific filtered results

```
POST http://localhost:8100/search
{
  "query": "<search query>",
  "n_results": 5,
  "where_filter": { "is_funder_requirement": "true" }
}
```

Useful filter fields (all values are strings, not booleans):

| Field | Use |
|---|---|
| `is_funder_requirement: "true"` | Only funder guidance chunks |
| `is_style_example: "true"` | Only chunks from successful applications |
| `is_evidence: "true"` | Only chunks with specific numbers/claims |
| `grant_scheme: "innovate_uk"` | Only chunks from a specific scheme |
| `section_hint: "innovation"` | Only chunks tagged to a specific section |

## What's in the vault

```
GET http://localhost:8100/stats
```

Shows total chunks, grant schemes loaded, document types, and source filenames. Check this if you are unsure what the vault contains before querying.

## Rules

- Always check health before querying.
- Always pass `grant_scheme` when the target scheme is known — this prevents style examples from one scheme contaminating results for another.
- Do not treat retrieved chunks as verified company facts — they are reference material.
- Do not claim specific outcomes unless the retrieved evidence explicitly supports them.
- Cite the `source` filename when using specific evidence points in a draft.
- If the vault returns empty results for a section, tell the user — do not invent content.
