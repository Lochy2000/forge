---
name: grant-writing
description: "Draft grant application sections using vault-retrieved evidence, funder requirements, and style examples from successful applications. Always run requirement-extraction first."
metadata: {"openclaw":{"emoji":"✍️"}}
---

# Grant Writing

Draft individual grant sections grounded in vault-retrieved evidence. Each section is written one at a time, checked against funder requirements, and self-assessed before delivery.

## Prerequisites

Before running this skill:
1. `grant-requirements.json` must exist in the workspace — run `requirement-extraction` first
2. The vault must be running — check `GET http://localhost:8100/health`
3. The user must specify which section to write

Read `grant-requirements.json` at the start of every writing task. Do not rely on memory of previous turns.

## Per-section workflow

### Step 1 — Load section spec

Read `grant-requirements.json` and find the target section. Extract:
- Section name
- `section_hint`
- Word limit (if null, ask the user before proceeding)
- Scoring weight
- Key requirements
- Red flags

### Step 2 — Retrieve vault context

Call the vault context pack for this section:

```
POST http://localhost:8100/context-pack
{
  "task": "Write the [section name] section for a [grant_name] application",
  "grant_scheme": "[grant_scheme from grant-requirements.json]",
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

If any group returns 0 results, note this explicitly. Do not invent content to fill the gap — flag it to the user instead.

If distances are consistently above 350 across all results, warn the user that vault context is weak for this section and retrieved content may not be closely relevant.

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

If a requirement has no supporting evidence in the vault or research, flag it to the user before drafting — do not draft a section you cannot ground.

### Step 5 — Plan the draft structure

Before writing, outline the structure based on:
- The section's key requirements (every requirement must be addressed)
- Style patterns from successful applications in the vault
- Funder red flags (structure must avoid these)

Present the outline to the user if the section is complex (over 300 words) or if the key requirements suggest a specific structure. Ask for confirmation before drafting.

### Step 6 — Write the draft

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

**Avoid every red flag**
- Go through the red flags from the section spec
- Check the draft does not contain any of the warned patterns

**Word count discipline**
- Target 90-100% of the word limit — do not go over
- If a word limit is not set, ask the user for a target before writing
- Track approximate word count as you write

### Step 7 — Self-check before output

Before showing the draft, run through this checklist internally:

```
□ Word count within limit?
□ Every key requirement addressed?
□ Every specific claim has a vault source?
□ No red flag patterns present?
□ Opens strongly (not with a generic statement)?
□ Ends with a clear outcome or impact statement?
```

If any check fails, fix it before outputting. Do not output a draft that fails its own checklist.

### Step 8 — Output

Present the draft with:

1. **The draft text** — clean, ready to copy

2. **Evidence used** — a short list of the vault sources cited, so the user can verify:
   ```
   Sources used:
   - innovate-uk-clean-tech-application-example.md (chunks 2, 5, 8)
   - Business-Connect-Good-Application-Guide_2024.pdf (chunk 15)
   ```

3. **Gaps flagged** — anything the draft could not ground in vault evidence:
   ```
   Gaps (not grounded in vault):
   - No vault evidence for [specific claim] — placeholder used, needs your input
   ```

4. **Word count** — exact count and whether it is within the limit

5. **Requirements check** — confirm every key requirement was addressed, or flag any missed

## Handling missing vault evidence

When vault context is missing for a claim the section needs:
- Insert a clearly marked placeholder: `[INSERT: description of what is needed]`
- List all placeholders in the gaps section
- Tell the user exactly what information or evidence would fill each gap

Do not invent company-specific information, financial figures, technical specifications, or market data. These must come from the user or the vault.

## Multiple sections

If the user asks to write the full application:
- Write one section at a time
- Present each section for review before moving to the next
- Update `grant-requirements.json` with a `status` field for each section as it is completed:
  `"status": "drafted"` / `"status": "approved"` / `"status": "needs_revision"`

## Revision workflow

When the user requests changes:
- Apply the specific changes requested
- Do not rewrite sections that were not mentioned
- Re-run the self-check after revisions
- Note what changed and why in a brief revision note below the updated draft

## Rules

- Never present invented content as retrieved fact
- Never exceed the word limit
- Never skip the vault context step — even for short sections
- Always cite sources for specific claims
- Always flag gaps explicitly rather than filling them with assumptions
- If the vault is unreachable, stop and tell the user — do not draft without context
