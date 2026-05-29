---
name: requirement-extraction
description: "Extract structured requirements from a grant brief — scoring criteria, sections, word limits, eligibility, and evidence needed. Always run this first before any grant writing task."
metadata: {"openclaw":{"emoji":"📋"}}
---

# Requirement Extraction

Extract all requirements from a grant brief before any writing begins. The output is a structured JSON file that every other grant skill references throughout the session.

## When to use

Run this skill first, before calling the vault or drafting anything. Every other skill depends on this output.

## Accepted inputs

- **Pasted text** — user pastes the grant brief or call document directly
- **Uploaded file** — user provides a PDF or document path
- **URL** — fetch the grant opportunity page using web fetch

If the input is a file path, read the file. If it is a URL, fetch the page content. If it is pasted text, use it directly.

## Extraction process

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

## Output format

Output a single JSON object. Do not add commentary around it — output the JSON directly.

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
      "red_flags": []
    }
  ],
  "evidence_needed": [],
  "disqualifiers": []
}
```

## After extraction

Once the JSON is complete:

1. **Save it** to a file called `grant-requirements.json` in the current workspace directory.

2. **Check the vault** — call `GET http://localhost:8100/stats` and report back:
   - Whether the vault contains documents for this `grant_scheme`
   - How many chunks are available
   - If the scheme is not in the vault, warn the user that vault context will be limited

3. **Summarise for the user** — present a short plain-English summary of:
   - What the grant is for
   - Key eligibility points
   - The sections that need writing and their word limits
   - Any immediate red flags or concerns

4. **Ask the user** — confirm before proceeding:
   - Is any information missing or unclear from the brief?
   - Are there additional documents (e.g. company information, previous applications) to add to the vault before writing begins?

## Rules

- If the brief is ambiguous about a requirement, note it explicitly in the summary — do not guess.
- If a word limit is not stated, leave `word_limit` as null — do not invent one.
- If the deadline is not stated, leave it blank — do not assume.
- Do not begin drafting any section until the user confirms the extraction is correct.
- `grant-requirements.json` is the single source of truth for this grant session — other skills read it.
