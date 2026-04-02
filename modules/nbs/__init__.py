"""
Nature-Based Solutions (NbS) registry.

Maps climate hazards to applicable NbS methods.
"""

from modules.nbs.nbs_hazard_matrix import (
    NBS_CODES,
    HAZARD_CODES,
    NBS_MATRIX,
    NBS_MATRIX_SUPPORTIVE,
    get_nbs_name,
    get_hazard_name,
    get_nbs_for_hazard,
    get_hazard_codes,
    get_nbs_codes,
    get_legacy_dict,
)

NbS_list = get_legacy_dict()

__all__ = [
    "NBS_CODES",
    "HAZARD_CODES",
    "NBS_MATRIX",
    "NBS_MATRIX_SUPPORTIVE",
    "NbS_list",
    "get_nbs_name",
    "get_hazard_name",
    "get_nbs_for_hazard",
    "get_hazard_codes",
    "get_nbs_codes",
]
