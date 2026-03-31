"""
Impact models registry.

Data lives in modules/impact_models/data/*.yaml (one file per CI type).
Files are auto-discovered - no manual registration needed.

YAML schema (snake_case keys):
  infrastructure: <name>
  impacts:
    - asset: <asset name>
      climate_driver: <climate driver>
      type_of_impact: Operations | Maintenance | Damages
      impact_model: <impact description>
      recommended_climate_indicator: <D2.1 recommended indicator>
      dictionary_key: <clima-ind-viz index_type>
      used_climate_indicator: <actual indicator used>
      possible_hazards: [list of hazard strings]

Derived keys (computed):
  Consequences: derived from Type of impact
"""

from pathlib import Path
import yaml

_DATA_DIR = Path(__file__).parent / "data"

ROW_KEYS = [
    "Infrastructure",
    "Asset",
    "Climate driver",
    "Type of impact",
    "Impact model",
    "Recommended climate Indicator",
    "Dictionary Key",
    "Used climate Indicator",
    "Possible Hazards",
]

YAML_TO_ROW = {k.lower().replace(" ", "_"): k for k in ROW_KEYS}

_CONSEQUENCES = {
    "Operations": "Revenues loss",
    "Maintenance": "Increase OPEX",
    "Damages": "Increase CAPEX",
}


def _load_yaml(path: Path) -> tuple[str, list[dict]]:
    """Load and flatten a YAML file. Returns (infrastructure_name, rows)."""
    data = yaml.safe_load(path.open(encoding="utf-8"))
    ci_name = data.get("infrastructure", path.stem)
    seen = {}

    for entry in data.get("impacts") or []:
        row = {"Infrastructure": ci_name}
        for yaml_key, value in entry.items():
            row_key = YAML_TO_ROW.get(yaml_key, yaml_key)
            row[row_key] = value

        row["Consequences"] = _CONSEQUENCES.get(row.get("Type of impact"), "")

        # Deduplicate by (Asset, Climate driver, Type of impact, Impact model)
        # Note: Current data has no duplicates; this is for future-proofing
        key = (
            row.get("Asset"),
            row.get("Climate driver"),
            row.get("Type of impact"),
            row.get("Impact model"),
        )
        if key not in seen:
            seen[key] = row
        else:
            seen[key]["Possible Hazards"] = sorted(
                {
                    *seen[key].get("Possible Hazards", []),
                    *row.get("Possible Hazards", []),
                }
            )

    return ci_name, list(seen.values())


def _load_all() -> dict[str, list[dict]]:
    """Load all YAML files and return dict mapping CI name to rows."""
    return {
        _load_yaml(path)[0]: _load_yaml(path)[1]
        for path in sorted(_DATA_DIR.glob("*.yaml"))
    }


ALL_IMPACT_MODELS: dict[str, list[dict]] = _load_all()


def get_all_impact_data() -> list[dict]:
    """Return all impact model rows across all infrastructure types."""
    return [row for rows in ALL_IMPACT_MODELS.values() for row in rows]


def get_ci_type_names() -> list[str]:
    """Return CI type names in alphabetical order."""
    return list(ALL_IMPACT_MODELS.keys())


def get_impact_data_for_infrastructure(name: str) -> list[dict]:
    """Return impact model rows for a specific infrastructure type."""
    return ALL_IMPACT_MODELS.get(name, [])
