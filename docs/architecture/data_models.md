# Data Models

## Impact model registry

### Overview

The **impact model registry** (`modules/impact_models/`) maps each CI type to the set of climate-driven impacts it may experience. The registry is YAML-file-driven: one file per CI type, auto-discovered at startup — no manual registration is required.

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
| Operations | Revenues loss |
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

---

## NbS–Hazard matrix

### Overview

The **NbS–Hazard matrix** (`modules/nbs/`) encodes the effectiveness of 74 Nature-Based Solutions against 29 climate hazards, drawn from the D1.1 NbS Catalogue (Kuschel et al., 2025).

### Data format

```python
# 74 NbS types, keyed by 3-letter code
NBS_CODES = {
    "BRC": "Bio-retention cells",
    "BSW": "Bioswales",
    "GPV": "Green permeable pavements",
    # ...
}

# 29 hazard types
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

### Backwards-compatible `NbS_list`

Pages access NbS data through the auto-generated `NbS_list` dict:

```python
from modules.nbs import NbS_list

# Structure:
# NbS_list[hazard_name]["Yes"]        → list of primary NbS names
# NbS_list[hazard_name]["Supportive"] → list of supportive NbS names

primary_nbs = NbS_list["Extreme high temperatures (Heatwave)"].get("Yes", [])
```

### How it is used in the DST

When the PRI calculation identifies active hazards for an asset, the DST:

1. Looks up each hazard in `NbS_list` to retrieve candidate NbS
2. Joins with MCA scores from the D1.1 catalogue
3. Ranks candidates by weighted MCA score
4. Presents the ranked list for user selection

---

## Köppen-Geiger classification

The Köppen-Geiger classification raster is stored in `Koppen/` as a GeoTIFF at 0.1° spatial resolution, based on the Beck et al. (2018) 1991–2020 climatology (the source 1 km raster is resampled to the DST grid). Both Specific Site and Custom Site analyses sample the raster at the asset location to provide local climate-zone context for hazard likelihood and NbS suitability.

---

## References

- `modules/impact_models/README.md` — schema documentation and template
- D2.1 Appendix A — impact model source tables
- D2.1 Appendix B — sensitivity index lookup tables
- D1.1 Tables 2.1, 5.1–5.8 — NbS catalogue and hazard-NbS matrix
- Kuschel et al. (2025) — NbS effectiveness data (`nbs_hazard_matrix.py`)
- Beck et al. (2018) — Köppen-Geiger climate classification 1991–2020
