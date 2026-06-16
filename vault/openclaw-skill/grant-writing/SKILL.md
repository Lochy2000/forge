---
name: grant-writing
description: "Draft grant application sections using vault-retrieved evidence, funder requirements, and style examples from successful applications. Always run requirement-extraction first."
metadata: {"openclaw":{"emoji":"✍️"}}
---

# Grant Writing

Draft individual grant sections grounded in vault-retrieved evidence. Each section is written one at a time, checked against funder requirements, and self-assessed before delivery.

## Delegation

Run each section as its own `sessions_spawn` call to
`model: "anthropic/claude-opus-4-7"`, `context: "isolated"`. One spawn per
section — up to `maxConcurrent` sections can run in parallel.

The spawn prompt must include: the grant slug and folder path
(`vault/grants/<slug>/`), the section `name` (so the sub-agent can find its
spec in `requirements.json`), and an instruction to write the finished draft
to `vault/grants/<slug>/sections/qN-<name>.md`. The sub-agent does its own
vault context-pack retrieval (Step 2 below) — the orchestrator does not
pre-fetch it.

Each sub-agent returns to the orchestrator: the word count, sources used,
any gaps/placeholders, the requirements check, and any `flags.json` entries
it generated (see Steps 1, 2, 3, 4 below). The orchestrator appends these to
`vault/grants/<slug>/flags.json` and updates `requirements.json`'s `status`
field for that section.

## Prerequisites

Before running this skill:
1. `vault/grants/<slug>/requirements.json` must exist — run `requirement-extraction` first
2. The vault must be running — check `GET http://localhost:8100/health`
3. The spawn prompt specifies which section to write

Read `requirements.json` at the start of every writing task. Do not rely on memory of previous turns.

## Per-section workflow

### Step 1 — Load section spec

Read `requirements.json` and find the target section. Extract: section name,
`section_hint`, word limit, scoring weight, key requirements, red flags.

**If `word_limit` is null**, do not stop and ask. Apply a default instead:
- `innovate_uk` sections: 400 words (check `style_examples` from the
  context-pack first in Step 2 — if a clearer scheme-specific figure is
  visible there, use that instead and note it in the flag).
- All other schemes / `unknown`: 500 words.

If a default was applied, prepare a `flags.json` entry to return:
```json
{
  "timestamp": "<ISO timestamp>",
  "skill": "grant-writing",
  "section": "<section name>",
  "category": "missing_word_limit",
  "description": "No word_limit in requirements.json for this section.",
  "default_action_taken": "Used 400-word target (innovate_uk default).",
  "severity": "low",
  "needs_human_review": true,
  "resolved": false
}
```

Use this as the working word limit for Steps 5-6.

### Step 2 — Retrieve vault context

Call the vault context pack for this section:

```
POST http://localhost:8100/context-pack
{
  "task": "Write the [section name] section for a [grant_name] application",
  "grant_scheme": "[grant_scheme from requirements.json]",
  "section": "[section_hint]"
}
```

Assess what came back before drafting:

| Group | What to check |
|---|---|
| `funder_requirements` | Are there specific scoring criteria? Note them — the draft must address every one |
| `style_examples` | How do successful applications structure and open this section? Note the patterns |
| `evidence` | What specific facts and numbers are available? List usable evidence points |
| `content` | What general context is relevant? Use for background and framing |

**If any group returns 0 results, or distances are consistently above 350**,
do not stop and ask. Note it, proceed with what's available, and add a
`flags.json` entry:
```json
{
  "timestamp": "<ISO timestamp>",
  "skill": "grant-writing",
  "section": "<section name>",
  "category": "evidence_gap",
  "description": "context-pack returned 0 results for group '<group>' (or: weak matches, distances > 350)",
  "default_action_taken": "Drafted using remaining groups; weak areas use [INSERT: ...] placeholders",
  "severity": "low",
  "needs_human_review": false,
  "resolved": false
}
```

### Step 3 — Score alignment check (before drafting)

Before writing, map each key requirement to a scoring approach. For each requirement in the section spec, ask:

- What does a score of 4 (excellent) look like for this requirement?
- What evidence from the vault or research pack supports hitting that score?
- What is missing that would prevent a top score?

Build a brief scoring plan:
```
Requirement: "Demonstrate innovation beyond state of the art"
Score 4 needs: Named competitors + specific quantified advance + cited source
Available evidence: [LIST what vault returned]
Gap: [ANYTHING missing that would prevent score 4]
```

