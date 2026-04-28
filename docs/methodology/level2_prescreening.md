# Level 2 — Semi-Quantitative Pre-Screening

## Overview

Level 2 is the **core analytical engine** of the DST. It delivers a semi-quantitative risk pre-screening using the **Potential Risk Index (PRI)**, adapted from the IHCantabria / FIHAC methodology for EURO-CORDEX climate data (D2.1 §5.3).

$$
\text{PRI} = \text{HI} \times \text{EI} \times \text{VI}
$$

where:

| Symbol | Name | Range | Description |
|--------|------|-------|-------------|
| **HI** | Hazard Index | 0 – 5 | Projected change in a climate driver relative to baseline |
| **EI** | Exposure Index | 1 – 5 | Asset financial exposure (CAPEX × annual revenues) |
| **VI** | Vulnerability Index | 0 – 5 | Sensitivity × (1 − Adaptive Capacity) |

After selecting one or more adaptation measures, the **Residual PRI (RPRI)** is computed to quantify the remaining risk:

$$
\text{RPRI} = \text{PRI} \times \text{AF} \quad \text{where } \text{AF} = 1 - \frac{\text{Technical\_efficiency}(\%)}{100}
$$

---

## Six-stage assessment workflow

### Stage 1 — Project setup

The user defines:

- **Location** — coordinates or city search (resolved via Nominatim / OSM)
- **CI sector and type** — one of the eight supported CI types
- **Asset components** — specific sub-elements of the CI (e.g., Pavement, Track, Drainage)
- **Financial data** — CAPEX (€) and annual revenues (€) for Exposure Index computation
- **Initial Adaptive Capacity** — current maintenance state, remaining service life, and existing adaptation measures

### Stage 2 — Hazard identification

Climate drivers are identified by mapping EURO-CORDEX indices to the D2.1 hazard taxonomy (Table 18). Nine hazard drivers are supported:

| Hazard driver | Primary climate index | Notes |
|---------------|----------------------|-------|
| High precipitation (chronic) | `prcptot_year` | Substitute for monthly mean precip |
| High precipitation (acute) | `rx1day_rp100`, `rx5day_rp100` | 100-year return period events |
| Low precipitation / drought (chronic) | `prcptot_year` | |
| Low precipitation / drought (acute) | `spei3_severe_prob` | SPEI-3 ≤ −1.5 probability |
| Snow intensity | `solidprcptot_winter` | Winter accumulated snow |
| High temperature (chronic) | `tg_year`, `tx40` | Annual mean and extreme days |
| Low temperature (acute) | `tn20` | Days Tmin < −20 °C |
| Wind (chronic) | `sfcwind_year`, `sfcwind10` | Mean speed and ≥10 m/s days |
| Wind (acute) | `sfcwind20` | Storm-force ≥20 m/s days |

Green spaces additionally use `hurs_year`, `hurs40_days`, and `par_plant_level`.

### Stage 3 — Hazard Index (HI)

For each climate driver the HI quantifies the **percentage change from the historical baseline** to the selected future scenario and time horizon. Changes are converted to a 0–5 integer score using D2.1 Table 19 thresholds:

| % change vs. baseline | HI score |
|-----------------------|-----------|
| No change | 0 |
| ≤ 10 % | 1 |
| ≤ 25 % | 2 |
| ≤ 50 % | 3 |
| ≤ 75 % | 4 |
| ≤ 100 % | 5 |

**Climate scenarios** available for HI computation:

| Scenario label | Period | RCP |
|---------------|--------|-----|
| Historic baseline | 1981–2010 | — |
| Mid-term 2050 — moderate | 2041–2070 | RCP4.5 |
| Mid-term 2050 — high | 2041–2070 | RCP8.5 |
| Long-term 2100 — moderate | 2071–2100 | RCP4.5 |
| Long-term 2100 — high | 2071–2100 | RCP8.5 |

### Stage 4 — Exposure Index (EI)

EI is scored 1–5 from the intersection of CAPEX range and annual revenues range (D2.1 Table 21):

|  | Revenues < 1 M€ | Revenues 1–10 M€ | Revenues > 10 M€ |
|--|:-:|:-:|:-:|
| **CAPEX < 10 M€** | 1 | 2 | 3 |
| **CAPEX 10–100 M€** | 2 | 3 | 4 |
| **CAPEX > 100 M€** | 3 | 4 | 5 |

### Stage 5 — Vulnerability Index (VI)

$$
\text{VI} = \text{Sensitivity} \times (1 - \text{AC})
$$

