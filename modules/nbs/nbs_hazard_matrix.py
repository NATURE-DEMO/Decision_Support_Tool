# ruff: noqa: E501
# fmt: off
"""
NbS-Hazard matrix data.

Maps climate hazards to applicable Nature-Based Solutions methods.
"""

NBS_CODES = {
    "3DS": "3D steel grids (vegetated)",
    "AFR": "Afforestation and reforestation",
    "AGR": "Agroforestry",
    "AVM": "Avalanche mounds",
    "BRC": "Bio-retention cells",
    "BDH": "Biodiverse hedgerows",
    "BSW": "Bioswales",
    "BRM": "Brush mattress",
    "BVS": "Buffer vegetation strips and coppice management",
    "CHW": "Channel widening",
    "CTI": "Conservation tillage",
    "CWT": "Constructed wetlands",
    "CTR": "Contour trenching",
    "CGR": "Controlled grazing",
    "CRC": "Coral reef conservation and restoration",
    "CVC": "Cover cropping",
    "DRC": "Dune restoration and coastal vegetation",
    "EDB": "Earth dams and barriers (vegetated)",
    "FRT": "Fire-resistant tree species and plants",
    "FSA": "Fire-smart agriculture",
    "FBF": "Firebreaks and firestrips",
    "FPR": "Floodplain restoration",
    "GCR": "Green corridors and tree rows",
    "GPV": "Green pavers",
    "GRF": "Green roofs",
    "GRV": "Groynes (vegetated)",
    "HOR": "Horticulture",
    "HMS": "Hydro and mulch seeding",
    "IFT": "Infiltration trenches",
    "LFS": "Littoral/intertidal forests and shrublands",
    "LFC": "Live fascines",
    "LFE": "Live fencing (for slope engineering)",
    "LLT": "Live layered techniques",
    "LPW": "Live palisades and live weirs",
    "LSG": "Live slope grids or contour logs",
    "LSK": "Live staking",
    "LVS": "Living shorelines",
    "MAR": "Managed aquifer recharge",
    "MGR": "Meadow and grassland restoration",
    "MCP": "Meandering channel planform",
    "MUL": "Mulching",
    "OPG": "Open green spaces",
    "PRB": "Prescribed burning",
    "PFM": "Protection forest management",
    "RGN": "Rain gardens",
    "RSP": "Reinforced soil and earth packs (vegetated)",
    "RTR": "Retention forest",
    "RBZ": "Riparian buffer zones",
    "RWD": "Root wad",
    "SMR": "Salt marsh restoration",
    "SDS": "Sand dune stabilisation",
    "SGR": "Seagrass bed restoration",
    "SLL": "Sills",
    "SDT": "Sod (turves)",
    "SAM": "Soil amendments",
    "TER": "Terracing (slope shaping, reduction of slope inclination)",
    "TRV": "Tree revetment (tree spurs)",
    "URF": "Urban forests",
    "VBM": "Vegetated biodegradable erosion control mats and blankets",
    "VME": "Vegetated biodegradable erosion control meshes",
    "VBZ": "Vegetated buffer zones",
    "VCF": "Vegetated cribwall (fascine-based design)",
    "VCL": "Vegetated cribwall (layer-based design)",
    "VDS": "Vegetated drainage systems",
    "VFD": "Vegetated flood protection dams, dikes and levees",
    "VLB": "Vegetated log/stone barriers and live/rock check dams",
    "VRP": "Vegetated riprap",
    "VGR": "Vertical greenery",
    "WRB": "Water retention basins and ponds (storage ponds)",
    "WRC": "Water retention, harvesting and cisterns",
    "WTF": "Wattle fence (for water engineering)",
    "WCR": "Wetland conservation and restoration",
    "WFM": "Wildfire-forest management",
    "WLF": "Wooden log fences",
}

HAZARD_CODES = {
    "EHT": "Extreme high temperatures (Heatwave)",
    "ECT": "Extreme cold temperatures (Coldwave, cold snap)",
    "DRT": "Drought",
    "WLF": "Wildfire",
    "DZT": "Desertification",
    "SSW": "Storms and strong winds",
    "HAI": "Hail",
    "AEO": "Aeolian erosion",
    "PLF": "Pluvial flood, heavy rainfall and surface runoff",
    "FLF": "Fluvial flood",
    "COF": "Coastal flood",
    "IFT": "Impact floods and tsunami",
    "FST": "Fluvial sediment transport",
    "SBE": "Stream bank and bed erosion",
    "SER": "Sheet erosion and rill erosion",
    "GUL": "Gully erosion",
    "CSE": "Coastal and shoreline erosion",
    "DFL": "Debris flood (Vol. Sediment Conc. 20–40%)",
}

