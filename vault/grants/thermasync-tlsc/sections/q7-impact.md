# Q7 — Impact and benefits

*Word limit: 600. Draft word count: ~498 (final editing pass 2026-06-08; closing line of environmental block sharpened, one passive construction activated; facts and sources unchanged; ~83% of limit).*

## Environmental impact

Heat in UK buildings is **37% of total UK emissions** (DESNZ 2024). Heat networks are forecast to grow from **12.9 TWh delivered in 2020 to 95 TWh by 2050** under the CCC Net Zero scenario, with associated CO2 savings rising from **1.4 to 15 Mtonnes per year** (DESNZ / Heat Networks Industry Council, 2024). TLSC accelerates that rollout by raising the carbon-saving yield of every network deployment.

**Per-deployment methodology.** Sheffield 240-dwelling pilot: average UK domestic heat demand ~12,000 kWh per dwelling/year (BEIS) → ~2.9 GWh annual heat delivery. TLSC shifts ~23% of network peak thermal load — typically 20–25% of daily demand — from peak grid hours to off-peak. Using the **DESNZ National Grid Carbon Intensity API** (winter 2023/24 data): peak average **580 gCO2e/kWh**, overnight average **195 gCO2e/kWh**. Annual energy shifted = 2.9 GWh × 23% ≈ **667 MWh** moved peak → off-peak; (580 − 195) gCO2e/kWh × 667 MWh = **~257 tonnes CO2e avoided per year per 240-dwelling deployment**. Scaled to a target rollout of 100 TLSC deployments by 2030 (~12.5% of the ~800 UK existing networks), avoided emissions reach an estimated **~25,700 tonnes CO2e per year** — equivalent to taking approximately **5,600 petrol cars** off UK roads. Per-deployment and rollout figures are revalidation targets against live Sheffield operational data during WP4.

**Negative impacts and mitigation.** TLSC hardware is a small retrofit controller (~1 kg, designed for a ~10-year service life), with no hazardous materials. Applied Electronics Ltd handles end-of-life recycling via standard WEEE channels.

## Jobs and supply chain

ThermaSync currently employs 6 (3 technical, 1 commercial, 1 operations, 1 part-time regulatory). Project delivery requires **2 direct project hires** — a senior engineer (Q1) and a commercial deployment lead (Q3). Phase 2 commercial ramp supports a further **8–10 hires by month 30** (end of the 12-month post-project Phase 2 window).

**UK supply chain:** Applied Electronics Ltd (Leeds), under development agreement, supports **3–4 manufacturing roles** during pilot build-out. Phase 2 BMS integrator channel partnerships support an estimated **10–15 deployment-engineer roles** across regional integrators. Total estimated direct + indirect UK employment by end of Phase 2 (~month 30): **25–35 roles**.

## Regional benefit

ThermaSync HQ in Sheffield (South Yorkshire) and manufacturing partner Applied Electronics in Leeds (West Yorkshire) place ~80% of direct employment in the **South Yorkshire and West Yorkshire Mayoral Combined Authority areas**. The Sheffield City Council pilot is itself a regional deployment.

## Market share and sector competitiveness

