# Data Models

The DST data layer is intentionally separated from the application code. Two of the most heavily used tables — the **impact model registry** and the **NbS–Hazard matrix** — live as standalone data modules, designed around three properties:

- **Modular** — each table is a self-contained file (or set of files) with no dependencies on UI or risk-calculation code, and can be edited or reviewed in isolation.
- **Inspectable** — domain experts can read the data directly without tracing it through Python logic: impact models are plain YAML, and the NbS matrix is a flat mapping of 3-letter codes to names together with per-hazard lists of applicable codes.
- **Extensible** — both tables are picked up automatically by the app. New impact YAML files are auto-discovered at module import time; new NbS codes or hazards added to the matrix data structures propagate through the derived `NbS_list` without any further changes.

This makes it possible to update the underlying climate-impact and adaptation knowledge base — including by non-developers — without touching the calculation engine or the Streamlit UI.

## Impact model registry

### Overview

The **impact model registry** (`modules/impact_models/`) maps each critical-infrastructure (CI) type to the set of climate-driven impacts it may experience. The registry is YAML-file-driven: one file per CI type, auto-discovered at module import time — no manual registration is required.

### Supported CI types

| File | CI type |
|------|---------|
| `road.yaml` | Roads |
| `railway.yaml` | Railways |
| `bridges.yaml` | Bridges |
| `tunnels.yaml` | Tunnels |
| `dams.yaml` | Dams |
| `river.yaml` | River training |
| `torrent.yaml` | Torrent control |
| `green_spaces.yaml` | Green spaces |
| `buildings.yaml` | Buildings |
| `energy_infrastructures.yaml` | Energy infrastructures |
| `industrial_buildings.yaml` | Industrial buildings |
| `water_infrastructure.yaml` | Water infrastructure |

The registry covers eight of the nine CI typologies in D2.1 Table 6 (Roads, Railways, Tunnels, Bridges, Dams, River training, Torrent control, Green spaces) and additionally provides Buildings, Industrial buildings, Water infrastructure, and Energy infrastructures to support the demonstrator-site analyses. Electricity distribution networks are listed in D2.1 Table 6 but are a planned addition rather than part of the current registry.

### YAML schema

Each YAML file has the following structure:

```yaml
infrastructure: Road   # Optional — defaults to filename stem
impacts:
  - asset: Pavement
    climate_driver: Changes in snow intensity
    type_of_impact: Operations          # Operations | Maintenance | Damages
    impact_model: Stop of operations due to snow accumulation
    recommended_climate_indicator: Winter months accumulated snow
    dictionary_key: solidprcptot_winter  # clima-ind-viz API index_type
    used_climate_indicator: Winter accumulated solid precipitation (mm)
    possible_hazards:
      - Snow drift
      - Snow avalanches
      - Extreme cold temperatures (Coldwave, cold snap)
```

### Schema fields

| Field | Required | Description |
|-------|----------|-------------|
| `asset` | ✅ | Asset component affected (e.g., "Pavement", "Track") |
| `climate_driver` | ✅ | Climate driver causing the impact |
| `type_of_impact` | ✅ | `Operations`, `Maintenance`, or `Damages` |
| `impact_model` | ✅ | Textual description of the impact mechanism |
| `recommended_climate_indicator` | ✅ | D2.1 recommended indicator name |
| `dictionary_key` | ✅ | `index_type` value for the clima-ind-viz API |
| `used_climate_indicator` | ✅ | Human-readable indicator name with units |
| `possible_hazards` | ✅ | List of hazard strings from `HAZARD_CODES` in `nbs_hazard_matrix.py` |

### Derived field

The `Consequences` field is auto-computed from `type_of_impact`:

| `type_of_impact` | `Consequences` |
|-----------------|---------------|
| Operations | Revenue loss |
| Maintenance | Increase OPEX |
| Damages | Increase CAPEX |

### Python API

```python
from modules.impact_models import (
    get_all_impact_data,
    get_ci_type_names,
    get_impact_data_for_infrastructure,
)

ci_types = get_ci_type_names()
road_impacts = get_impact_data_for_infrastructure("Road")
all_impacts = get_all_impact_data()
```

### Adding a new CI type

1. Drop a new file `<ci_name>.yaml` in `modules/impact_models/data/` following the schema above (a complete template lives in `modules/impact_models/README.md`).
2. Restart the app — the loader auto-discovers the file; no registration code to edit.
3. The new CI type immediately appears in `get_ci_type_names()` and in the DST's CI-type selector, with its impacts available to the PRI calculation.

Existing CI types can be inspected or revised the same way: open the YAML file, edit the rows, restart.

---

## NbS–Hazard matrix

### Overview

