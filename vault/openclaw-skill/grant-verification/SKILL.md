---
name: grant-verification
description: "Verify every claim in a drafted grant section against vault sources and research findings. Catches hallucinations, overstated evidence, source mismatches, and cross-section inconsistencies before human review."
metadata: {"openclaw":{"emoji":"🔍"}}
---

# Grant Verification

Check every claim in a drafted grant section before it goes to human review. The vault and research pack are the ground truth — anything in the draft that cannot be traced back to one of them is a problem.

## Prerequisites

- `grant-requirements.json` must exist
- `grant-research.json` must exist (run `grant-research` first)
- The vault must be running — check `GET http://localhost:8100/health`
- A drafted section must exist to verify

## What verification checks

### Check 1 — Claim extraction

Read the drafted section and extract every verifiable claim. A verifiable claim is any statement that:
- Contains a specific number, percentage, or financial figure
- Makes a comparison ("better than", "beyond", "faster than")
- Attributes a fact to a source `[source: filename]`
- States something about the market, technology, policy, or competition
- Makes a prediction or projection

List every extracted claim before checking any of them.

### Check 2 — Source tracing

For every claim that has a cited source `[source: filename, chunk: N]`:

1. Retrieve the chunk from the vault:
```
POST http://localhost:8100/search
{
  "query": "[the claim text]",
  "n_results": 3,
  "where_filter": { "source": "[filename]" }
}
```

2. Compare the claim against the retrieved chunk text. Check for:

| Issue | Example |
|---|---|
| **Overstated** | Source says "may reduce" — draft says "reduces" |
| **Number changed** | Source says £4.2bn — draft says £4bn |
| **Wrong attribution** | Claim is from source B but cited as source A |
| **Extrapolation** | Source gives UK figure, draft applies it globally |
| **Outdated** | Source is from 2021 but presented as current |

Mark each claim as: `verified` / `overstated` / `number_mismatch` / `wrong_source` / `unverifiable`

### Check 3 — Unsourced claims

For every claim with no cited source:

1. Search the vault for supporting evidence:
```
POST http://localhost:8100/search
{
  "query": "[the claim]",
  "n_results": 5,
  "where_filter": { "is_evidence": "true" }
}
```

2. Search `grant-research.json` findings for a matching entry.

3. Classify the result:
- **Found in vault** — attach the source, mark as `retroactively_sourced`
- **Found in research** — attach the research finding, mark as `retroactively_sourced`
- **Not found anywhere** — mark as `hallucination` — this must be fixed before the draft is used

### Check 4 — Cross-section consistency

If multiple sections have been drafted, check for contradictions across them.

Common inconsistencies to look for:
- Team size stated differently across sections
- Market size figures that differ between sections
- Project costs that don't add up between summary and finance sections
- TRL levels stated differently
- Timelines that contradict between sections
- Company founding date or history stated differently

For each inconsistency found, note which sections conflict and what the two statements are.

### Check 5 — Requirements coverage

Read the section's `key_requirements` from `grant-requirements.json`.

For each key requirement, check whether the draft explicitly addresses it:
- `addressed` — the draft directly responds to this requirement
- `implied` — the draft touches on it but not directly — flag for strengthening
- `missing` — the draft does not address this requirement at all

Any `missing` requirement must be flagged — the section will score poorly without it.

### Check 6 — Red flag scan

Read the section's `red_flags` from `grant-requirements.json`.

Check the draft for any of the warned patterns. Flag any that are present with the exact line where it appears.

## Verification output format

Produce a structured verification report. Save it to `verification-[section-name].json` in the workspace.

```json
{
  "section": "[section name]",
  "verified_at": "[timestamp]",
  "overall_status": "pass | fail | needs_revision",
  "claim_results": [
    {
      "claim": "exact text of the claim from the draft",
      "status": "verified | overstated | number_mismatch | wrong_source | hallucination | retroactively_sourced",
      "source": "filename or null",
      "vault_text": "exact text from vault chunk that supports or contradicts",
      "issue": "description of the problem if status is not verified",
      "fix_required": true
    }
  ],
  "requirements_coverage": [
    {
      "requirement": "requirement text from grant-requirements.json",
      "status": "addressed | implied | missing"
    }
  ],
  "red_flags_found": [
    {
      "red_flag": "the red flag from grant-requirements.json",
      "found_in_draft": "exact line from the draft that triggered it"
    }
  ],
  "cross_section_conflicts": [],
  "summary": {
    "total_claims": 0,
    "verified": 0,
    "overstated": 0,
    "hallucinations": 0,
    "retroactively_sourced": 0,
    "requirements_missing": 0,
    "red_flags_triggered": 0
  }
}
```

**Overall status rules:**
- `pass` — all claims verified or retroactively sourced, all requirements addressed, no red flags
- `needs_revision` — some claims overstated or implied requirements, no hallucinations
- `fail` — any hallucinations present, any missing requirements, or any red flags triggered

## After verification

### If status is `pass`

Tell the user the section passed verification. Present the summary counts. Note any retroactively sourced claims so the writing agent can add the citations to the draft.

### If status is `needs_revision`

Present a prioritised fix list:
1. Overstated claims — show the claim, show what the source actually says, suggest corrected wording
2. Number mismatches — show the claim figure and the source figure
3. Implied requirements — show what is missing and suggest where to add it

Ask the user whether to:
- Send the fix list back to the writing agent to revise automatically
- Present the issues for the user to fix manually

### If status is `fail`

Stop. Do not proceed to editing. Present:
- Every hallucination with the exact claim text
- Every missing requirement
- Every red flag triggered

The section must be revised before moving forward. Tell the user clearly.

## Rules

- Never pass a section with hallucinations — there are no exceptions
- Never pass a section with missing key requirements
- Never silently correct a claim — always flag it and show the original source text
- If the vault is unreachable during verification, stop — do not verify without access to source material
- Retroactively sourced claims must have their citations added to the draft before it is considered final
- Cross-section conflicts must be resolved before the full application is submitted — note them even if checking a single section