NBS_MATRIX = {
    "EHT": ["BRC", "BSW", "GPV", "GRF", "IFT", "LVS", "MAR", "VLB", "VRP", "VGR", "WRB", "WRC"],
    "ECT": ["BRC", "BSW", "GPV", "GRF", "LFS", "LFC", "LFE", "LSG", "LSK", "LVS", "MAR", "VGR", "WRB", "WRC"],
    "DRT": ["BRC", "BSW", "FPR", "GCR", "LFE", "LLT", "LPW", "MAR", "RTR", "RBZ", "RWD", "SAM", "WRB", "WRC"],
    "WLF": ["3DS", "BDH", "BRC", "BSW", "BVS", "CHW", "CTI", "CWT", "CTR", "FRT", "FSA", "FPR", "GCR", "GRF", "GRV", "MGR", "MCP", "RSP", "SDS"],
    "DZT": ["3DS", "BDH", "BRC", "BSW", "BRM", "LFC", "LFE", "LLT", "LPW", "LSG", "LSK", "LVS", "MAR", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "RTR", "RBZ", "SAM"],
    "SSW": ["BRC", "BSW", "BRM", "CGR", "CRC", "GPV", "LVS", "MAR", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VME"],
    "HAI": ["BRC", "BSW", "BRM", "RSP", "RTR", "RBZ", "RWD", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "URF", "VME", "VCL"],
    "AEO": ["3DS", "AFR", "AGR", "AVM", "BDH", "BRC", "BSW", "BRM", "CHW", "FRT", "LFC", "LFE", "LSG", "LSK", "MAR", "MGR", "OPG", "PRB", "PFM", "RGN", "RSP", "RTR", "RBZ", "RWD", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VBM", "VME", "VBZ", "VCF", "VCL"],
    "PLF": ["3DS", "AFR", "BRC", "BSW", "BRM", "CRC", "CVC", "DRC", "EDB", "FRT", "FSA", "FPR", "GCR", "IFT", "MAR", "MUL", "RSP", "RTR", "RBZ", "SMR", "SAM", "TER", "URF", "VLB", "VRP", "VGR", "WRB", "WRC", "WFM"],
    "FLF": ["3DS", "BRC", "BSW", "BRM", "CGR", "FRT", "FSA", "FPR", "GCR", "GRF", "GRV", "HOR", "HMS", "IFT", "LFS", "LVS", "MAR", "MUL", "RSP", "RTR", "RBZ", "SMR", "SAM", "TER", "URF", "VCL", "VLB", "VRP", "VGR", "WRB", "WRC", "WFM", "WLF"],
    "COF": ["3DS", "AFR", "CRC", "CVC", "DRC", "EDB", "GCR", "GPV", "GRF", "GRV", "LFS", "LFC", "LVS", "MAR", "SMR", "SDS", "SGR", "SLL", "SDT", "URF", "VBM", "VME"],
    "IFT": ["3DS", "BDH", "BRC", "BSW", "BRM", "CRC", "CVC", "DRC", "EDB", "FBF", "FSA", "IFT", "LFC", "MAR", "RSP", "RTR", "RBZ", "SDS", "SDT", "SAM", "TER", "TRV", "URF", "VBM", "VME"],
    "FST": ["3DS", "AVM", "BDH", "BRC", "BSW", "BRM", "BVS", "CGR", "FBF", "FRT", "FSA", "FPR", "GCR", "LFC", "LFE", "LLT", "LSG", "LSK", "LVS", "MAR", "RSP", "RTR", "RBZ", "RWD", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VBM", "VDS", "VFD", "WRB", "WRC", "WFM", "WLF"],
    "SBE": ["3DS", "AVM", "BDH", "BRC", "BSW", "BRM", "CGR", "FRT", "FPR", "GCR", "GPV", "GRF", "LFC", "LFE", "LSG", "LSK", "LVS", "MAR", "MUL", "OPG", "PRB", "PFM", "RGN", "RSP", "RTR", "RBZ", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VBM", "VME", "VBZ", "VCF", "VCL", "VDS", "VFD", "WRB", "WRC", "WFM", "WLF"],
    "SER": ["3DS", "AFR", "AVM", "BDH", "BRC", "BSW", "BRM", "CGR", "CRC", "CVC", "DRC", "EDB", "FRT", "FPR", "GCR", "GRF", "GRV", "LFC", "LFE", "LLT", "LPW", "LSG", "LSK", "LVS", "MAR", "MUL", "RSP", "RTR", "RBZ", "SMR", "SDS", "SGR", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VBM", "VME", "VBZ", "VCF", "VCL", "VDS", "VFD", "WRB", "WRC", "WFM", "WLF"],
    "GUL": ["3DS", "AFR", "AVM", "BDH", "BRC", "BSW", "BRM", "CGR", "CRC", "CVC", "DRC", "EDB", "FRT", "FPR", "GCR", "LFC", "LFE", "LLT", "LSG", "LSK", "LVS", "MAR", "RSP", "RTR", "RBZ", "RWD", "SMR", "SDS", "SLL", "SDT", "SAM", "TER", "TRV", "URF", "VBZ", "VCF", "VCL", "VFD", "WRB", "WRC", "WFM", "WLF"],
    "CSE": ["3DS", "AVM", "BDH", "BRC", "BSW", "CGR", "FRT", "GCR", "GRF", "GRV", "LFC", "LFE", "LSG", "LSK", "LVS", "MAR", "RSP", "RTR", "RBZ", "SMR", "SDS", "SLL", "SDT", "SAM", "URF", "VME", "VBZ", "VCF", "VCL", "VFD"],
    "DFL": ["3DS", "AFR", "AGR", "BDH", "BRC", "BSW", "BRM", "CHW", "CGR", "FRT", "LFC", "LFE", "LSG", "LSK", "LVS", "MAR", "RBZ", "RSP", "SMR", "SDS", "SLL", "SDT", "SAM", "URF", "VBM", "VBZ", "VCF", "VCL", "VDS", "VFD", "VLB", "VRP", "VGR", "WRB", "WRC", "WTF", "WCR", "WFM"],
}

NBS_MATRIX_SUPPORTIVE = {
    "EHT": ["BRM", "CGR", "CRC", "CVC", "DRC", "EDB", "FSA", "FPR", "GCR", "LFS", "LSG", "LSK", "SMR", "SDS", "SGR", "SDT", "SAM", "URF", "WTF", "WCR", "WLF"],
    "ECT": ["AGR", "BRM", "CRC", "CVC", "DRC", "FSA", "FPR", "GCR", "SMR", "SDS", "SGR", "SDT", "SAM", "URF", "WTF", "WCR", "WLF"],
    "DRT": ["3DS", "AFR", "AGR", "AVM", "BDH", "BRM", "CHW", "CGR", "CRC", "CVC", "DRC", "EDB", "FSA", "GPV", "LFC", "LSG", "LSK", "LVS", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "SAM", "SMR", "SDS", "SGR", "SDT", "TER", "TRV", "URF", "VBM", "VME", "VBZ", "VCF", "VFD", "WTF", "WCR", "WFM", "WLF"],
    "WLF": ["AFR", "AGR", "AVM", "BRM", "CGR", "DRC", "FBF", "LFC", "LSG", "LSK", "LVS", "MAR", "MUL", "OPG", "PRB", "PFM", "RGN", "RTR", "RBZ", "SMR", "SGR", "SDT", "SAM", "VFD"],
    "DZT": ["AFR", "AGR", "AVM", "CGR", "CRC", "CVC", "DRC", "EDB", "FSA", "FPR", "GCR", "GPV", "GRF", "LFS", "SMR", "SDS", "SGR", "SDT", "TER", "TRV", "URF", "WRB", "WRC", "WTF", "WCR", "WFM", "WLF"],
    "SSW": ["3DS", "AFR", "AGR", "AVM", "CHW", "FRT", "GCR", "GRF", "GRV", "LFC", "LFE", "LSG", "LSK", "RSP", "RTR", "RBZ", "RWD", "VBM", "VCL", "VDS", "VFD"],
    "HAI": ["3DS", "AVM", "FRT", "LFC", "LFE", "LSG", "LSK", "LVS", "MAR", "TER", "TRV", "VBM", "VBZ", "VCF", "VDS", "VFD"],
    "AEO": ["CGR", "CRC", "CVC", "DRC", "EDB", "FBF", "FSA", "FPR", "GCR", "GRV", "LFS", "LFE", "LVS", "VDS", "VFD"],
    "PLF": ["AGR", "AVM", "CHW", "CGR", "GPV", "GRF", "GRV", "HOR", "HMS", "LFS", "LFC", "LFE", "LLT", "LPW", "LSG", "LSK", "LVS", "MGR", "OPG", "PRB", "PFM", "RGN", "SDS", "SGR", "SDT", "TRV", "VBM", "VBZ", "VCF", "VCL", "VDS", "VFD", "WTF", "WCR", "WLF"],
    "FLF": ["AFR", "AGR", "AVM", "CHW", "GPV", "LFC", "LFE", "LLT", "LPW", "LSG", "LSK", "MGR", "OPG", "PRB", "PFM", "RGN", "SDS", "SGR", "SDT", "VBM", "VBZ", "VCF", "VDS", "VFD", "WTF", "WCR"],
    "COF": ["AGR", "AVM", "BRC", "BSW", "BRM", "FPR", "LFE", "LSG", "LSK", "MGR", "RSP", "RTR", "RBZ", "RWD", "SAM", "VBZ", "VCF", "VCL", "VFD"],
    "IFT": ["AFR", "AGR", "AVM", "CHW", "CGR", "FPR", "GCR", "GRF", "LFE", "LSG", "LSK", "LVS", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "SMR", "SGR", "SLL", "SAM", "VBZ", "VCF", "VCL", "VDS", "VFD", "WRB", "WRC", "WTF", "WCR", "WFM", "WLF"],
    "FST": ["AFR", "AGR", "CHW", "GRF", "GRV", "LFS", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "VBZ", "VCF", "VCL"],
    "SBE": ["AFR", "AGR", "CHW", "CRC", "CVC", "DRC", "EDB", "FSA", "GRV", "HOR", "HMS", "IFT", "LFS", "LLT", "LPW", "MCP", "MUL", "OPG", "RWD", "VLB", "VRP", "VGR"],
    "SER": ["AGR", "CHW", "GPV", "LFS", "MGR", "OPG", "PRB", "PFM", "RGN"],
    "GUL": ["AGR", "CHW", "FBF", "GPV", "GRF", "GRV", "LFS", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "SGR", "VBM", "VME", "VDS"],
    "CSE": ["AFR", "AGR", "BRM", "CRC", "CVC", "DRC", "EDB", "FSA", "FPR", "GPV", "LFS", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "SGR", "VDS", "WRB", "WRC", "WTF", "WCR", "WFM", "WLF"],
    "DFL": ["AVM", "CRC", "CVC", "DRC", "EDB", "FBF", "FSA", "FPR", "GCR", "GRF", "GRV", "LFS", "LLT", "LPW", "MGR", "MUL", "OPG", "PRB", "PFM", "RGN", "RTR", "SGR", "TER", "TRV"],
}
# fmt: on


def get_nbs_name(code: str) -> str:
    """Return full NbS name from code."""
    return NBS_CODES.get(code, code)


def get_hazard_name(code: str) -> str:
    """Return full hazard name from code."""
    return HAZARD_CODES.get(code, code)


def get_nbs_for_hazard(hazard_code: str, category: str = "Yes") -> list[str]:
    """Return NbS method names for a given hazard code and category."""
    if category == "Yes":
        matrix = NBS_MATRIX
    else:
        matrix = NBS_MATRIX_SUPPORTIVE
    codes = matrix.get(hazard_code, [])
    return [get_nbs_name(code) for code in codes]


def get_hazard_codes() -> list[str]:
    """Return list of all hazard codes."""
    return list(NBS_MATRIX.keys())


def get_nbs_codes() -> list[str]:
    """Return list of all NbS codes."""
    return list(NBS_CODES.keys())


def get_legacy_dict() -> dict:
    """Build backwards-compatible NbS_list dict from matrices."""
    result = {}
    for haz_code, haz_name in HAZARD_CODES.items():
        result[haz_name] = {
            "Yes": [NBS_CODES[c] for c in NBS_MATRIX.get(haz_code, [])],
            "Supportive": [NBS_CODES[c] for c in NBS_MATRIX_SUPPORTIVE.get(haz_code, [])],
        }
    return result
