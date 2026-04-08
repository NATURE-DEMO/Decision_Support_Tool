# ruff: noqa: E501
# fmt: off
"""
NbS-Hazard matrix data.

Maps climate hazards to applicable Nature-Based Solutions methods.
Corrected Version: Resolves transposition error, incorporates corrected 3-letter codes,
and fixes LFA typo.

References:
    Kuschel, E.; Obriejetan, M.; Kuzmanić, T.; et al. (2025).
    A Systematic Framework for Assessing the Temporally Variable Protective Capacity
    of Nature-Based Solutions Against Natural Hazards. *Infrastructures*, 10(12), 318.
    https://doi.org/10.3390/infrastructures10120318
"""

NBS_REFERENCE = "Kuschel et al. (2025), https://doi.org/10.3390/infrastructures10120318"

NBS_CODES = {
    "TER": "Terracing (slope shaping, reduction of slope inclination)",
    "EDB": "Earth dams and barriers (vegetated)",
    "AVM": "Avalanche mounds",
    "3DG": "3-D steel grids (vegetated)",
    "RSV": "Reinforced soil and earth packs (vegetated)",
    "AFF": "Afforestation and reforestation",
    "PFM": "Protection forest management",
    "RTF": "Retention forest",
    "WFM": "Wildfire-forest management",
    "BVS": "Buffer vegetation strips and coppice management",
    "FBS": "Firebreaks and firestrips",
    "FTS": "Fire-resistant tree species and plants",
    "PRB": "Prescribed burning",
    "RBZ": "Riparian buffer zones",
    "FLR": "Floodplain restoration",
    "MCP": "Meandering channel planform",
    "CHW": "Channel widening",
    "SIL": "Sills",
    "GRO": "Groynes (vegetated)",
    "VFD": "Vegetated flood protection dams, dikes and levees",
    "WRB": "Water retention basins and ponds (storage ponds)",
    "WCR": "Wetland conservation and restoration",
    "CWL": "Constructed wetlands",
    "LSL": "Living shorelines",
    "DRC": "Dune restoration and coastal vegetation",
    "SDS": "Sand dune stabilization",
    "SBR": "Seagrass bed restoration",
    "CRC": "Coral reef conservation and restoration",
    "SMR": "Salt marsh restoration",
    "LFS": "Litoral intertidal forests and shrublands",
    "AGF": "Agroforestry",
    "HTC": "Horticulture",
    "WRH": "Water retention, harvesting and cisterns",
    "MAR": "Managed aquifer recharge (MAR)",
    "GCR": "Green corridors and tree rows",
    "BDH": "Biodiverse hedgerows",
    "MGR": "Meadow and grassland restoration",
    "VBZ": "Vegetated buffer zones",
    "CRG": "Controlled grazing",
    "FSA": "Fire-smart agriculture",
    "CTR": "Contour trenching",
    "CNT": "Conservation tillage",
    "MLH": "Mulching",
    "CVC": "Cover cropping",
    "SAM": "Soil amendments",
    "HMS": "Hydro and mulch seeding",
    "VEM": "Vegetated biodegradeable erosion control meshes",
    "VMB": "Vegetated biodegradeable erosion control mats and blankets",
    "SOD": "Sod (turves)",
    "LST": "Live staking",
    "LFE": "Live fencing (for slope engineering)",
    "SLG": "Live slope grids or contour logs",
    "LLT": "Live layered techniques",
    "VCL": "Vegetated cribwall (layer-based design)",
    "VDS": "Vegetated drainage systems",
    "WAF": "Wattle fence (for water engineering)",
    "TRV": "Tree revetment (tree spurs)",
    "VRP": "Vegetated riprap",
    "RWD": "Root wad",
    "VCF": "Vegetated crib wall (fascine-based design)",
    "LFA": "Live fascines",
    "BMT": "Brush mattress",
    "LPW": "Live palisades and live weirs",
    "LSB": "Vegetated log/stone barriers and live/rock check dams",
    "WLF": "Wooden log fences",
    "OGS": "Open green spaces",
    "GRP": "Green pavers",
    "GRF": "Green roofs",
    "VGN": "Vertical greenery",
    "UBF": "Urban forests",
    "RNG": "Rain gardens",
    "BRC": "Bio-retention cells",
    "IFT": "Infiltration trenches",
    "BSW": "Bioswales",
}

