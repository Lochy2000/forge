# Cross-application coherence check — Q4–Q9

**Date:** 2026-06-09
**Pipeline stage:** post-verification, post-editing, pre-submission
**Scope:** ThermaSync Ltd / Innovate UK Smart Grants — November 2024 round

---

## Verdict

**Substantially coherent.** Headline numbers, names, dates, regulatory references, sources, and the TRL/finance/cost spine all align across the six sections. One real arithmetic discrepancy inside Q9 needs resolving before submission; three minor wording alignments would tighten the read-through.

---

## Coherent across all six (spot-checked)

**Project spine**
- £400,000 total / £180,000 grant (45%) / £220,000 contribution (55%) — Q5 + Q9
- TRL 4 → TRL 7 across 18 months — Q4 + Q5 + Q8 + Q9
- 23% peak-reduction target with ≥18% acceptance threshold — Q4 + Q7 + Q8 WP2/WP4 + Q9

**Anchors**
- Sheffield CC 240-dwelling paid pilot (Phase 1 feasibility extension Q3 2024, £25k contract value, cashflow Q2 2025) — Q4 + Q5 + Q6 + Q7 + Q8 WP4 + Q9
- Brindleyplace 6-building LOI contingent on TRL 7 — Q4 + Q6 + Q8 WP5 + Q9

**IP / data**
- GB2024/TH0012 patent application (Mar 2024) + FTO Jan 2024 + 847,000-hour dataset across 23 building types — Q4 + Q6 + Q9

**Market context**
- 800 UK heat networks — Q6 + Q7 + Q9
- £340m TAM consistently framed as "ThermaSync internal analysis (Frontier Economics, 2023)" — Q6 + Q9 (Q4 correctly defers to Q6)
- HNIP £320m / GHNF £753m / HNES £77m / HNDU £37m → >£1bn pipeline — Q6 + Q7
- BMS incumbent list (Honeywell, JCI, Schneider, Siemens, Trend, Priva, ABB, Tridium) — Q4 + Q6 + Q7 + Q9

**Regulatory window**
- Heat Networks (Market Framework) Regulations 2025 + Heat Network Zoning under Energy Act 2023 — Q4 + Q5 + Q6 + Q7 + Q8 (Webb advisory) + Q9

**Team and supply chain**
- 6-person team (3 tech, 1 commercial, 1 ops, 1 part-time regulatory) — Q5 + Q7 + Q8
- Nair / Okafor / Chen credentials — Q6 (Chen brief) + Q8 (full)
- Marcus Webb ex-HNDU, regulatory advisor from Q2 2024 — Q7 + Q8
- Applied Electronics Ltd (Leeds) under signed development agreement — Q7 + Q8 + Q9
- Advisory board (Prof. Fisk CBE, Dr Kramer) — Q8 + Q9

**Finance history**
- £150k IUK SIF 2022 + £45k UKRI Smart Energy Systems 2023 + £200k angel 2023 = £395k (sums correctly) — Q5 + Q9
- £47k turnover, ~9 months runway, 2/3 grant win rate — Q5 + Q9
- £180k cash + £25k Sheffield + £15k Applied Electronics = £220k bridging — Q5 + Q9

**Environmental methodology**
- DESNZ National Grid Carbon Intensity API winter 2023/24 (580 gCO2e/kWh peak / 195 gCO2e/kWh off-peak) — Q7 only, arithmetic checks: 2.9 GWh × 23% = 667 MWh; (580−195) × 667 = ~257 t/deployment; 100 deployments × 257 t = 25,700 t/yr; 25,700 / 4.6 t per car ≈ 5,600 cars. All consistent.
- 37% UK emissions from heat in buildings (DESNZ 2024) — Q4 + Q7

**Hires (count)**
- 2 direct project hires: Senior Engineer (M1, FTE 1.0) + Commercial Deployment Lead (M9 / Q3, FTE 1.0) — Q7 + Q8 + Q9

---

## Minor flags — recommend tighten

### F1 — Phase 2 ramp timing inconsistent
- **Q7 main text:** "8–10 hires by month 24"
- **Q7 source map:** "Total estimated direct + indirect UK employment by end of Phase 2 (~month 30): 25–35 roles"
- **Q9 value-for-money:** "ramping to 8–10 within 3 years"

Three different time anchors (M24 / M30 / 3 years). Recommend aligning to **month 30** (matches Q6 Phase 2 window of M18–M30) and edit Q7 main text + Q9 value-for-money line accordingly. Single-word change in each.

### F2 — Sheffield postcode scope under-articulated
- **Q6:** conversion clause covers rollout across "S2 and S3 postcodes"
- **Q9 source map:** pilot cited as "S2 postcode"

