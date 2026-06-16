# Q4 — Your idea and innovation

*Word limit: 600. Draft word count: ~528 (final editing pass 2026-06-08; long sentences split, two passive constructions activated, light padding cut; facts and sources unchanged; ~88% of limit).*

## What is the innovation?

ThermaSync's Thermal Load-Shifting Controller (**TLSC**) synchronises thermal loads across distributed heating and cooling networks in real time, targeting a **23% reduction in network peak thermal demand without replacing existing plant or building infrastructure**. This 18-month single-applicant Smart Grant project advances TLSC from **TRL 4 to TRL 7**. Starting evidence at TRL 4: laboratory validation of the predictive algorithm on simulated 14-node network data, plus controller hardware bench-tested against three BMS manufacturers. End state at TRL 7: live demonstration in a 240-dwelling Sheffield City Council district heating network (paid pilot signed) and — contingent on TRL 7 validation — a six-building commercial portfolio at Brindleyplace Estate (LOI signed).

The innovation combines three elements not previously deployed together as a UK commercial product:

1. **Network-level coordination.** One optimiser across every node in a heat or process-cooling network, exploiting demand diversity rather than optimising each building in isolation.
2. **Predictive load-shifting 2–6 hours ahead of peak.** Driven by weather forecasts, building-thermal-mass models, and grid price signals. UK patent application **GB2024/TH0012** filed March 2024.
3. **Retrofit-first deployment** via BACnet and Modbus into existing building management systems (BMS) — no smart meters, heat pumps, or BMS replacement required.

## Why now

Heat in buildings accounts for **37% of total UK emissions** (DESNZ, *UK heat networks: market overview*, 2024), yet heat networks deliver under 3% of UK heat — against the Climate Change Committee Net Zero scenario of ~20% by 2050. Two regulatory shifts make this decade the critical window for network-level thermal control: the **Heat Networks (Market Framework) (GB) Regulations 2025** bring district networks under Ofgem regulation for the first time, and **Heat Network Zoning** under the Energy Act 2023 will designate zones where local authorities can mandate connection. Networks built into those zones need controllers that deliver peak management from day one — the gap TLSC closes.

## Advance beyond the current state of the art

UK building-control incumbents — Honeywell, Johnson Controls, Schneider Electric, Siemens Building Technologies, Trend, Priva, ABB, and Tridium — dominate the BMS market (Carbon Trust *DTEM Buyer's Guide*, 2024). Their products optimise **inside each building**: setpoint scheduling, plant sequencing, fault detection. **None offers cross-network coordination of thermal load as a standard product**, leaving network operators without a deployable layer to capture demand diversity between connected buildings.

Independent UK peer-reviewed work supports the underlying physics. A ScienceDirect paper (*Assessing the ability of electrified domestic heating in the UK to provide unplanned, short-term responsive demand*, 2021) finds that thermal load-shifting from electrified heating could remove up to **7 GW (≈5%) of GB peak electricity demand**. A 2019 ResearchGate study (*Demand side management in district heating systems by innovative control*) reports that **2–3 hour ahead thermal demand forecasting delivers an average 25% reduction in individual-building thermal load** — directly comparable in magnitude to ThermaSync's internally-simulated **23% network-level peak reduction**, which this project will revalidate against live operational data at Sheffield and Brindleyplace. ThermaSync's specific advance is to operationalise that potential as a **retrofit product layer above the BMS rather than replacing it** — the missing commercial step between DSM literature and a network-operator-grade controller for the newly-regulated heat-network market.

## Freedom to operate

A freedom-to-operate search completed **January 2024** identified no blocking patents on the network-level coordination approach. Patent application **GB2024/TH0012** (filed March 2024) protects the core algorithm. ThermaSync's **847,000-hour training dataset of thermal demand profiles across 23 building types** is held as a trade secret. Project IP follows the same strategy: algorithm enhancements patented, operational data retained as know-how, integration code released only where commercially neutral.

---

*Source map for verification stage:*

- TLSC description, 23% target, retrofit-first BACnet/Modbus, 847k-hour dataset (23 building types), GB2024/TH0012, FTO Jan 2024 → `company-profile.md`
- Sheffield (paid pilot signed) + Brindleyplace (LOI, contingent on TRL 7) pilot status → `company-profile.md`
- TRL 4 starting point ("Current TRL: 4", evidence = simulated 14-node validation + bench testing with three BMS manufacturers) → `company-profile.md` chunk 1
- Heat = 37% UK emissions; <3% heat-network share; ~20% by 2050 → `grant-research.json` finding #5 (DESNZ 2024)
- Heat Networks (Market Framework) Regs 2025 → `grant-research.json` finding #6
- Heat Network Zoning / Energy Act 2023 → `grant-research.json` finding #7
- Incumbent BMS suppliers list → `research-notes-innovate_uk-thermasync.md` + Carbon Trust DTEM (2024)
- 7 GW / ≈5% peak demand finding → `grant-research.json` finding #11 (ScienceDirect 2021)
- 25% individual-building reduction → `grant-research.json` finding #10 (ResearchGate 2019)

*Items NOT in Q4 (will appear elsewhere):*
- £340m TAM (Frontier Economics, 2023) — Q6 commercialisation
- Quantified CO2 avoidance — Q7 impact