HAZARD_CODES = {
    "EHT": "Extreme high temperatures (Heatwave)",
    "ECT": "Extreme cold temperatures (Coldwave, cold snap)",
    "DRT": "Drought",
    "WFR": "Wildfire",
    "DSF": "Desertification",
    "SSW": "Storms and strong winds",
    "HAL": "Hail",
    "AEO": "Aeolian erosion",
    "PFR": "Pluvial flood, heavy rainfall and surface runoff",
    "FVF": "Fluvial flood",
    "COF": "Coastal flood",
    "IFT": "Impact floods and tsunami",
    "FST": "Fluvial sediment transport",
    "SBE": "Stream bank and bed erosion",
    "SRE": "Sheet erosion and rill erosion",
    "GUE": "Gully erosion",
    "CSE": "Coastal and shoreline erosion",
    "DFH": "Debris flood (Vol. Sediment Conc. 20–40%)",
    "DFM": "Debris flow (Volumetric Sediment Concentration >40%)",
    "RFS": "Small Rockfall (Diameter <25cm)",
    "RFL": "Large Rockfall (Diameter >25-100 cm)",
    "LS1": "Landslides < 2 m depth",
    "LS2": "Landslides 2-10 m depth",
    "LS3": "Landslides > 10 m depths",
    "LS4": "Mud or Earth flow",
    "SDS": "Soil slope deformation & Soil creep",
    "AVA": "Snow avalanches",
    "SDR": "Snow drift",
    "SCS": "Snow creep & slide"
}

