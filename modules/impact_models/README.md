# Impact Models

Data registry for climate impact models on critical infrastructure (CI) types.

## Quick Start

Want to add a new CI type (e.g., Electricity distribution)? Here's how:

1. **Create a new file** in `modules/impact_models/data/` named after your CI type (lowercase, underscores):
   ```bash
   touch modules/impact_models/data/electricity.yaml
   ```

2. **Copy the template** below into the file

3. **Run tests** to verify:
   ```bash
   uv run pytest tests/test_impact_models.py -v
   ```

That's it — no registration needed. The module auto-discovers all YAML files.

---

## Overview

This module loads impact model definitions from YAML files and exposes them via a simple API. Each YAML file contains impact data for one CI type (e.g., Road, Railway, Bridges).

## YAML Schema

### Top-level keys

| Field | Required | Description | Default |
|-------|----------|-------------|---------|
| `infrastructure` | No | CI type name | Filename (without `.yaml`) |
| `impacts` | Yes | List of impact entries | — |

### Impact entry keys

| Field | Required | Description |
|-------|----------|-------------|
| `asset` | Yes | Asset component affected (e.g., "Pavement", "Track") |
| `climate_driver` | Yes | Climate driver causing the impact (e.g., "Changes in precipitation") |
| `type_of_impact` | Yes | Impact category: `Operations`, `Maintenance`, or `Damages` |
| `impact_model` | Yes | Description of the impact (e.g., "Stop of operations due to heavy rain") |
| `recommended_climate_indicator` | Yes | D2.1 recommended climate indicator |
| `dictionary_key` | Yes | clima-ind-viz API `index_type` (e.g., `rx1day_rp100`) |
| `used_climate_indicator` | Yes | Human-readable indicator name |
| `possible_hazards` | Yes | List of hazard strings from the NbS hazard matrix (see Note below) |

> **Note**: For `possible_hazards`, use strings from `modules/nbs/nbs_hazard_matrix.py` → `HAZARD_CODES`. Example values:
> - `Extreme high temperatures (Heatwave)`
> - `Pluvial flood, heavy rainfall and surface runoff`
> - `Wildfire`
> - `Drought`
> - `Storms and strong winds`

### Valid values

- **`type_of_impact`**: `Operations` | `Maintenance` | `Damages`
- **`dictionary_key`**: Must be a valid [climate indicator](https://nature-demo.github.io/clima-data/indicators) (e.g., `rx1day_rp100`, `solidprcptot_winter`, `tn20`)

### Derived fields

The following field is auto-computed (not in YAML):

| Field | Source |
|-------|--------|
| `Consequences` | Derived from `type_of_impact`: <br>• `Operations` → `Revenues loss` <br>• `Maintenance` → `Increase OPEX` <br>• `Damages` → `Increase CAPEX` |

## File Naming

One YAML file per CI type. Filename should be lowercase with underscores:

```
data/
├── road.yaml       # Road infrastructure
├── railway.yaml    # Railway infrastructure
├── bridges.yaml   # Bridges
├── tunnels.yaml   # Tunnels
├── dams.yaml      # Dams
├── river.yaml     # River training
├── torrent.yaml   # Torrent control
└── green_spaces.yaml  # Green spaces
```

## Adding a New CI Type

1. Create a new YAML file in `modules/impact_models/data/`. Use lowercase with underscores:
   ```
   modules/impact_models/data/my_new_ci.yaml
   ```

2. Add content following the template below

3. Test with: `uv run pytest tests/test_impact_models.py -v`

No registration needed — the module auto-discovers all `.yaml` files in the `data/` directory.

### Template

```yaml
# infrastructure: <CI type name>  # Optional: defaults to filename
impacts:
  - asset: <component name>
    climate_driver: <driver name>
    type_of_impact: Operations  # or Maintenance or Damages
    impact_model: <description>
    recommended_climate_indicator: <D2.1 indicator>
    dictionary_key: <clima-ind-viz index_type>
    used_climate_indicator: <human-readable name>
    possible_hazards:
      - <hazard 1>
      - <hazard 2>
```

### Complete Example

```yaml
infrastructure: Road
impacts:
  - asset: Pavement
    climate_driver: Changes in snow intensity
    type_of_impact: Operations
    impact_model: Stop of operations due to snow accumulation
    recommended_climate_indicator: Winter months accumulated snow
    dictionary_key: solidprcptot_winter
    used_climate_indicator: Winter accumulated solid precipitation (mm)
    possible_hazards:
      - Snow drift
      - Snow avalanches
      - Extreme cold temperatures (Coldwave, cold snap)
```

## API Usage

```python
from modules.impact_models import get_all_impact_data, get_ci_type_names

# Get all CI type names
ci_types = get_ci_type_names()

# Get impact data for a specific CI type
road_impacts = get_impact_data_for_infrastructure("Road")

# Get all impact data
all_impacts = get_all_impact_data()
```

## References

- D2.1 methodology: `docs/NATUREDEMO_D2.1_final.pdf`
- clima-ind-viz API: `https://naturedemo-clima-ind.dic-cloudmate.eu`
- Climate indicators: `https://nature-demo.github.io/clima-data/indicators`
