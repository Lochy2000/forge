---
name: grant-editing
description: "Polish a verified grant section for readability, tone, clarity, and conciseness. Only runs after verification has passed. Does not change facts, sources, or structure."
metadata: {"openclaw":{"emoji":"✏️"}}
---

# Grant Editing

Polish a verified grant section for submission quality. This skill improves how the draft reads — not what it says. Facts, sources, and structure are not changed. Only run this after `grant-verification` has passed (or finished its bounded auto-retry).

This runs on the orchestrator (Sonnet) — no delegation needed. It's lower
stakes than drafting, makes no new vault calls, and benefits from the section
context already loaded while reviewing the verification result.

## Prerequisites

- `grant-verification` must have produced `verification/qN.json` for this
  section with `overall_status: "pass"`, or `"needs_revision"` after its one
  auto-retry (see `grant-verification`'s bounded auto-retry rules)
- `vault/grants/<slug>/requirements.json` must exist
- **Skip this section** if its `flags.json` has an unresolved
  `verification_failed` entry for it (i.e. it's still `fail` after retry) —
  leave its `status` as `"needs_revision"` and move on to the next section

## What editing changes

### What editing DOES change
- Sentence clarity — long or tangled sentences broken into shorter ones
- Word choice — vague words replaced with precise ones
- Tone — passive voice converted to active where appropriate
- Redundancy — repeated points removed, padding cut
- Flow — transitions between paragraphs improved
- Opening line — generic openings replaced with strong, specific ones
- Closing line — sections should end with impact or outcome, not process

### What editing DOES NOT change
- Facts, statistics, or claims
- Source citations
- The structure or order of points
- Word count (unless the current draft exceeds the limit)
- Technical terminology — do not simplify technical language that must be precise

## Grant writing tone

Grant writing has a specific register. When editing, enforce these conventions:

**Active over passive**
- Before: "The project will be delivered by a team of experienced engineers"
- After: "An experienced engineering team will deliver the project"

**Specific over vague**
- Before: "significant market opportunity"
- After: "a £4.2bn UK addressable market by 2030"

**Evidence-led, not assertion-led**
- Before: "Our technology is innovative"
- After: "Our SPEEK membrane synthesis process advances beyond the Nafion-based state of the art by achieving 80 mS/cm proton conductivity at 500kg batch scale"

**Confident but not overclaiming**
- Before: "will definitely achieve"
- After: "is designed to achieve" / "targets"
- Before: "groundbreaking"
- After: "novel" / "beyond current state of the art"

**Concise — no padding**
Cut phrases that add length without meaning:
- "It is important to note that..."
- "As mentioned previously..."
- "In order to..."
- "It should be highlighted that..."
- "We firmly believe that..."

## Editing process

### Step 1 — Read for overall impression

Read the full section once without editing. Note:
- Does it open strongly?
- Is the argument clear from start to finish?
- Does it end with impact?
- Are there any sections that feel weak or unconvincing?

### Step 2 — Line-level editing

Go through the draft sentence by sentence. For each sentence ask:
- Can this be shorter without losing meaning?
- Is the subject clear and does it come early?
- Is the verb active?
- Are there any vague words that should be specific?
- Does this sentence earn its place?

### Step 3 — Check the opening

The first sentence sets the tone. It must be specific and strong. Replace any opening that:
- Starts with "We are..." or "Our company..."
- States the obvious ("Innovation is important for...")
- Restates the section title

A strong grant opening states the problem, the gap, or the specific claim immediately.

### Step 4 — Check the closing

The last sentence should leave the reader with the impact or outcome. It must not:
- Tail off with a process point
- Repeat something said earlier
- End mid-argument

### Step 5 — Word count check

Count the words in the edited draft. Check against `requirements.json`'s
working word limit (the stated `word_limit`, or the default applied by
`grant-writing` if it was null):
- If over the limit: cut further — prioritise cutting padding, not substance
- If under 85% of the limit: proceed anyway, but note this in the edit
  summary so it surfaces in the `section_complete` flag below — the section
  may be underdeveloped
- If within 85-100%: acceptable

Never exceed the word limit. Funders disqualify sections that exceed limits.

### Step 6 — Funder tone check

Read the funder requirements for this section from `requirements.json`. Check that the edited draft:
- Uses language consistent with the funder's own terminology where known
- Addresses scoring criteria in the order they appear (if the brief implies an order)
- Does not use language the funder has warned against (check red flags)

## Step 7 — Save, auto-approve, and log

1. **Overwrite** `vault/grants/<slug>/sections/qN-<name>.md` with the edited draft.

2. **Determine status**:
   - If `verification/qN.json` was `"pass"` (or `"needs_revision"` after its
     one retry, per `grant-verification`), and the edited draft is within
     the word limit: set this section's `status` in `requirements.json` to
     `"approved"`.
   - Otherwise leave `status` as `"verified"`/`"needs_revision"` — human
     sign-off happens in `grant-review`, not here.

3. **Append a `flags.json` entry** summarising the edit — this is the record
   a human reviews in `grant-review`, replacing the old per-section
   "are you happy with this?" prompt:
   ```json
   {
     "timestamp": "<ISO timestamp>",
     "skill": "grant-editing",
     "section": "<section name>",
     "category": "section_complete",
     "description": "Edited and auto-approved. Changes: <short summary, e.g. '4 passive->active, cut 47 words padding, strengthened opening/closing'>. Word count: <before> -> <after> / <limit>.",
     "default_action_taken": "status set to 'approved'",
     "severity": "low",
     "needs_human_review": <true if under 85% of limit, or if status left as needs_revision, else false>,
     "resolved": false
   }
   ```
   If a sentence was left unchanged despite looking weak because it's tied to
   a cited fact, include that note in `description` too — it's the
   "anything not changed and why" information for the human reviewer.

Do not stop to ask whether the user is happy with the edit, and do not
prompt for a final cross-application check — `grant-review` runs
automatically once every section has been through this step and produces the
single end-of-pipeline summary.

## Rules

- Never change a fact, number, or citation during editing
- Never exceed the word limit — cut instead
- Never simplify technical terminology that must be precise
- Do not run on a section whose verification is still `fail` after the bounded auto-retry (see Prerequisites) — leave it for `grant-review` to surface
- If asked to "improve" a claim that is a verified fact, refuse — explain that changing the claim would require re-verification
- `grant-review` is the last automated step in the pipeline — editing auto-approves and proceeds, the human reviews at the end