_RAW_MATRIX_DATA = """
TER	Terracing (slope shaping, reduction of slope inclination)	0	0	0	1	2	0	0	2	1	1	1	1	2	2	2	2	2	1	2	2	2	2	1	1	1	2	1	1	2
EDB	Earth dams and barriers (vegetated)	0	0	0	0	0	0	0	2	2	0	1	1	0	0	2	2	0	2	2	2	2	2	1	0	1	0	2	2	2
AVM	Avalanche mounds	0	0	0	0	0	0	0	0	0	0	0	0	1	1	1	1	1	1	2	2	2	2	1	0	2	2	2	2	2
3DG	3-D steel grids (vegetated)	0	0	0	0	0	0	0	2	0	0	0	0	2	2	2	2	2	1	1	1	2	2	1	0	2	2	0	0	0
RSV	Reinforced soil and earth packs (vegetated)	0	0	0	1	2	0	0	2	0	0	0	1	2	2	2	2	2	2	2	2	2	2	1	0	2	2	0	0	0
AFF	Afforestation and reforestation	2	1	2	2	2	1	2	2	2	2	0	1	1	2	2	2	2	2	2	2	1	2	1	1	2	2	2	2	2
PFM	Protection forest management	1	1	2	2	2	1	2	2	2	2	0	1	1	2	2	2	2	2	2	2	1	2	1	1	2	2	2	2	2
RTF	Retention forest	1	1	1	0	2	1	2	2	2	2	0	1	1	2	2	2	0	2	2	1	0	1	0	0	1	1	1	1	1
WFM	Wildfire-forest management 	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
BVS	Buffer vegetation strips and coppice management	0	0	1	2	1	1	0	2	1	1	0	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	1	1	1
FBS	Firebreaks and firestrips	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
FTS	Fire-resistant tree species and plants	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
PRB	Prescribed burning	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
RBZ	Riparian buffer zones 	1	0	1	0	1	1	0	1	1	2	0	0	2	2	0	0	0	1	1	0	0	0	0	0	0	0	1	1	1
FLR	Floodplain restoration	1	0	1	0	1	1	0	0	0	2	0	0	2	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
MCP	Meandering channel planform	1	0	1	0	1	0	0	0	0	2	0	0	2	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
CHW	Channel widening	0	0	1	1	1	0	0	0	0	2	0	0	2	2	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0
SIL	Sills	0	0	1	0	1	0	0	0	0	2	0	0	2	2	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0
GRO	Groynes (vegetated)	0	0	0	0	0	0	0	0	0	2	0	0	2	2	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0
VFD	Vegetated flood protection dams, dikes and levees 	0	0	0	0	0	0	0	0	2	2	2	0	2	2	0	0	1	2	2	0	0	0	0	0	0	0	0	0	0
WRB	Water retention basins and ponds (storage ponds)	1	0	1	2	1	0	0	0	2	2	0	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
WCR	Wetland conservation and restoration	1	0	2	1	1	0	0	0	2	2	1	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
CWL	Constructed wetlands 	1	0	1	1	1	0	0	0	2	2	1	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
LSL	Living shorelines	1	1	0	0	1	1	0	0	0	0	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0
DRC	Dune restoration and coastal vegetation 	0	0	0	0	1	0	0	0	0	0	2	1	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0
SDS	Sand dune stabilization	0	0	0	0	1	0	0	0	0	0	1	1	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0
SBR	Seagrass bed restoration 	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0
CRC	Coral reef conservation and restoration	0	0	0	0	0	0	0	0	0	0	1	0	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0
SMR	Salt marsh restoration 	1	0	0	0	0	0	0	0	1	1	1	0	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
LFS	Litoral intertidal forests and shrublands	1	1	0	0	1	1	0	0	0	0	2	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0
AGF	Agroforestry	1	1	1	0	2	2	1	2	2	2	0	0	1	1	2	1	0	1	1	0	0	1	0	0	1	1	0	1	1
HTC	Horticulture	1	1	2	0	2	1	0	2	1	1	0	0	1	1	2	0	0	1	1	0	0	1	0	0	1	1	0	1	1
WRH	Water retention, harvesting and cisterns 	0	0	2	0	2	0	0	0	1	1	0	0	2	0	2	0	0	1	0	0	0	0	0	0	0	0	0	0	0
MAR	Managed aquifer recharge (MAR)	0	0	2	0	2	0	0	0	1	1	0	0	0	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0
GCR	Green corridors and tree rows	1	1	1	0	2	1	0	2	1	1	0	0	2	1	2	0	1	1	1	0	0	1	0	0	1	1	0	2	0
BDH	Biodiverse hedgerows	1	1	1	0	2	1	0	2	1	1	0	0	1	1	1	1	1	1	1	0	0	1	0	0	1	1	0	2	0
MGR	Meadow and grassland restoration	1	1	1	0	2	1	0	2	2	2	0	0	1	1	1	1	0	1	1	0	0	1	0	0	1	1	0	1	1
VBZ	Vegetated buffer zones	1	1	1	0	2	1	0	2	2	2	0	0	2	2	2	1	2	1	1	0	0	1	0	0	1	1	0	2	2
CRG	Controlled grazing 	0	0	0	2	2	0	0	1	1	1	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0
FSA	Fire-smart agriculture	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
CTR	Contour trenching 	0	0	1	1	2	0	0	0	2	2	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0
CNT	Conservation tillage	0	0	1	0	2	0	0	1	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0
MLH	Mulching 	0	0	1	0	2	0	0	1	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0
CVC	Cover cropping	0	0	1	0	2	0	0	1	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0
SAM	Soil amendments	0	0	1	0	2	0	0	1	1	1	0	0	0	0	2	0	0	0	0	0	0	0	0	0	0	0	0	0	0
HMS	Hydro and mulch seeding 	0	0	0	0	2	0	1	2	1	1	1	0	1	2	2	2	2	1	0	2	0	2	1	0	1	1	0	0	0
VEM	Vegetated biodegradeable erosion control meshes	0	0	2	0	2	0	1	2	1	1	1	0	1	2	2	2	2	1	1	2	0	2	1	0	1	1	0	0	0
VMB	Vegetated biodegradeable erosion control mats and blankets	0	0	2	0	2	0	1	2	1	1	1	0	1	2	2	2	2	1	1	2	0	2	1	0	1	1	0	0	0
SOD	Sod (turves)	0	0	2	0	1	0	1	2	1	1	0	0	0	0	2	0	0	1	0	0	0	0	0	0	0	0	0	0	0
LST	Live staking	0	0	1	0	1	0	1	2	2	2	2	0	1	2	2	2	2	1	2	2	1	2	1	0	1	1	0	1	0
LFE	Live fencing (for slope engineering)	0	0	0	0	0	2	1	2	1	1	1	0	1	2	2	2	2	1	2	2	1	2	1	0	1	1	0	2	2
SLG	Live slope grids or contour logs	0	0	1	0	1	0	1	2	1	1	1	0	0	0	2	2	0	1	2	2	1	2	1	0	1	1	0	0	0
LLT	Live layered techniques	0	0	0	0	0	0	1	2	1	1	1	0	0	0	1	1	0	1	2	2	1	2	1	0	2	2	0	0	0
VCL	Vegetated cribwall (layer-based design)	0	0	1	0	1	1	1	2	1	1	0	0	1	0	1	1	2	1	2	1	1	2	1	0	2	2	1	2	2
VDS	Vegetated drainage systems 	0	0	1	0	1	0	1	1	2	2	0	0	0	0	2	2	0	1	2	0	0	2	2	2	2	2	0	0	0
WAF	Wattle fence (for water engineering)	0	0	0	0	0	0	1	1	2	2	2	0	1	2	2	1	2	1	0	0	0	0	0	0	0	0	0	0	0
TRV	Tree revetment (tree spurs)	0	0	0	0	0	0	1	1	1	1	0	0	1	2	2	2	2	1	0	0	0	0	0	0	0	0	0	0	0
VRP	Vegetated riprap 	0	0	0	0	0	0	1	2	2	2	0	0	1	2	2	2	2	1	2	2	1	2	0	0	1	1	0	0	0
RWD	Root wad	0	0	0	0	0	0	1	1	1	1	0	0	1	2	2	2	0	1	0	0	0	0	0	0	0	0	0	0	0
VCF	Vegetated crib wall (fascine-based design)	0	0	0	0	0	1	1	2	2	2	0	0	2	2	0	0	2	1	2	0	0	0	0	0	0	0	1	2	2
LFA	Live fascines	0	0	1	0	1	0	1	2	2	2	0	0	1	2	2	2	2	1	1	0	0	0	0	0	0	0	0	0	0
BMT	Brush mattress	0	0	1	0	1	0	1	2	2	2	0	0	1	2	2	2	2	1	1	0	0	0	0	0	0	0	0	0	0
LPW	Live palisades and live weirs	0	0	0	0	0	1	1	2	2	2	0	0	1	2	2	2	2	1	1	0	0	0	0	0	0	0	0	0	0
LSB	Vegetated log/stone barriers and live/rock check dams 	0	0	0	0	0	0	1	1	2	2	0	0	2	2	0	2	0	1	2	0	0	0	0	0	0	0	1	0	0
WLF	Wooden log fences	0	0	0	0	0	1	1	1	1	1	0	0	2	2	2	2	0	1	1	2	1	0	0	0	0	0	0	2	2
OGS	Open green spaces	2	0	1	0	1	0	0	0	2	2	0	0	0	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0
GRP	Green pavers	2	0	1	0	1	0	0	0	2	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
GRF	Green roofs	2	1	1	0	1	0	1	0	2	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
VGN	Vertical greenery	2	1	1	0	1	0	0	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
UBF	Urban forests 	2	1	1	0	1	0	0	0	2	2	0	0	1	1	0	0	0	1	1	1	0	1	0	0	1	1	0	0	0
RNG	Rain gardens	1	0	1	0	1	0	0	0	1	1	0	0	0	0	0	0	0	1	0	0	0	0	0	0	0	0	0	0	0
BRC	Bio-retention cells	1	0	1	0	1	0	0	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
IFT	Infiltration trenches	0	0	1	0	1	0	0	0	2	1	0	0	1	1	1	0	0	1	0	0	0	0	0	0	0	0	0	0	0
BSW	Bioswales 	1	0	1	0	0	0	0	0	1	2	0	0	1	1	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
"""

NBS_MATRIX = {h: [] for h in HAZARD_CODES.keys()}
NBS_MATRIX_SUPPORTIVE = {h: [] for h in HAZARD_CODES.keys()}

def _build_matrices():
    """Parses the raw verified matrix data safely into final dictionaries."""
    hazards_ordered = list(HAZARD_CODES.keys())
    for line in _RAW_MATRIX_DATA.strip().split('\n'):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split('\t')]
        if len(parts) < 31: 
            continue
        
        nbs_code = parts[0]
        scores = parts[2:31]
        
        for i, score in enumerate(scores):
            if i >= len(hazards_ordered):
                break
            hazard_code = hazards_ordered[i]
            if score == '2':
                NBS_MATRIX[hazard_code].append(nbs_code)
            elif score == '1':
                NBS_MATRIX_SUPPORTIVE[hazard_code].append(nbs_code)

_build_matrices()
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
