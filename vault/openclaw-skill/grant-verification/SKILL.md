---
name: grant-verification
description: "Verify every claim in a drafted grant section against vault sources and research findings. Catches hallucinations, overstated evidence, source mismatches, and cross-section inconsistencies before human review."
metadata: {"openclaw":{"emoji":"🔍"}}
---

# Grant Verification

Check every claim in a drafted grant section before it goes to human review. The vault and research pack are the ground truth — anything in the draft that cannot be traced back to one of them is a problem.

## Delegation

Run each section's verification as its own `sessions_spawn` call to
`model: "ollama/qwen2.5:7b"`, `context: "isolated"`. This runs through
OpenClaw's embedded runtime — no Claude Code usage.

The spawn prompt must include: the grant slug and folder path
(`vault/grants/<slug>/`) and the section name. The sub-agent reads
`requirements.json`, `research.json`, and
`sections/qN-<name>.md` itself, runs Checks 1-6 below, writes
`verification/qN.json`, and returns `overall_status` plus any flags to the
orchestrator.

**Tool-calling fallback ladder** — Checks 2-3 need `exec curl` against the
vault. If `ollama/qwen2.5:7b` fails to call tools reliably:
1. Try `ollama/qwen2.5-coder:7b` (`ollama pull qwen2.5-coder:7b` if not present).
2. If local models still can't call tools: set `compat.supportsTools: false`
   + `experimental.localModelLean: true` on the model entry, and have the
   **orchestrator** pre-fetch the vault lookups (one `/search` call per
   cited source, one `/search` with `is_evidence: true` for unsourced
   claims) and pass the raw JSON results into the sub-agent's prompt — the
   sub-agent then only classifies/compares (text in, JSON out, no tools).

Checks 1, 4, 5, and 6 are pure text/JSON and need no tools — `qwen2.5:3b` is
sufficient if `7b` is ever unavailable.

## Prerequisites

- `vault/grants/<slug>/requirements.json` must exist
- `vault/grants/<slug>/research.json` must exist (run `grant-research` first)
- The vault must be running — check with `curl http://localhost:8100/health`
- The vault is a local HTTP API — use curl (not web_fetch, which blocks localhost)
- `vault/grants/<slug>/sections/qN-<name>.md` must exist (run `grant-writing` first)

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

1. Retrieve the chunk from the vault using curl:
```bash
curl -s -X POST http://localhost:8100/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"[claim text]\", \"n_results\": 3, \"where_filter\": {\"source\": \"[filename]\"}}"
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

2. Search `research.json` findings for a matching entry.

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

Read the section's `key_requirements` from `requirements.json`.

For each key requirement, check whether the draft explicitly addresses it:
- `addressed` — the draft directly responds to this requirement
- `implied` — the draft touches on it but not directly — flag for strengthening
- `missing` — the draft does not address this requirement at all

Any `missing` requirement must be flagged — the section will score poorly without it. Note: a `[INSERT: ...]` placeholder for a requirement should be marked `missing` or `implied`, not `addressed`.

### Check 6 — Red flag scan

Read the section's `red_flags` from `requirements.json`.

Check the draft for any of the warned patterns. Flag any that are present with the exact line where it appears.

## Verification output format

Produce a structured verification report. Save it to
`vault/grants/<slug>/verification/qN.json` (e.g. `verification/q4.json`).

```json
{
  "section": "[section name]",
  "verified_at": "[timestamp]",
  "overall_status": "pass | fail | needs_revision",
  "retry_count": 0,
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
      "requirement": "requirement text from requirements.json",
      "status": "addressed | implied | missing"
    }
  ],
  "red_flags_found": [
    {
      "red_flag": "the red flag from requirements.json",
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

## After verification — bounded auto-retry, then continue

This section describes orchestrator-level logic that runs after the
verification sub-agent returns.

### If status is `pass`

Update `requirements.json`'s `status` for this section to `"verified"`.
Note any `retroactively_sourced` claims so `grant-editing` adds the citations
to the draft. Proceed to `grant-editing` for this section.

### If status is `needs_revision` or `fail`, and `retry_count` is 0

Do not stop and ask. Build a prioritised fix list from:
1. Hallucinations and missing requirements (if `fail`) — highest priority
2. Overstated claims and number mismatches — show the claim, show what the source actually says, suggest corrected wording
3. Implied/missing requirements — show what is missing and where to add it
4. Red flags triggered — show the exact line

Spawn a `grant-writing` revision sub-agent (see that skill's Revision
workflow) for this section only, with the fix list. When it returns, spawn a
fresh `grant-verification` sub-agent for the same section with
`retry_count: 1`.

### If status is `needs_revision` or `fail`, and `retry_count` is 1 (i.e. retry already happened)

Stop retrying — do not loop indefinitely. Append a `flags.json` entry:

```json
{
  "timestamp": "<ISO timestamp>",
  "skill": "grant-verification",
  "section": "<section name>",
  "category": "verification_failed",
  "description": "Section still '<overall_status>' after one auto-revision pass. <N> hallucinations, <N> missing requirements, <N> red flags.",
  "default_action_taken": "Left as 'needs_revision'/'verified' status unchanged; editing skipped for this section",
  "severity": "high",
  "needs_human_review": true,
  "resolved": false
}
```

- If still `fail` after the retry: leave `requirements.json`'s `status` for
  this section as `"needs_revision"` and **skip `grant-editing` for this
  section only** — other sections continue through the pipeline unaffected.
- If `needs_revision` (not `fail`) after the retry: proceed to
  `grant-editing` anyway (the remaining issues are overstatements/implied
  requirements, not hallucinations) but keep the `high`-severity flag so it's
  prominent in `grant-review`.

## Rules

- Never pass a section with hallucinations — there are no exceptions
- Never pass a section with missing key requirements
- Never silently correct a claim — always record the issue and the original source text in `verification/qN.json`
- If the vault is unreachable during verification, stop and tell the orchestrator — do not verify without access to source material
- Retroactively sourced claims must have their citations added to the draft during `grant-editing`
- Cross-section conflicts must be recorded even when checking a single section — `grant-review` consolidates them across all sections
- Bounded auto-retry is exactly one cycle — after that, log and move on (see above)
