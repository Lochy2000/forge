---
name: grant-editing
description: "Polish a verified grant section for readability, tone, clarity, and conciseness. Only runs after verification has passed. Does not change facts, sources, or structure."
metadata: {"openclaw":{"emoji":"✏️"}}
---

# Grant Editing

Polish a verified grant section for submission quality. This skill improves how the draft reads — not what it says. Facts, sources, and structure are not changed. Only run this after `grant-verification` has passed.

## Prerequisites

- `grant-verification` must have passed for this section (`overall_status: pass`)
- `grant-requirements.json` must exist
- Do not run editing on a section that has not been verified

If the user asks to edit an unverified section, remind them to run verification first.

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

Count the words in the edited draft. Check against `grant-requirements.json`:
- If over the limit: cut further — prioritise cutting padding, not substance
- If under 85% of the limit: flag to the user — the section may be underdeveloped
- If within 85-100%: acceptable

Never exceed the word limit. Funders disqualify sections that exceed limits.

### Step 6 — Funder tone check

Read the funder requirements for this section from `grant-requirements.json`. Check that the edited draft:
- Uses language consistent with the funder's own terminology where known
- Addresses scoring criteria in the order they appear (if the brief implies an order)
- Does not use language the funder has warned against (check red flags)

## Output

Present the edited draft with:

1. **The edited draft** — clean, ready to copy

2. **Edit summary** — a short list of the main changes made:
   ```
   Changes made:
   - Converted 4 passive constructions to active voice
   - Cut 47 words of padding
   - Strengthened opening line — replaced generic statement with specific claim
   - Improved closing — added impact statement
   - Replaced 3 vague phrases with specific language
   ```

3. **Word count** — before and after, and whether it is within the limit

4. **Anything not changed and why** — if a sentence looks weak but was left because changing it would alter a cited fact, note it:
   ```
   Not changed:
   - Paragraph 3, sentence 2: phrasing is awkward but tied directly to source citation — recommend user reviews manually
   ```

## After editing

Ask the user:
- Are you happy with the edited version?
- Would you like any specific section re-edited with different emphasis?
- Is this section ready to mark as complete?

If the user approves, update `grant-requirements.json` to mark the section status as `approved`:
```json
{
  "name": "Innovation",
  "status": "approved"
}
```

## Final application check

When all sections are marked `approved` in `grant-requirements.json`, prompt the user to run a final cross-application check:

- Read all approved sections together as one document
- Check overall narrative consistency — does the application tell a coherent story?
- Check total word counts across all sections — are any significantly under?
- Check that the opening of the application and the closing section reinforce each other
- List any final issues before the user submits

## Rules

- Never change a fact, number, or citation during editing
- Never exceed the word limit — cut instead
- Never simplify technical terminology that must be precise
- Do not run on unverified sections
- If the user asks to "improve" a claim that is a verified fact, refuse — explain that changing the claim would require re-verification
- Editing is the last automated step — the human submits, not the agent
