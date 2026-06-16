---
name: grant-research
description: "Research public evidence, market data, policy context, and technical state of the art for a grant application. Produces a verified, cited research pack grounded in authoritative sources."
metadata: {"openclaw":{"emoji":"🔬"}}
---

# Grant Research

Gather and verify public evidence to support a grant application. Every finding must be sourced, dated, and cross-referenced before it can be used in a draft. Unverified statistics in a grant application damage credibility with funders.

## Delegation

Run this entire skill inside one isolated sub-agent
(`sessions_spawn`, `model: "anthropic/claude-sonnet-4-6"`,
`context: "isolated"`). This is the single biggest context consumer in the
pipeline — multiple search/extract rounds across several evidence categories
— so keeping it out of the orchestrator's session is the highest-value
isolation change.

The orchestrator's job is just to spawn the sub-agent with the grant slug and
folder path (`vault/grants/<slug>/`) and call `sessions_yield`. The sub-agent
reads `requirements.json` itself, runs the full research pass below
including the vault ingestion, writes `research.json` and
`research-notes.md`, and returns a short summary plus any `flags.json`
entries for the orchestrator to append.

## Prerequisites

- `vault/grants/<slug>/requirements.json` must exist — run
  `requirement-extraction` first
- Read it to understand what evidence is needed before planning any searches

## Research planning

Before searching, build a research plan from `requirements.json`.

Extract:
- The `evidence_needed` list — these are the minimum required findings
- Each section's `key_requirements` — these reveal what evidence each section needs
- The `grant_scheme` — this determines which sources are most authoritative

Group the evidence needed into these categories and assign priority:

| Category | Priority | What to find |
|---|---|---|
| Market data | High | Market size, growth rates, addressable market for UK |
| Policy context | High | Government priorities, existing funding programmes, targets |
| State of the art | High | What technology/solutions currently exist and their limitations |
| Competitive landscape | Medium | Who else operates in this space, what they offer |
| Economic impact | Medium | Jobs, productivity, economic value relevant to the project |
| Funder priorities | High | What this funder has recently funded, their stated priorities |

## Search tools

Use these tools in escalation order — start simple, escalate only when needed:

**`web_search`** — quick lookups, general queries
**`tavily_search`** — when you need depth control, domain filtering, time ranges, or AI-synthesised answers
**`tavily_extract`** — when you have a specific URL and need its full content

If Tavily is not available, use `web_search` for all queries, but note that research quality will be lower and manual verification becomes more important.

## Trusted source domains by category

Use `include_domains` in `tavily_search` to restrict to authoritative sources:

**UK government and statistics:**
`gov.uk` `ons.gov.uk` `ukri.org` `innovateuk.ukri.org` `nesta.org.uk` `ofgem.gov.uk`

**Academic and technical:**
`arxiv.org` `researchgate.net` `nature.com` `sciencedirect.com` `iea.org`

**Market and industry:**
`statista.com` `ibisworld.com` `mckinsey.com` `deloitte.com` `pwc.com`

**News and current events:**
Use `topic: news` with `time_range: year` in `tavily_search` for recent developments.

## Executing searches

For each evidence category, run searches in this order:

### Step 1 — Find authoritative sources

```
tavily_search(
  query: "[specific query]",
  search_depth: "advanced",
  max_results: 8,
  include_domains: [relevant trusted domains],
  include_answer: true
)
```

Use `include_answer: true` to get a synthesised summary alongside raw results.

### Step 2 — Extract full content from key results

When a search result looks highly relevant but the snippet is not enough:

```
tavily_extract(
  urls: ["url1", "url2"],
  query: "[what you are looking for]",
  chunks_per_source: 3,
  extract_depth: "basic"
)
```

Use `extract_depth: advanced` only if basic returns incomplete content.

### Step 3 — Find recent developments

For fast-moving fields (technology, policy, energy), run a second pass for recent news:

```
tavily_search(
  query: "[topic] UK 2025 2026",
  topic: "news",
  time_range: "year",
  max_results: 5
)
```

### Step 4 — Research the funder

Always research the funder specifically:

```
tavily_search(
  query: "[funder name] funded projects priorities [year]",
  search_depth: "advanced",
  include_domains: [funder domain],
  max_results: 5
)
```

Look for: recently funded projects, stated strategic priorities, evaluation criteria emphasis.

## Source quality assessment

For every source, assess before recording it:

| Factor | Questions to ask |
|---|---|
| Authority | Is this a government body, academic institution, or major research organisation? Or a blog/opinion piece? |
| Recency | When was this published or last updated? For market data and policy, flag anything over 2 years old. |
| Specificity | Does it give specific UK figures, or only global/EU figures? Note which. |
| Primary vs secondary | Is this original research, or citing another source? If secondary, find the primary. |

**Source tiers:**
- **Tier 1** (high confidence): Government statistics, peer-reviewed research, official funder publications
- **Tier 2** (medium confidence): Major consultancy reports, established industry bodies, quality journalism
- **Tier 3** (low confidence): Company blogs, opinion pieces, unattributed statistics

Only use Tier 3 sources if Tier 1/2 are unavailable, and flag them clearly.

## Cross-referencing key statistics