Reads coherently on close reading (pilot in S2; conversion extends across S2+S3 rollout) but an assessor speed-reading the source map vs Q6 may flag. Recommend lengthening Q9 source map note to "S2 postcode pilot, S2/S3 rollout via conversion clause" so the two explicitly reconcile.

### F3 — Stale Q5 source-map analytical inference
- **Q5 prose:** £40k bridging = £25k Sheffield + £15k Applied Electronics (cash commitments)
- **Q5 source map (analytical-inferences block):** carries a leftover Forge note: "£40,000 in-kind contribution from allocated CEO and CTO time"

The source-map line is stale — it predates the cash-bridging resolution and contradicts Q5 prose and Q9. Recommend deleting or updating that single bullet so Q5's working notes match its narrative.

---

## Real finding — needs fix before submission

### R1 — Q9 existing-team labour arithmetic does not reconcile

**Q9 states (line 22):**
> "Existing core team allocation across 18 months (Nair 15%, Okafor 25%, Chen 15%): **£30,000** — blended at ~£20,000 per person-year equivalent."

**Actual arithmetic:** (0.15 + 0.25 + 0.15) FTE × 1.5 years × £20,000/person-year = **£16,500**, not £30,000. A £13,500 gap.

This is internal to Q9, but it propagates: labour line (£225k) and project total (£400k) currently rely on the £30k figure, which in turn underpins Q5's £400k envelope and Q9's £180k grant / £220k contribution split.

**Three fix options:**

| Option | Effect on Q9 totals | Notes |
|---|---|---|
| (a) Raise blended rate from £20k/PY → ~£36k/PY | None — £30k line preserved | Defensible — £36k/PY blended-fully-loaded (NI + pension + share of overhead) is plausible for mid-senior Sheffield-based founders/leads. Reconciles cleanly with 0.825 PY × £36k = £29.7k ≈ £30k. Q8 WP-lead percentages and Okafor 4.5pm reconciliation remain untouched. **Recommended.** |
| (b) Reduce existing-team line to ~£16.5k | Labour falls to £211.5k, total falls to £386.5k | Cascades: grant becomes £174k, contribution £213k. Requires updating Q5 + Q9 envelope language. Highest disruption. |
| (c) Raise FTE allocations (e.g. Nair 25%, Okafor 45%, Chen 25%) | None — £30k preserved | Conflicts with Q8 Okafor person-month reconciliation (4.5 pm = 25% of 18 months); raising Okafor to 45% breaks the WP2/WP4/WP5 distribution that was closed out 2026-06-08. **Not recommended.** |

**Recommendation:** Option (a). Edit Q9 line 22 to read "blended at ~£36,000 per person-year equivalent" — single-character (digit) change, preserves every downstream figure, no cascade into Q5 / Q8 / grant / contribution split.

---

## Pre-submission residual tasks (already flagged in drafts)

- Finance team to obtain confirmation letters for £25k Sheffield (Phase 1 extension) and £15k Applied Electronics co-investment for IUK finance form (Q9).
- Finance/technical team to retrieve and archive the DESNZ National Grid Carbon Intensity API extract (winter 2023/24, 580/195 gCO2e/kWh) supporting Q7.
- 2-page PDF appendices: Q4 innovation (state-of-art comparison), Q8 project plan (Gantt), Q8 risk register (RAID log).
- Pipeline reference back-confirm: Sarah Chen's Phase 2 named-operator pipeline view (Q6 "five paid commercial deployments" + Q8 WP6 "≥5 named operators by M18").
- 23% → ≥18% acceptance-threshold framing: confirm with Okafor / Nair that the gap is comfortable given Sheffield simulation precedent.

---

## Sign-off

**Resolved 2026-06-09 12:28 GMT+1 (Loch direction):**
- ✅ R1 — Q9 line 22 blended rate edited £20,000 → £36,000 per person-year (fully-loaded Sheffield mid-senior rate; reconciliation arithmetic now spelled out in the draft). Downstream totals unchanged.
- ✅ F1 — Q7 main text "by month 24" → "by month 30 (end of the 12-month post-project Phase 2 window)"; Q9 value-for-money line "within 3 years" → "by month 30 (end of the 12-month post-project Phase 2 window, per Q7)". Q7 source map already referenced M30 — all three references now aligned.
- ✅ F2 — Q9 source map updated: "S2 postcode pilot; S2/S3 rollout via conversion clause per Q6".
- ✅ F3 — Q5 source-map stale "£40,000 in-kind CEO/CTO time" inference bullet deleted; Q5 prose remains the single source of truth for the £40k bridging split.

The application is internally coherent and ready for human submission review. Word counts all within IUK caps (Q4 528/600, Q5 362/400, Q6 351/400, Q7 498/600, Q8 291/400 prose, Q9 386/400 prose).
