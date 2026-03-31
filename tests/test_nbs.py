from modules.nbs import (
    NBS_CODES,
    HAZARD_CODES,
    NBS_MATRIX,
    NBS_MATRIX_SUPPORTIVE,
    NbS_list,
    get_nbs_name,
    get_hazard_name,
    get_nbs_for_hazard,
    get_hazard_codes,
    get_nbs_codes,
)


class TestNbSCodes:
    def test_nbs_codes_count(self):
        assert len(NBS_CODES) == 74

    def test_nbs_codes_are_unique(self):
        assert len(NBS_CODES) == len(set(NBS_CODES.values()))

    def test_nbs_codes_all_strings(self):
        for code, name in NBS_CODES.items():
            assert isinstance(code, str)
            assert isinstance(name, str)
            assert len(code) == 3
            assert len(name) > 0


class TestHazardCodes:
    def test_hazard_codes_count(self):
        assert len(HAZARD_CODES) == 18

    def test_hazard_codes_are_unique(self):
        assert len(HAZARD_CODES) == len(set(HAZARD_CODES.values()))

    def test_hazard_codes_all_strings(self):
        for code, name in HAZARD_CODES.items():
            assert isinstance(code, str)
            assert isinstance(name, str)
            assert len(code) == 3
            assert len(name) > 0


class TestNBSMatrix:
    def test_matrix_has_all_hazards(self):
        assert set(NBS_MATRIX.keys()) == set(HAZARD_CODES.keys())

    def test_matrix_supportive_has_all_hazards(self):
        assert set(NBS_MATRIX_SUPPORTIVE.keys()) == set(HAZARD_CODES.keys())

    def test_matrix_rows_are_lists(self):
        for haz_code, row in NBS_MATRIX.items():
            assert isinstance(row, list)
            for nbs_code in row:
                assert nbs_code in NBS_CODES

    def test_matrix_supportive_rows_are_lists(self):
        for haz_code, row in NBS_MATRIX_SUPPORTIVE.items():
            assert isinstance(row, list)
            for nbs_code in row:
                assert nbs_code in NBS_CODES

    def test_eht_heatwave_primary_solutions(self):
        eht_yes = get_nbs_for_hazard("EHT", "Yes")
        assert "Bio-retention cells" in eht_yes
        assert "Green roofs" in eht_yes
        assert "Water retention basins and ponds (storage ponds)" in eht_yes
        assert len(eht_yes) >= 10

    def test_wlf_wildfire_primary_solutions(self):
        wlf_yes = get_nbs_for_hazard("WLF", "Yes")
        assert "3D steel grids (vegetated)" in wlf_yes
        assert "Biodiverse hedgerows" in wlf_yes
        assert "Buffer vegetation strips and coppice management" in wlf_yes

    def test_get_nbs_for_hazard_supportive(self):
        eht_supp = get_nbs_for_hazard("EHT", "Supportive")
        assert "Brush mattress" in eht_supp
        assert len(eht_supp) >= 10


class TestLegacyCompatibility:
    def test_nbs_list_structure(self):
        assert isinstance(NbS_list, dict)
        assert len(NbS_list) == 18
        for hazard_data in NbS_list.values():
            assert "Yes" in hazard_data
            assert "Supportive" in hazard_data
            assert isinstance(hazard_data["Yes"], list)
            assert isinstance(hazard_data["Supportive"], list)

    def test_nbs_list_matches_matrix(self):
        for haz_code, haz_name in HAZARD_CODES.items():
            matrix_yes = set(get_nbs_for_hazard(haz_code, "Yes"))
            legacy_yes = set(NbS_list[haz_name]["Yes"])
            assert matrix_yes == legacy_yes, f"Mismatch for {haz_code}"

            matrix_supp = set(get_nbs_for_hazard(haz_code, "Supportive"))
            legacy_supp = set(NbS_list[haz_name]["Supportive"])
            assert matrix_supp == legacy_supp, f"Mismatch for {haz_code}"

    def test_nbs_list_hazard_names(self):
        expected_names = set(HAZARD_CODES.values())
        actual_names = set(NbS_list.keys())
        assert expected_names == actual_names


class TestHelperFunctions:
    def test_get_nbs_name(self):
        assert get_nbs_name("BRC") == "Bio-retention cells"
        assert get_nbs_name("GRF") == "Green roofs"
        assert get_nbs_name("XXX") == "XXX"

    def test_get_hazard_name(self):
        assert get_hazard_name("EHT") == "Extreme high temperatures (Heatwave)"
        assert get_hazard_name("WLF") == "Wildfire"
        assert get_hazard_name("XXX") == "XXX"

    def test_get_hazard_codes_all_present(self):
        codes = get_hazard_codes()
        assert len(codes) == 18
        assert "EHT" in codes
        assert "WLF" in codes

    def test_get_nbs_codes_all_present(self):
        codes = get_nbs_codes()
        assert len(codes) == 74
        assert "BRC" in codes
        assert "GRF" in codes