**Sensitivity** is pre-defined per CI type × impact type in D2.1 Appendix B (scale 0–5):

| Score | Meaning |
|-------|---------|
| 0 | No effect |
| 1 | Marginal effect, days of disruption |
| 2 | Moderate effect, weeks of disruption |
| 3 | Significant effect, months of disruption |
| 4 | Major effect, months of disruption + partial replacement |
| 5 | Critical effect, months of disruption + full replacement |

**Adaptive Capacity (AC)** defaults to **0** (baseline — no adaptive capacity adjustment). A higher AC value represents a more adaptive asset and lowers the Vulnerability Index. AC is bounded in [0, 0.4] and is refined from a baseline value (AC₀) through three parameters:

- Remaining service life (Greenfield +0.10 / Intermediate 0 / End-of-life −0.10)
- Maintenance level (High +0.10 / Medium 0 / Low −0.10)
- Design topology (Resilient +0.10 / Acceptable 0 / Not acceptable −0.10)

Final AC = AC₀ + sum of adjustments, capped at 0.4.

!!! note "VI formula — implementation"
    The DST computes `VI = Sensitivity × (1 − AC)` where AC ∈ [0, 0.4] is an adaptive capacity factor.  
    AC = 0 → no adjustment; VI equals Sensitivity.  
    AC = 0.4 → maximum adaptive capacity; VI is 60 % of Sensitivity.  
    This is a linearised adaptation of the D2.1 formulation; both lower VI for more adaptive assets.

### Stage 6 — PRI computation and outputs

$$
\text{PRI}[\text{asset, impact, hazard, scenario, horizon}] = \text{HI} \times \text{EI} \times \text{VI}
$$

The raw product is mapped to a risk tier using the following lookup table:

| HI × EI × VI product | PRI score | Risk label |
|-----------------------|:---------:|------------|
| 0 | 0 | No Risk |
| ≤ 25 | 1 | Very Low |
| ≤ 50 | 2 | Low |
| ≤ 75 | 3 | Medium |
| ≤ 100 | 4 | High |
| ≥ 125 | 5 | Extreme |

The theoretical maximum is HI(5) × EI(5) × VI(5) = **125**, but in practice scores cluster well below this ceiling.

**Visualisations produced:**

- Heat map — Assets × Hazard drivers (colour-coded by PRI)
- Bar chart — Top 10 risks across all asset–hazard combinations
- Impact-type breakdown — grouped by Operations / Maintenance / Damages

---

## Nature-Based Solutions ranking (MCA)

After PRI computation, applicable NbS are retrieved from the D1.1 catalogue by filtering the NbS–Hazard matrix for each active hazard. Each candidate NbS (and conventional grey alternatives) is then scored on five weighted criteria:

| Criterion | Weight |
|-----------|-------:|
| Technical efficiency (% risk reduction) | 30 % |
| Implementation cost | 20 % |
| Implementation time | 10 % |
| Environmental impact | 25 % |
| Social acceptance | 15 % |

$$
\text{MCA score} = \sum_{i} w_i \times s_i
$$

$$
\text{Co-Benefit Factor (CBF)} = \text{Environmental impact} \times 0.6 + \text{Social acceptance} \times 0.4
$$

CBF is reported separately — it is not included in the MCA score weights.

---

## Residual risk

Once the user selects an adaptation option, the Adaptation Factor (AF) is computed from its technical efficiency and applied to derive the residual risk:

$$
\text{AF} = 1 - \frac{\text{Technical\_efficiency}(\%)}{100}
$$

$$
\text{RPRI}_\text{NbS} = \text{PRI} \times \text{AF}_\text{NbS} \qquad \text{RPRI}_\text{conv} = \text{PRI} \times \text{AF}_\text{conventional}
$$

$$
\Delta\text{RPRI} = \text{RPRI}_\text{conv} - \text{RPRI}_\text{NbS} \quad (\text{positive} = \text{NbS outperforms grey})
$$

A side-by-side comparison dashboard shows conventional vs. NbS residual risk across all assets and hazards.

---

## References

- D2.1 §5.3 — Semi-quantitative risk pre-screening methodology
- D2.1 Table 18 — Climate indicator to hazard driver mapping
- D2.1 Table 19 — HI scoring thresholds
- D2.1 Table 21 — Exposure Index matrix
- D2.1 Appendix B — Sensitivity index lookup tables
- D2.1 Appendix C — MCA criteria weights
- D1.1 Tables 2.1, 5.1–5.8 — NbS catalogue and effectiveness matrix
