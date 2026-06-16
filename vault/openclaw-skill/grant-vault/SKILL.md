---
name: grant-vault
description: "Retrieve grant knowledge, evidence, style examples, and funder requirements from the local grant vault before writing any grant section."
metadata: {"openclaw":{"emoji":"🗄️"}}
---

# Grant Vault

The grant vault is a local REST API running at `http://localhost:8100`. It is a standard HTTP service — no MCP required.

## Active grant folder

Every grant session has a per-grant folder at `vault/grants/<slug>/`
(`C:\Users\User\OneDrive\Desktop\projects\Bontaic\vault\grants\<slug>\`),
created by `requirement-extraction`. It holds `requirements.json`,
`research.json`, `flags.json`, `review.md`, `sections/`, and `verification/`.
All grant skills — including sub-agents spawned for research, writing, and
verification — read and write inside this same folder using the slug
established at the start of the session. Don't ask which grant is active or
where to write output; it's this folder.

## How to call the vault

`web_fetch` blocks localhost by design. Use shell commands (curl or PowerShell) for all vault calls.

**GET request:**
```bash
curl http://localhost:8100/health
```

**POST request with JSON body:**
```bash
curl -s -X POST http://localhost:8100/context-pack \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"...\", \"grant_scheme\": \"innovate_uk\"}"
```

**On Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8100/context-pack" -Method POST -ContentType "application/json" -Body '{"task":"...","grant_scheme":"innovate_uk"}'
```

---

## Step 1 — Always check health first

```bash
curl http://localhost:8100/health
```

Expected response:
```json
{ "status": "ok", "ollama": "ok", "vault_chunks": 82 }
```

If `ollama` is not `"ok"` or `vault_chunks` is 0, stop and tell the user the vault is not ready.

---

## Step 2 — Primary retrieval

```bash
curl -s -X POST http://localhost:8100/context-pack \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"<task>\", \"grant_scheme\": \"innovate_uk\", \"section\": \"<section hint>\"}"
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

---

## Step 3 — Targeted search (when you need filtered results)

```bash
curl -s -X POST http://localhost:8100/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"<query>\", \"n_results\": 5, \"where_filter\": {\"is_funder_requirement\": \"true\"}}"
```

Useful filter fields (all values are strings, not booleans):

| Field | Use |
|---|---|
| `is_funder_requirement: "true"` | Only funder guidance chunks |
| `is_style_example: "true"` | Only chunks from successful applications |
| `is_evidence: "true"` | Only chunks with specific numbers/claims |
| `grant_scheme: "innovate_uk"` | Only chunks from a specific scheme |
| `section_hint: "innovation"` | Only chunks tagged to a specific section |

**Single filter:**
```json
"where_filter": { "is_funder_requirement": "true" }
```

**Multiple filters — must use `$and`:**
```json
"where_filter": { "$and": [{ "is_style_example": "true" }, { "grant_scheme": "innovate_uk" }] }
```

ChromaDB rejects flat dicts with more than one key — always use `$and` for combined filters.

---

## Compressed brief (slow — ~2 minutes)

Only use when you need a pre-summarised brief rather than raw chunks:

```bash
curl -s -X POST http://localhost:8100/brief \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"<task>\", \"grant_scheme\": \"innovate_uk\"}"
```

---

## Check what is in the vault

```bash
curl http://localhost:8100/stats
```

---

## Look up a specific chunk by source and index

```bash
curl "http://localhost:8100/chunk?source=filename.pdf&index=5"
```

Use this during verification to retrieve the exact source text for a cited claim.

---

## Rules

- Always check health before querying — use `curl http://localhost:8100/health`
- Always pass `grant_scheme` when the target scheme is known
- Do not treat retrieved chunks as verified company facts — they are reference material
- Do not claim specific outcomes unless the retrieved evidence explicitly supports them
- Cite the `source` filename when using specific evidence points in a draft
- If the vault returns empty results for a section, tell the user — do not invent content
- This is a local HTTP API, not MCP — use web_fetch directly
