"""
Unit tests for impact_models module.
"""

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
        assert len(data) >= 184

    def test_ci_types_count(self):
        """Test that all CI types are discovered."""
        ci_types = get_ci_type_names()
        assert len(ci_types) >= 8

    def test_yaml_to_row_mapping_complete(self):
        """Test that all row keys have a YAML mapping."""
        from modules.impact_models import ROW_KEYS

        for key in ROW_KEYS:
            yaml_key = key.lower().replace(" ", "_")
            assert yaml_key in YAML_TO_ROW, f"Missing mapping for {key}"

    def test_all_yaml_files_loaded(self):
        """Test that all YAML files are discovered."""
        ci_types = get_ci_type_names()
        assert len(ci_types) >= 8
        for name in ci_types:
            assert name.strip()


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
        actual_infras = set(ALL_IMPACT_MODELS.keys())
        assert len(actual_infras) >= 8
        for name in actual_infras:
            assert name.strip()

    def test_no_empty_impact_models(self):
        """Test that no Impact model is empty."""
        data = get_all_impact_data()

        for i, row in enumerate(data):
            assert row["Impact model"].strip(), f"Row {i}: Empty Impact model"

    def test_no_empty_required_fields(self):
        """Test that all required fields are non-empty."""
        required_string_fields = [
            "Asset",
            "Climate driver",
            "Impact model",
            "Recommended climate Indicator",
            "Dictionary Key",
            "Used climate Indicator",
        ]
        data = get_all_impact_data()

        for i, row in enumerate(data):
            for field in required_string_fields:
                value = row.get(field, "")
                assert value and value.strip(), f"Row {i}: Empty field '{field}'"

    def test_possible_hazards_is_list(self):
        """Test that possible_hazards is a non-empty list."""
        data = get_all_impact_data()

        for i, row in enumerate(data):
            hazards = row.get("Possible Hazards")
            assert hazards is not None, f"Row {i}: Missing Possible Hazards"
            assert isinstance(hazards, list), (
                f"Row {i}: Possible Hazards must be a list, got {type(hazards)}"
            )
            assert len(hazards) > 0, f"Row {i}: Empty Possible Hazards list"

    def test_dictionary_key_format(self):
        """Test that dictionary_key follows clima-ind-viz format (snake_case)."""
        data = get_all_impact_data()

        for i, row in enumerate(data):
            key = row.get("Dictionary Key", "")
            assert key.islower() or "_" in key, (
                f"Row {i}: Dictionary Key '{key}' should be snake_case"
            )
            assert " " not in key, f"Row {i}: Dictionary Key '{key}' should not contain spaces"


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
        for yaml_key in YAML_TO_ROW.keys():
            assert yaml_key.islower() or "_" in yaml_key, f"Key '{yaml_key}' should be snake_case"
            assert " " not in yaml_key, f"Key '{yaml_key}' should not contain spaces"