For any statistic that will be cited in the grant:
- Find it in at least 2 independent sources
- If sources conflict, **resolve automatically** using this order, and record
  both figures plus the resolution (see "Handling conflicts" below):
  1. Prefer the Tier 1 source over Tier 2/3
  2. If tied on tier, prefer the more recent source
  3. If still tied, prefer the UK-specific figure over a global/EU one
- If only 1 source exists, note it as single-source in `low_confidence_items`

Statistics that require cross-referencing:
- Market size figures
- Growth rate projections
- Employment/jobs figures
- Cost or price benchmarks
- Technical performance claims

## Handling conflicts

When two sources conflict on a statistic, do not stop and ask. Apply the
resolution order above, record the conflict with the chosen figure in
`research.json`'s `conflicts` array, and add a `flags.json` entry so the user
can review the choice later:

```json
{
  "id": "flag-00N",
  "timestamp": "<ISO timestamp>",
  "skill": "grant-research",
  "section": null,
  "category": "source_conflict",
  "description": "Market size: gov.uk (2025) says £X, statista (2024) says £Y",
  "default_action_taken": "Used £X (Tier 1, gov.uk) — see research.json conflicts[]",
  "severity": "medium",
  "needs_human_review": true,
  "resolved": false
}
```

A conflict between two Tier-1 sources, or one that the resolution order
cannot break (same tier, same recency, both UK-specific), gets
`severity: "high"` — these are the ones most worth a second look in
`grant-review`.

## Research output format

Save findings to `vault/grants/<slug>/research.json`:

```json
{
  "research_date": "[today's date]",
  "grant_scheme": "[from requirements.json]",
  "findings": [
    {
      "category": "market_size",
      "claim": "exact claim as stated in source",
      "source_name": "Publication or organisation name",
      "source_url": "full URL",
      "source_date": "YYYY-MM or YYYY",
      "source_tier": 1,
      "cross_referenced": true,
      "second_source_url": "URL of confirming source or null",
      "uk_specific": true,
      "notes": "any caveats or context"
    }
  ],
  "funder_intelligence": {
    "recent_funded_projects": [],
    "stated_priorities": [],
    "notes": ""
  },
  "gaps": [
    "Could not find UK-specific data on X — only global figures available"
  ],
  "conflicts": [
    {
      "claim_a": "exact claim text",
      "source_a": "name/url/tier",
      "claim_b": "exact claim text",
      "source_b": "name/url/tier",
      "resolution": "Used claim_a — Tier 1 preferred over Tier 2",
      "chosen": "a"
    }
  ],
  "low_confidence_items": [
    "Claim X is single-source only (Tier 3) — flag to user before using in draft"
  ]
}
```

## After research is complete

1. **Save** `research.json` to `vault/grants/<slug>/research.json`.

2. **Always save research notes to the vault** — format findings as a markdown file and ingest it so future sessions can retrieve this research without repeating the searches:

   Create `vault/grants/<slug>/research-notes.md` with this structure:
   ```markdown
   # Research Notes — [GRANT SCHEME] — [PROJECT]
   Research date: [DATE]

   ## Market findings
   - [CLAIM]. Source: [URL] ([DATE])
   - [CLAIM]. Source: [URL] ([DATE])

   ## Policy and regulatory context
   - [CLAIM]. Source: [URL] ([DATE])

   ## State of the art
   - [CLAIM]. Source: [URL] ([DATE])

   ## Funder intelligence
   - [FINDING about funder priorities]. Source: [URL] ([DATE])

   ## Gaps
   - [What could not be found]
   ```

   Then ingest it:
   ```
   POST http://localhost:8100/ingest
   file: vault/grants/<slug>/research-notes.md
   grant_scheme: [scheme]
   quality_signal: unknown
   source_type: internal
   sensitivity: internal
   ```

   Only include verified Tier 1 or Tier 2 findings in this file — do not persist unverified or single-source claims to the vault.

3. **Return a summary to the orchestrator** (not the user directly — this
   runs in an isolated sub-agent):
   - Key findings by category
   - Source quality overview (how many Tier 1/2/3 sources used)
   - Every entry in `gaps` and `conflicts`, each as a proposed `flags.json`
     entry (category `research_gap` for gaps, `source_conflict` for
     conflicts — see above for the conflict entry shape; use the same shape
     with `category: "research_gap"` and `severity: "low"` for gaps)
   - Any single-source statistics from `low_confidence_items`

   The orchestrator appends these to `vault/grants/<slug>/flags.json` and
   proceeds straight to `grant-writing` — research gaps and conflicts do not
   block drafting. `grant-writing` will insert `[INSERT: ...]` placeholders
   for anything genuinely missing, and `grant-review` surfaces everything
   logged here at the end.

## Rules

- Never use a statistic in a grant draft without a URL, source name, and date
- Never present global figures as UK figures without noting the distinction
- Never use a statistic older than 3 years for market or technology claims without flagging it
- Always check the funder's own website — their stated priorities should inform every section
- If a key evidence item cannot be found at Tier 1 or 2, record it in `gaps` rather than substituting a weaker source silently
- When sources conflict, resolve using the documented order, record both figures and the resolution, and log a `flags.json` entry — never pick silently and never stop to ask
- `research.json` is the source of truth for public evidence — the vault is for private/historical evidence
