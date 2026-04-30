# Level 3 — High-Resolution Quantitative Analysis

## Purpose

Level 3 delivers an **investment-grade quantitative risk analysis** that monetises climate impacts and provides the economic evidence base for adaptation decisions. It builds on Level 2's asset inventory and PRI results, adding high-resolution climate data, damage/vulnerability curves, and economic valuation.

---

## Inputs (additional to Level 2)

| Input | Source | Notes |
|-------|--------|-------|
| Downscaled climate data | EURO-CORDEX 10–50 km resolution | Finer spatial resolution than Level 2 |
| Damage / vulnerability curves | Literature (Nirandjan et al. 2024; IPCC AR6) | Hazard intensity → % damage |
| CAPEX, OPEX, revenue streams | Asset owner / financial data | Required for monetised risk |
| Discount rate, asset lifetime | Regulatory / project context | For NPV / BCR computation |

---

## Outputs

| Metric | Description |
|--------|-------------|
| **Monetised risk** | Expected annual damage (EAD) in € per asset per hazard |
| **RPRI monetised** | Residual risk after adaptation, in € |
| **NPV** | Net Present Value of adaptation investment |
| **BCR** | Benefit-Cost Ratio of NbS vs. grey infrastructure |

---

## Methodology

Level 3 uses the same formula structure as Level 2 but replaces the semi-quantitative indices with physical damage functions:

$$
\text{EAD}[\text{asset, hazard}] = \int P(\text{intensity}) \times D(\text{intensity}) \times \text{Asset value} \, d(\text{intensity})
$$

where:

- $P(\text{intensity})$ — exceedance probability from the climate hazard curve
- $D(\text{intensity})$ — damage fraction from the vulnerability curve (0–1)
- **Asset value** — replacement cost (CAPEX) or business disruption cost (revenue)

The **Benefit-Cost Ratio** for a given adaptation option (NbS or grey) is:

$$
\text{BCR} = \frac{\text{EAD}_\text{baseline} - \text{EAD}_\text{adapted}}{\text{Annualised adaptation cost}}
$$

---

## Implementation in D2.3

The High Resolution DST exposes a Level 3 tab on each demonstrator-site view that renders partner-supplied site-specific assessments, data tables, and interpretation reports from the GitHub content system. Where Level 3 material is not yet available for a site, the application displays a *"No Level 3 data found."* message. The depth of supplied content varies by demonstrator.

An automated quantitative engine (EAD integration, NPV/BCR module, Monte Carlo uncertainty propagation) requires site-specific damage/vulnerability curves compiled from literature and is not part of D2.3.

---

## References

- D2.1 §5.4 — High-resolution quantitative risk analysis
- Nirandjan et al. (2024) — Damage functions for European CI
- IPCC AR6 Working Group II — Vulnerability and exposure data