The **NbS–Hazard matrix** (`modules/nbs/`) classifies 74 Nature-Based Solutions (NbS) as primary (direct) or supportive (indirect) solutions against 29 natural hazards. The matrix in `nbs_hazard_matrix.py` is reproduced from the peer-reviewed framework of Kuschel et al. (2025, *Infrastructures* 10(12), 318, [DOI:10.3390/infrastructures10120318](https://doi.org/10.3390/infrastructures10120318)), produced within the NATURE-DEMO project context, with corrections noted in the module docstring (transposition error, 3-letter-code corrections, LFA typo). Quantitative effectiveness is **not** encoded here; it is handled separately via the MCA criteria.

### Data format

```python
# 74 NbS types, keyed by 3-letter code
NBS_CODES = {
    "BRC": "Bio-retention cells",
    "BSW": "Bioswales",
    "GPV": "Green permeable pavements",
    # ...
}

# 29 natural hazards
HAZARD_CODES = {
    "EHT": "Extreme high temperatures (Heatwave)",
    "DRT": "Drought",
    "PLF": "Pluvial flood, heavy rainfall and surface runoff",
    # ...
}

# Primary (direct) effectiveness
NBS_MATRIX = {
    "EHT": ["BRC", "BSW", "GPV", ...],  # NbS codes that directly address this hazard
    # ...
}

# Supportive (indirect / co-benefit) effectiveness
NBS_MATRIX_SUPPORTIVE = {
    "EHT": ["BRM", "CGR", ...],
    # ...
}
```

### Derived `NbS_list`

Pages access NbS data through the `NbS_list` dict, derived at import time from the four data structures above:

```python
from modules.nbs import NbS_list

# Structure:
# NbS_list[hazard_name]["Yes"]        → list of primary NbS names
# NbS_list[hazard_name]["Supportive"] → list of supportive NbS names

primary_nbs = NbS_list["Extreme high temperatures (Heatwave)"].get("Yes", [])
```

### How it is used in the DST

When the Potential Risk Index (PRI) calculation identifies active hazards for an asset, the DST:

1. Looks up each hazard in `NbS_list` to retrieve candidate NbS (primary and supportive).
2. Presents the candidates to the user, who weights them against the D1.1 / D2.1 Multi-Criteria Analysis (MCA) criteria — technical efficiency, implementation cost, implementation time, environmental impact, and social acceptance.
3. Computes a weighted suitability score per option and ranks the list.
4. Returns the ranked list for user selection and downstream Residual-PRI (RPRI) calculation.

A pre-scored MCA database from WP1 is anticipated; until it is integrated, the DST collects MCA inputs interactively from the user.

### Extending the matrix

The matrix is decoupled from the rest of the codebase: only the four data structures above are exposed, and `NbS_list` is regenerated at import time from `NBS_CODES`, `HAZARD_CODES`, `NBS_MATRIX`, and `NBS_MATRIX_SUPPORTIVE`.

- **Add a new NbS method** — insert `"<3-letter code>": "<name>"` into `NBS_CODES`, then list the code under each applicable hazard in `NBS_MATRIX` (primary) and/or `NBS_MATRIX_SUPPORTIVE` (supportive).
- **Add a new hazard** — insert `"<3-letter code>": "<name>"` into `HAZARD_CODES`, then add the hazard's key with its NbS list to the matrix data structures.
- **Revise an existing entry** — edit the relevant lists directly; pages reading `NbS_list` pick up the change without modification.

When extending the matrix, also align hazard names with the `possible_hazards` strings used in the impact-model YAML files so that the PRI → NbS lookup remains consistent.

---

## Köppen-Geiger classification

The Köppen-Geiger classification rasters are stored in `Koppen/` as GeoTIFFs at 0.1° spatial resolution, derived from the Beck et al. (2023) 1 km Köppen-Geiger dataset. The repository bundles a 1991–2020 historical baseline plus mid- and end-of-century projection layers to support climate-zone framing across the time horizons used elsewhere in the DST. Both demonstrator-site and Custom Site analyses sample the raster at the asset location to inform hazard likelihood and NbS suitability; the layer is contextual and is not consumed as input to the PRI calculation.

---

## References

- `modules/impact_models/README.md` — schema documentation and template for adding a new CI type.
- D2.1 *Risk Assessment Framework*, Appendix A — impact model source tables.
- D2.1 *Risk Assessment Framework*, Appendix B — sensitivity index lookup tables.
- D2.1 *Risk Assessment Framework*, Table 6 — CI typology covered by the registry.
- D1.1 *NbS Catalogue for Critical Infrastructure*, Tables 2.1 and 5.1–5.8 — NbS catalogue and hazard–NbS relationships.
- Kuschel, E. et al. (2025). *A Systematic Framework for Assessing the Temporally Variable Protective Capacity of Nature-Based Solutions Against Natural Hazards.* *Infrastructures*, 10(12), 318. [DOI:10.3390/infrastructures10120318](https://doi.org/10.3390/infrastructures10120318) — source matrix reproduced (with documented corrections) in `modules/nbs/nbs_hazard_matrix.py`.
- Beck, H.E. et al. (2023). *High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained CMIP6 projections.* *Scientific Data*, 10, 724. [DOI:10.1038/s41597-023-02549-6](https://doi.org/10.1038/s41597-023-02549-6) — source dataset for `Koppen/`.

For the consolidated bibliography, see [`bibliography.md`](../bibliography.md).
