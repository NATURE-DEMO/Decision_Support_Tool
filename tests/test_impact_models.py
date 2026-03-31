"""
Unit tests for impact_models module.
"""

import pytest
from modules.impact_models import (
    get_all_impact_data,
    get_ci_type_names,
    get_impact_data_for_infrastructure,
    ALL_IMPACT_MODELS,
    YAML_TO_ROW,
)


class TestDataLoading:
    def test_total_rows(self):
        """Test that all impact models are loaded."""
        data = get_all_impact_data()
        assert len(data) == 184, f"Expected 184 rows, got {len(data)}"

    def test_ci_types_count(self):
        """Test that all CI types are discovered."""
        ci_types = get_ci_type_names()
        assert len(ci_types) == 8, f"Expected 8 CI types, got {len(ci_types)}"

    def test_yaml_to_row_mapping_complete(self):
        """Test that all row keys have a YAML mapping."""
        from modules.impact_models import ROW_KEYS

        for key in ROW_KEYS:
            yaml_key = key.lower().replace(" ", "_")
            assert yaml_key in YAML_TO_ROW, f"Missing mapping for {key}"

    def test_all_yaml_files_loaded(self):
        """Test that all YAML files are discovered."""
        expected_infras = {
            "Bridges",
            "Dams",
            "green spaces",
            "Railway",
            "River training infrastructure",
            "Road",
            "Torrent control infrastructure",
            "Tunnels",
        }
        actual = set(get_ci_type_names())
        assert actual == expected_infras, f"Missing: {expected_infras - actual}"


class TestDataIntegrity:
    def test_all_rows_have_required_fields(self):
        """Test that every row has all required fields."""
        required_fields = {
            "Infrastructure",
            "Asset",
            "Climate driver",
            "Type of impact",
            "Impact model",
            "Dictionary Key",
        }
        data = get_all_impact_data()

        for i, row in enumerate(data):
            missing = required_fields - set(row.keys())
            assert not missing, f"Row {i} missing fields: {missing}"

    def test_type_of_impact_valid(self):
        """Test that all Type of impact values are valid."""
        valid_types = {"Operations", "Maintenance", "Damages"}
        data = get_all_impact_data()

        for i, row in enumerate(data):
            assert row["Type of impact"] in valid_types, (
                f"Row {i}: Invalid type '{row['Type of impact']}'"
            )

    def test_consequences_derived(self):
        """Test that Consequences is correctly derived from Type of impact."""
        consequences_map = {
            "Operations": "Revenues loss",
            "Maintenance": "Increase OPEX",
            "Damages": "Increase CAPEX",
        }
        data = get_all_impact_data()

        for i, row in enumerate(data):
            expected = consequences_map.get(row["Type of impact"])
            actual = row.get("Consequences")
            assert actual == expected, (
                f"Row {i}: Expected Consequences='{expected}', got '{actual}'"
            )

    def test_infrastructure_matches_filename(self):
        """Test that Infrastructure matches the YAML file."""
        expected_infras = {
            "Bridges",
            "Dams",
            "green spaces",
            "Railway",
            "River training infrastructure",
            "Road",
            "Torrent control infrastructure",
            "Tunnels",
        }
        actual_infras = set(ALL_IMPACT_MODELS.keys())
        assert actual_infras == expected_infras

    def test_no_empty_impact_models(self):
        """Test that no Impact model is empty."""
        data = get_all_impact_data()

        for i, row in enumerate(data):
            assert row["Impact model"].strip(), f"Row {i}: Empty Impact model"


class TestHelpers:
    def test_get_impact_data_for_infrastructure(self):
        """Test the helper function."""
        road_data = get_impact_data_for_infrastructure("Road")
        assert len(road_data) > 0, "Road data should not be empty"

        # All rows should be Road
        for row in road_data:
            assert row["Infrastructure"] == "Road"

    def test_get_impact_data_for_unknown_returns_empty(self):
        """Test that unknown infrastructure returns empty list."""
        result = get_impact_data_for_infrastructure("Unknown Infrastructure")
        assert result == []


class TestYAMLKeys:
    """Test that YAML keys are correctly mapped."""

    def test_yaml_keys_are_snake_case(self):
        """Test that YAML keys follow snake_case convention."""
        expected_yaml_keys = {
            "infrastructure",
            "asset",
            "climate_driver",
            "type_of_impact",
            "impact_model",
            "recommended_climate_indicator",
            "dictionary_key",
            "used_climate_indicator",
            "possible_hazards",
        }

        for yaml_key in YAML_TO_ROW.keys():
            # Should be snake_case (lowercase with underscores)
            assert yaml_key.islower() or "_" in yaml_key, (
                f"Key '{yaml_key}' should be snake_case"
            )
            assert " " not in yaml_key, f"Key '{yaml_key}' should not contain spaces"
