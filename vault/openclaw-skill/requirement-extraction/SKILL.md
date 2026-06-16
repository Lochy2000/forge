---
name: requirement-extraction
description: "Extract structured requirements from a grant brief — scoring criteria, sections, word limits, eligibility, and evidence needed. Always run this first before any grant writing task."
metadata: {"openclaw":{"emoji":"📋"}}
---

# Requirement Extraction

Extract all requirements from a grant brief before any writing begins. The output is a structured JSON file that every other grant skill references throughout the session, inside a per-grant folder that every other skill also writes into.

## When to use

Run this skill first, before calling the vault or drafting anything. Every other skill depends on this output and on the grant folder it creates.

## Accepted inputs

- **Pasted text** — user pastes the grant brief or call document directly
- **Uploaded file** — user provides a PDF or document path
- **URL** — fetch the grant opportunity page using web fetch

If the input is a file path, read the file. If it is a URL, fetch the page content. If it is pasted text, use it directly.

## Step 1 — Determine the grant slug and create the grant folder

Derive a short, memorable, kebab-case slug from the project/company name, e.g.
`thermasync-tlsc`. If the project name alone would be ambiguous or ugly as a
slug (too generic, or collides with an existing folder under
`vault/grants/`), combine it with a distinguishing acronym or the funder name.

**This is the one question worth asking up front if genuinely unclear** —
e.g. if no project/company name appears anywhere in the brief. Otherwise,
pick a reasonable slug yourself and proceed; it can be renamed later by
renaming the folder.

Create this structure under `vault/grants/<slug>/` (the Bontaic repo, at
`C:\Users\User\OneDrive\Desktop\projects\Bontaic\vault\grants\<slug>\`):

```
vault/grants/<slug>/
├── flags.json          (seed with {"grant_slug": "<slug>", "flags": []})
├── sections/            (empty — grant-writing fills this in)
└── verification/        (empty — grant-verification fills this in)
```

`requirements.json` itself is written in Step 4. Every later skill in this
session (research, writing, verification, editing, review) reuses this same
`<slug>` and folder — do not re-ask which grant is active.

## Step 2 — Extraction process

Read the full brief carefully. Extract the following:

### 1. Top-level information
- Grant name and round (if specified)
- Funder organisation
- Grant scheme — map to one of: `innovate_uk` / `communities_fund` / `horizon_europe` / `unknown`
- Application deadline
- Funding range (min/max if given)
- Funding percentage (what % of project costs the grant covers)
- Project duration limits

### 2. Eligibility
List every eligibility criterion explicitly stated. Include:
- Organisation type (SME, charity, university etc)
- Location requirements
- TRL or readiness level requirements
- Sector restrictions
- Partnership requirements
- Anything that would disqualify an applicant

### 3. Sections
For every section the application requires, extract:
- Section name (as written in the brief)
- `section_hint` — map to the closest value from this list:
  `innovation` / `environmental_impact` / `risk_mitigation` / `market_need` /
  `funding_justification` / `team_capability` / `project_management` /
  `finance` / `impact` / `commercialisation`
  Use `general` if none fit.
- Word or character limit (if stated)
- Scoring weight or marks available (if stated)
- Key requirements — what the funder explicitly says they want to see in this section
- Red flags — things the brief warns will score poorly

### 4. Evidence needed
List specific types of evidence the brief asks for across all sections:
- Market data or statistics
- Technical validation
- Team credentials
- Financial information
- Letters of support
- Partnership agreements

### 5. Disqualifiers
Hard rules that would invalidate the application:
- Work that has already started
- Retrospective costs
- Ineligible cost categories
- Missing mandatory attachments

## Step 3 — Output format

Build a single JSON object. Each section gets a `status` field, initialised
to `"pending"` — later skills update this to `drafted` / `verified` /
`needs_revision` / `approved`.

```json
{
  "grant_name": "",
  "funder": "",
  "grant_scheme": "",
  "deadline": "",
  "funding_range": "",
  "funding_percentage": "",
  "duration_limit": "",
  "eligibility": [],
  "sections": [
    {
      "name": "",
      "section_hint": "",
      "word_limit": null,
      "scoring_weight": "",
      "key_requirements": [],
      "red_flags": [],
      "status": "pending"
    }
  ],
  "evidence_needed": [],
  "disqualifiers": []
}
```

## Step 4 — Save and initialise the grant folder

1. **Save the JSON** to `vault/grants/<slug>/requirements.json`.

2. **Check the vault** — call `GET http://localhost:8100/stats` and report back:
   - Whether the vault contains documents for this `grant_scheme`
   - How many chunks are available
   - If the scheme is not in the vault, warn the user that vault context will be limited

3. **Summarise for the user** — present a short plain-English summary of:
   - The grant slug and folder you created
   - What the grant is for
   - Key eligibility points
   - The sections that need writing and their word limits
   - Any immediate red flags or concerns

4. **Log gaps, don't ask** — for anything ambiguous, missing, or guessed
   (e.g. no word limit stated, scheme unclear, deadline missing), append an
   entry to `vault/grants/<slug>/flags.json`:
   ```json
   {
     "id": "flag-001",
     "timestamp": "<ISO timestamp>",
     "skill": "requirement-extraction",
     "section": "<section name or null for top-level>",
     "category": "extraction_gap",
     "description": "<what was ambiguous/missing>",
     "default_action_taken": "Left as null/\"unknown\" — see field <x>",
     "severity": "low",
     "needs_human_review": true,
     "resolved": false
   }
   ```
   Then proceed straight to research/writing — do not stop to ask whether
   the extraction is correct. The consolidated `grant-review` step at the end
   of the pipeline is where the user reviews all logged gaps at once.

## Rules

- If the brief is ambiguous about a requirement, leave the field
  `null`/`"unknown"` and log a `flags.json` entry — do not guess a value, but
  also do not stop and ask.
- If a word limit is not stated, leave `word_limit` as null — `grant-writing`
  applies a documented default and logs its own flag.
- If the deadline is not stated, leave it blank — do not assume.
- `requirements.json` is the single source of truth for this grant session —
  other skills read and update it (especially the per-section `status` field).
- `flags.json` is the running log for this grant — only the orchestrator
  appends to it; sub-agents return flag data in their results instead of
  writing the file directly.
