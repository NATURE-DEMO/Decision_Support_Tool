# Decision Support Tool

Climate change risk assessment platform for critical infrastructure, based on the NATURE-DEMO methodology (D2.1).

## Purpose

Assess climate change impacts on infrastructure by calculating Hazard Index (HI), Exposure Index (EI), Vulnerability Index (VI), and Potential Risk Index (PRI). Includes Nature-Based Solutions (NbS) matching for adaptation planning.

## Features

- Köppen-Geiger climate classification maps
- Climate indicator calculation via clima-ind-viz API
- PRI calculation with sensitivity and adaptive capacity
- NbS solution matching based on hazards
- General DST and site-specific demo modes

## Infrastructure Types

Road, Railway, Bridges, Tunnels, Green Spaces, Dams, River Training, Torrent Control

## Quick Start

```bash
uv run streamlit run Home.py
```

## Structure

```
.
├── Home.py                    # App entry point
├── pages/
│   ├── 1_General_DST.py      # General DST
│   └── 2_Specific_Site_DST_v2.py  # Demo sites
├── modules/
│   └── impact_models/        # Impact models (YAML)
└── tests/
```

## Impact Models

Stored in `modules/impact_models/data/*.yaml`. Auto-discovered - no registration needed.

## Testing

```bash
uv run pytest tests/test_impact_models.py -v
```

## Dependencies

Managed with `uv`. Install with `uv sync`.