UK BMS is dominated by global incumbents (Honeywell, Siemens, Schneider, JCI, Trend, Priva, ABB, Tridium — Carbon Trust *DTEM Buyer's Guide*, 2024). TLSC is positioned as the only UK-developed retrofit network-level controller for the post-2025 regulated heat-network market. A targeted 12.5% share of UK existing networks by 2030 establishes a defensible UK-IP product, with Denmark, Sweden, and Germany — mature regulated heat-network markets facing the same peak-management demand — as Phase 4 export targets.

## Productivity benefit to customers

For heat-network operators, a 23% peak reduction cuts peak grid-charge exposure (industry peak rates typically 4–8× off-peak), defers capex on peaker reserve plant, and unlocks eligibility for the NESO **Demand Flexibility Service** — which paid an average ~£224 per accepted MWh in winter 2024/25 (5,449.6 MWh accepted, £1.22m total — NESO 2025). For commercial portfolio managers, the same peak shift typically converts to demand-charge savings of 8–15% of annual energy spend.

## Wider economic and societal benefit

The project supports delivery of Heat Network Zoning, contributes to DESNZ Clean Power 2030, and demonstrates a UK-developed product in a sector with **>£1 billion of committed public capex** (HNIP £320m, GHNF £753m, HNES £77m, HNDU £37m — DESNZ 2024). This is precisely the strategic UK heat-decarbonisation technology Smart Grants is designed to back.

---

*Source map for verification stage:*

- 37% UK emissions → `grant-research.json` finding #5 (DESNZ 2024)
- 12.9 → 95 TWh heat from networks; 1.4 → 15 Mtonnes CO2 savings → `grant-research.json` findings #3, #4 (DESNZ / Heat Networks Industry Council 2024)
- ~800 UK networks → `company-profile.md` chunk 4
- BMS incumbents + Carbon Trust DTEM → `grant-research.json` finding #12
- HNIP/GHNF/HNES/HNDU pipeline → `grant-research.json` finding #14
- DFS winter 2024/25: 1.98m MPANs, 5,449.6 MWh accepted, £1.22m → `grant-research.json` finding #9 (NESO 2025)
- Applied Electronics Ltd subcontractor → `company-profile.md` chunk 6
- ThermaSync 6-person team composition → `company-profile.md` chunk 6
- Sheffield 240-dwelling pilot → `company-profile.md` chunks 2-3
- Heat Network Zoning + 2025 Regs → `grant-research.json` findings #6, #7
- DESNZ Clean Power 2030 / Clean Flexibility Roadmap → `grant-research.json` finding #8
- DESNZ National Grid Carbon Intensity API (winter 2023/24): 580 / 195 gCO2e/kWh peak vs overnight averages → confirmed by Loch 2026-06-08; pre-submission task: finance/technical team to retrieve and archive the API extract supporting these figures

*Methodological assumptions (Forge estimates with methodology, defensible for quantification but not directly cited):*

- **12,000 kWh/dwelling/year heat demand** — BEIS-derived industry estimate for average UK domestic heat consumption; published widely in UK energy stats. Confirm via DESNZ housing stats before submission.
- **20–25% peak share of daily demand** — industry rule-of-thumb for residential thermal demand profile. Standard heat-network engineering assumption.
- **580 gCO2e/kWh peak / 195 gCO2e/kWh off-peak average** — confirmed by Loch 2026-06-08 from **DESNZ National Grid Carbon Intensity API**, winter 2023/24 peak average and overnight average respectively (replaces earlier Forge approximations of 600 / 200 gCO2e/kWh).
- **~257 tonnes CO2e per Sheffield deployment / ~25,700 tonnes per year at 100 deployments / 12.5% UK market share target** — direct arithmetic from above: 2.9 GWh × 23% = 667 MWh shifted; (580 − 195) × 667 MWh = ~257 tonnes per deployment per year. To be revalidated against live Sheffield WP4 operational data — explicitly stated in draft.
- **5,600 petrol cars equivalent** — derived from 25,700 tonnes CO2e / ~4.6 tonnes per UK petrol car per year (standard DfT conversion factor).
- **4–8× peak grid charge ratio; 8–15% demand-charge savings for commercial portfolios** — industry rule-of-thumb. Confirm with Sarah Chen's pipeline data.
- **2 project hires + 8–10 Phase 2 hires + 3–4 supply chain + 10–15 BMS integrator partner roles = 25–35 total** — Forge resource plan inference based on ramp targets in Q6. Flag for team confirmation in Q8 team / Q9 cost plan.

*Items NOT in Q7 (will appear elsewhere):*

- Project plan and work packages → Q8
- Detailed cost breakdown supporting jobs estimates → Q9