**If a requirement has no supporting evidence in the vault or research**, do
not stop and ask. Mark it for a `[INSERT: ...]` placeholder in Step 5 and add
a `flags.json` entry:
```json
{
  "timestamp": "<ISO timestamp>",
  "skill": "grant-writing",
  "section": "<section name>",
  "category": "ungrounded_requirement",
  "description": "No vault/research evidence for: '<requirement text>'",
  "default_action_taken": "Drafted with [INSERT: ...] placeholder for this requirement",
  "severity": "medium",
  "needs_human_review": true,
  "resolved": false
}
```
`grant-verification` Check 5 will independently confirm this requirement is
`missing`/`implied` while the placeholder remains.

### Step 4 — Plan the draft structure

Outline the structure based on:
- The section's key requirements (every requirement must be addressed)
- Style patterns from successful applications in the vault
- Funder red flags (structure must avoid these)

Proceed directly to drafting from this outline — do not stop for
confirmation, even for long/complex sections. Include the outline (as a short
bullet list) in the summary returned to the orchestrator so it's visible in
`flags.json`/`review.md` context if useful, but this does not need its own
flag entry — it's a normal part of the section summary.

### Step 5 — Write the draft

Write the section following these principles:

**Ground every specific claim**
- Facts, numbers, percentages, market sizes, technical specs — every one must come from vault evidence
- When using a specific claim, note the source in brackets: `[source: filename.pdf]`
- Do not use approximate figures unless the vault source uses them

**Follow the style patterns**
- Use the opening structure that style examples demonstrate
- Match the level of technical specificity shown in successful applications
- Match the tone — grant writing is formal, precise, and evidence-led

**Address every key requirement**
- Go through the key requirements from the section spec
- Ensure each is explicitly addressed somewhere in the draft
- Do not assume a requirement is implied — state it directly
- For any requirement flagged `ungrounded_requirement` in Step 3, insert a
  `[INSERT: description of what is needed]` placeholder that addresses the
  requirement structurally

**Avoid every red flag**
- Go through the red flags from the section spec
- Check the draft does not contain any of the warned patterns

**Word count discipline**
- Target 90-100% of the working word limit (Step 1) — do not go over
- Track approximate word count as you write

### Step 6 — Self-check before output

Before saving the draft, run through this checklist internally:

```
□ Word count within working limit?
□ Every key requirement addressed (directly or via [INSERT: ...] placeholder)?
□ Every specific claim has a vault source?
□ No red flag patterns present?
□ Opens strongly (not with a generic statement)?
□ Ends with a clear outcome or impact statement?
```

If any check fails, fix it before saving. Do not save a draft that fails its own checklist.

### Step 7 — Save and report

1. **Save the draft** to `vault/grants/<slug>/sections/qN-<name>.md` (clean
   markdown, ready to read or copy).

2. **Update `requirements.json`** — set this section's `status` to
   `"drafted"`.

3. **Return to the orchestrator**:
   - **Evidence used** — vault sources cited:
     ```
     Sources used:
     - innovate-uk-clean-tech-application-example.md (chunks 2, 5, 8)
     - Business-Connect-Good-Application-Guide_2024.pdf (chunk 15)
     ```
   - **Gaps/placeholders** — every `[INSERT: ...]` placeholder and what would fill it
   - **Word count** — exact count and whether it is within the working limit
   - **Requirements check** — confirm every key requirement was addressed, or note any that rely on a placeholder
   - **Flags** — any `flags.json` entries from Steps 1-3 above

## Handling missing vault evidence

When vault context is missing for a claim the section needs:
- Insert a clearly marked placeholder: `[INSERT: description of what is needed]`
- List all placeholders in the Step 7 summary
- Tell the orchestrator exactly what information or evidence would fill each gap

Do not invent company-specific information, financial figures, technical specifications, or market data. These must come from the user or the vault.

## Multiple sections

When asked to write the full application, the orchestrator spawns one
sub-agent per section (see Delegation above) — sections do not need to be
written sequentially. After each sub-agent returns, the orchestrator updates
`requirements.json`'s `status` for that section (`"drafted"`) and appends any
returned flags to `flags.json`.

## Revision workflow

When a revision is requested — either by the user, or automatically by
`grant-verification`'s bounded auto-retry on `needs_revision`/`fail` — spawn
a fresh sub-agent for just that section with the specific changes to make:
- Apply the specific changes requested
- Do not rewrite sections that were not mentioned
- Re-run the Step 6 self-check after revisions
- Note what changed and why in a brief revision note returned to the orchestrator
- Re-save `vault/grants/<slug>/sections/qN-<name>.md` and update `status` to
  `"verified"` (the orchestrator will re-run verification)

## Rules

- Never present invented content as retrieved fact
- Never exceed the working word limit
- Never skip the vault context step — even for short sections
- Always cite sources for specific claims
- Always use `[INSERT: ...]` placeholders plus a `flags.json` entry for gaps — never stop and ask mid-draft
- If the vault is unreachable, stop and tell the orchestrator — do not draft without context (this is the one legitimate hard stop)
