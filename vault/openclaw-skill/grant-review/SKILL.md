---
name: grant-review
description: "Consolidated end-of-pipeline review for a grant application — gathers every logged flag, checks cross-section consistency, and produces a single review.md for human sign-off. Run this last, after every section has been through writing, verification, and editing."
metadata: {"openclaw":{"emoji":"🧾"}}
---

# Grant Review

The single end-of-pipeline interruption. Every earlier skill in this pipeline
logs decisions and gaps to `flags.json` instead of stopping to ask — this
skill is where all of that surfaces for human review, once, at the end.

Runs on the orchestrator (Sonnet) — it's a synthesis step over files already
on disk, no new vault calls or sub-agent spawns needed.

## When to run

After every section in `requirements.json` has a `status` of `"approved"`,
`"verified"`, or `"needs_revision"` (i.e. `grant-writing` →
`grant-verification` → `grant-editing` have all run for every section,
including any bounded auto-retries). Run once per grant, not per section.

## Step 1 — Gather inputs

Read, for `vault/grants/<slug>/`:
- `requirements.json` — section list, statuses, word limits
- `flags.json` — every logged flag from every skill this session
- `verification/qN.json` for every section
- `sections/qN-*.md` for every section

## Step 2 — Group flags

Group `flags.json` entries by `severity` (high, medium, low), then by
`category` within each severity. Note which flags are still `resolved: false`
— these are the ones from this session that haven't been surfaced yet.

## Step 3 — Cross-application consistency check

This is the check formerly run at the end of `grant-editing`. Read all
sections with `status: "approved"` or `"verified"` together as one document
and check:

- **Narrative consistency** — does the application tell one coherent story?
  Do sections reference each other consistently (e.g. the team described in
  Q8 matches the team mentioned elsewhere, the cost figures in Q9 match any
  figures quoted in other sections)?
- **Total word counts** — sum word counts vs. limits; flag any section
  significantly under its limit (under 85%) that wasn't already flagged by
  `grant-editing`
- **Opening/closing reinforcement** — does the application's opening section
  set up themes that the closing section (or overall narrative) follows
  through on?
- Cross-reference against any `cross_section_conflicts` already recorded in
  `verification/qN.json` files

For each new inconsistency found here, append a `flags.json` entry with
`category: "cross_section_conflict"`, `severity: "medium"` or `"high"`
(high if it's a hard factual contradiction, e.g. two different team sizes or
cost totals; medium for softer narrative drift).

## Step 4 — Produce `review.md`

Write `vault/grants/<slug>/review.md`:

```markdown
# Grant Review — <grant_name> (<slug>)
Generated: <ISO timestamp>

## Summary

| Section | Status | Word count | Limit | Verification |
|---|---|---|---|---|
| Q4 — ... | approved | 580 | 600 | pass |
| Q5 — ... | needs_revision | 410 | 400 | needs_revision (after retry) |
...

## Needs your decision

<Only items where the default action taken might genuinely need
overriding — not every flag. Typically: any `severity: "high"` flag,
`source_conflict` entries between two Tier-1 sources, sections still
`needs_revision`/`fail` after retry, and any `cross_section_conflict`
found in Step 3.>

- [HIGH] verification_failed — Q5: still 'fail' after one revision pass
  (1 hallucination, 1 missing requirement). Editing skipped for this
  section. See verification/q5.json.
- [HIGH] source_conflict — UK heat pump market size: gov.uk (2025) says
  £X vs statista (2024) says £Y. Used £X (Tier 1). See research.json
  conflicts[].
...

## All flags (grouped by severity)

### High
- ...

### Medium
- ...

### Low
- ...

## Cross-application consistency check

- Narrative consistency: <findings>
- Word counts: <any sections under 85% of limit>
- Opening/closing reinforcement: <findings>
- New conflicts found: <any new cross_section_conflict entries, or "none">
```

## Step 5 — Present and mark flags reviewed

Present `review.md` to the user — this is the single end-of-pipeline
interruption, replacing the per-step prompts the earlier skills used to have.

Mark every flag included in `review.md` as `resolved: true` in
`flags.json`. Here `resolved` means "surfaced to the human in a review pass",
not "fixed" — items in the "Needs your decision" section of `review.md`
remain the durable record of what might need follow-up regardless of this
flag. If `grant-review` is ever re-run after manual edits, only newly-added
flags would show as unresolved.

## Rules

- Do not re-run `grant-writing`/`grant-verification`/`grant-editing` from
  this skill — it only reads existing output and (for Step 3) may add new
  `flags.json` entries
- Always include every section from `requirements.json` in the summary
  table, even ones still `needs_revision` — the point is visibility, not
  hiding incomplete work
- The human submits the application — this skill does not submit anything,
  it only prepares the review
