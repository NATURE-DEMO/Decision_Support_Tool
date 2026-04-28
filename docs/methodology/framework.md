# Risk Assessment Framework

## Overview

The NATURE-DEMO risk assessment methodology is defined in **Deliverable D2.1** and follows an internationally recognised risk formula:

$$
\text{Risk} = \text{Hazard} \times \text{Exposure} \times \text{Vulnerability}
$$

The methodology is structured into **three complementary assessment levels** of increasing depth and data demand, allowing practitioners to calibrate the analysis to their information availability and decision context.

---

## Three-level assessment structure

| Level | Name | Method | Key output |
|-------|------|--------|------------|
| **1** | Qualitative risk perception | RAMS SHEEP participatory scoring | CI condition per KPI per scenario (1–5 scale) |
| **2** | Semi-quantitative pre-screening | PRI = HI × EI × VI | Potential Risk Index per asset/hazard; MCA-ranked NbS; Residual PRI |
| **3** | Quantitative analysis | Damage/vulnerability curves + economic valuation | Monetised risk; NPV and BCR for adaptation options |

The three levels are designed to be used **sequentially** — Level 1 identifies priority areas, Level 2 pre-screens risks, and Level 3 delivers investment-grade analysis — but each level can also stand alone depending on stakeholder needs.

---

## Hazard taxonomy

The methodology recognises four broad hazard categories, each with chronic (slow-onset) and acute (event-based) components:

| Category | Chronic hazards | Acute hazards |
|----------|----------------|---------------|
| **Temperature** | Changing temperature patterns, permafrost thaw | Heatwave, cold snap, wildfire |
| **Wind** | Changing wind patterns | Storm, tornado, blizzard |
| **Water** | Changing precipitation patterns, water stress | Drought, heavy precipitation, flood |
| **Solid mass** | Soil erosion | Landslide, avalanche, subsidence |

---

## Critical infrastructure taxonomy

The D2.1 methodology defines eight core CI types. The DST implementation extends this to twelve by adding Buildings, Industrial buildings, Water infrastructure, and Energy infrastructures. The eight D2.1 types are:

| Sector | CI type | Key assets |
|--------|---------|------------|
| **Transportation** | Roads | Pavement, drainage, slopes/embankments, signage |
| | Railways | Track/platform, drainage, electrical, structures |
| | Tunnels | Ventilation, heating/defrost, drainage, structural elements |
| | Bridges | Deck/surfaces, structural elements, drainage, foundations |
| **Water Management** | Dams | Spillway, water intake, downstream face, penstock |
| | River training | Embankments, channel bed, weirs, ramps |
| | Torrent control | Embankments, rip-rap/levées, check dams, ground sills |
| **Urban** | Green spaces | Green areas, plants |

---

## Climate data foundation

All three levels draw on EURO-CORDEX climate projections processed by the **clima-data** pipeline into 23 climate indices. Projections are available for:

- **Baseline**: historical 1981–2010
- **Mid-term 2050**: short (2011–2040) and medium (2041–2070) horizons
- **Long-term 2100**: long horizon (2071–2100)
- **Scenarios**: RCP4.5 (moderate emissions) and RCP8.5 (high emissions)
- **Uncertainty**: ensemble statistics — mean, p10, p50, p90

For the full list of indices see the [clima-data documentation](https://nature-demo.github.io/clima-data/indicators/).

---

## Nature-Based Solutions catalogue

NbS recommendations are drawn from the **D1.1 NbS Catalogue** (74 NbS types across 16 families). Each NbS is characterised by:

- Applicable hazards (primary / supportive effectiveness)
- Five MCA criteria scores (see [Level 2](level2_prescreening.md))
- Cost range, implementation time, environmental impact, social acceptance
- Co-Benefit Factor (CBF = Environmental impact × 0.6 + Social acceptance × 0.4)

---

## References

- D2.1 — *Risk Assessment Framework for NbS-enhanced Critical Infrastructure*, NATURE-DEMO (2024)
- D1.1 — *NbS Catalogue for Critical Infrastructure*, NATURE-DEMO (2024)
- IHCantabria / FIHAC methodology adapted for EURO-CORDEX
