import streamlit as st
import requests
import folium
import folium.plugins
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pandas as pd
import json
import re
import time
import os
from google import genai
from google.genai.errors import APIError
import numpy as np
import io
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import contextily as cx
import traceback
import plotly.graph_objects as go
import plotly.express as px
import streamlit_antd_components as sac

KOPPEN_COLORS = np.array([
    [0, 0, 255], [0, 120, 255], [70, 170, 250], [255, 0, 0], [255, 150, 150],
    [245, 165, 0], [255, 220, 100], [255, 255, 0], [200, 200, 0], [150, 150, 0],
    [150, 255, 150], [100, 200, 100], [
        50, 150, 50], [200, 255, 80], [100, 255, 80],
    [50, 200, 0], [255, 0, 255], [200, 0, 200], [150, 50, 150], [150, 100, 150],
    [170, 175, 255], [90, 120, 220], [75, 80, 180], [50, 0, 135], [0, 255, 255],
    [55, 200, 255], [0, 125, 125], [0, 70, 95], [178, 178, 178], [102, 102, 102]
]) / 255.0

KOPPEN_CLASSES = {
    1: "Af", 2: "Am", 3: "Aw", 4: "BWh", 5: "BWk", 6: "BSh", 7: "BSk",
    8: "Csa", 9: "Csb", 10: "Csc", 11: "Cwa", 12: "Cwb", 13: "Cwc",
    14: "Cfa", 15: "Cfb", 16: "Cfc", 17: "Dsa", 18: "Dsb", 19: "Dsc",
    20: "Dsd", 21: "Dwa", 22: "Dwb", 23: "Dwc", 24: "Dwd", 25: "Dfa",
    26: "Dfb", 27: "Dfc", 28: "Dfd", 29: "ET", 30: "EF"
}

KOPPEN_TIFF_URL = "https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/Koppen/1991-2020/koppen_geiger_0p1.tif"

infra_options = {
    "Buildings": ['["building"]'], "Roads": ['["highway"]'], "Railways": ['["railway"]'],
    "Water": ['["water"]', '["waterway"]'], "Power": ['["power"]'], "Landuse": ['["landuse"]'],
    "Man-made Structures": ['["man_made"]'], "Barriers": ['["barrier"]'], "Natural Features": ['["natural"]'],
    "Amenities": ['["amenity"]'], "Leisure": ['["leisure"]'], "Dams & Waterworks": ['["waterway"="dam"]'],
}

kpis = [
    "Safety, Reliability and Security (SRS)",
    "Availability and Maintainability (AM)",
    "Economy (EC)",
    "Environment (EV)",
    "Health and Politics (HP)"
]
scenarios = {
    "CI": "Current condition of the critical infrastructure",
    "CI_H": "Condition after natural hazard (H)",
    "CI_HG": "Condition after hazard but protected by grey measures (HG)",
    "CI_HN": "Condition after hazard but protected by nature-based solutions (HN)",
    "CI_HNG": "Condition after hazard but protected by both grey and nature-based solutions (HNG)"
}


EXAMPLE_HAZARD_TABLE = """
| Infrastructure | Climate driver | Impact model | Hazard Index | Hazard Level |
| :--- | :--- | :--- | :--- | :--- |
| Railway | Heat wave | Track buckling and equipment failure due to extreme heat | 5 | Extreme |
| Railway | Droughts | Soil desiccation affecting embankment stability | 5 | Extreme |
| Railway | Water stress | Reduced water availability for maintenance and cleaning | 4 | Very High |
| Railway | Changing temperature (Chronic) | Thermal expansion of rail components over time | 2 | Medium |
| Railway | Heavy precipitation | Flash flooding affecting track drainage systems | 1 | Low |
| Railway | Landslide | Slope instability triggered by saturation | 2 | Medium |
| Railway | Changing wind patterns | Crosswinds affecting train stability | 0 | No variation |
"""

EXAMPLE_HAZARD_REPORT = """
It can be concluded that droughts and heat waves constitute the most critical climate hazards for the analyzed railway line, consistently registering EXTREME hazard index scores (Hazard Index: 5). This underscores their high likelihood and severity, reflecting the growing influence of temperature-related acute events on the structural and operational integrity of the infrastructure.

In addition, water stress emerges as a significant chronic hazard, with VERY HIGH hazard levels (Index: 4). This indicates potential challenges in water availability for maintenance operations, ecological balance, and indirect effects such as soil desiccation and vegetation loss on embankments.

Conversely, chronic temperature changes, such as mean annual temperature rise, register MEDIUM scores (Index: 2). While their direct impacts may be moderate, they may act cumulatively or serve as enabling conditions for more severe events (e.g., prolonged high temperatures amplifying drought effects).

Precipitation-related hazards, including heavy rainfall, present LOW hazard levels (Index: 1). Notably, there is no significant variation projected in mean annual rainfall, which suggests limited change in total precipitation but potential shifts in intensity. This may still pose operational risks if drainage systems are overwhelmed.

Landslides, classified as acute and linked to precipitation, show MEDIUM scores (Index: 2). Despite their moderate hazard classification, their localized impact potential is high, especially in mountainous terrain with critical slope infrastructure.

Finally, wind-related hazards are generally assessed as showing NO VARIATION (Index: 0). Although currently not prioritized, these hazards should be monitored as part of a comprehensive risk strategy.

In summary, while droughts, heat waves, and water stress represent the most immediate and severe threats, the analysis highlights the importance of considering the full spectrum of hazards, including those with medium or low scores, as their risk contribution is ultimately shaped by the exposure and vulnerability profile of the infrastructure.
"""
EXAMPLE_PRI_TABLE = """
| Infrastructure | Climate driver | Impact model | Hazard Index | Exposure Index | Vulnerability Index | PRI scores |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Railway | Heavy precipitation | Reactive CAPEX due to damages associated to heavy rains | 2 | 4 | 4 | 2 |
| Railway | Storm (winds) | Reactive CAPEX due to damages associated to strong winds | 1 | 4 | 3 | 1 |
| Railway | Landslides | Reactive CAPEX due to damages associated to landslides | 2 | 4 | 5 | 2 |
| Railway | Changing precipitation | Increased maintenance due to increase in precipitation | 0 | 4 | 3 | 0 |
| Railway | Temperature variability | Increased maintenance due to temperature increase | 1 | 4 | 3 | 1 |
| Railway | Heavy precipitation | Stop of operations due to heavy rain | 2 | 4 | 3 | 1 |
"""

EXAMPLE_PRI_REPORT = """
**Potential Risk Index (PRI) Assessment Report**

The analysis integrates the Hazard Index (HI), Exposure Index (EI), and Vulnerability Index (VI) to compute the Potential Risk Index (PRI) for the analyzed infrastructure assets.

**High and Moderate Risks (PRI 2)**
The results indicate that the highest computed risk levels (PRI = 2) are driven by **Heavy Precipitation** and **Landslides**. 
* **Drivers:** These risks are characterized by a moderate Hazard Index (HI: 2) combined with high Exposure (EI: 4) and high Vulnerability (VI: 4-5).
* **Consequences:** The impacts include reactive CAPEX due to structural damages and potential operational stoppages. The high vulnerability scores suggest that the asset's adaptive capacity regarding geotechnical stability and drainage is currently insufficient for these specific hazards.

**Low Risks (PRI 1)**
**Temperature variability** and **Storms (winds)** present a low risk (PRI = 1). While the Exposure is high (EI: 4), the Hazard Index is low (HI: 1), limiting the overall risk score. However, these should still be monitored as climate change may intensify these drivers over longer time horizons.

**No Risk (PRI 0)**
Impacts related to general **Changing precipitation patterns** (chronic changes) registered a PRI of 0. This is primarily due to a Hazard Index of 0, indicating no significant variation projected for the mean values in the selected scenario, despite the high exposure of the asset.

**Conclusion**
Overall, the asset shows a sensitivity to acute hydrometeorological events (landslides, heavy rain) rather than chronic climate shifts. Adaptation strategies should prioritize drainage improvements and slope stabilization to reduce the Vulnerability Index, which is the primary driver amplifying the risk in this scenario.
"""
road_data = [
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to heavy rain', 'Preliminary climate Indicator': '25-year return period for maximum 1-day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Storms & strong winds']},
    {'Infrastructure': 'Road', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of the drainage system due to increase in heavy precipitation', 'Preliminary climate Indicator': '25-year return period for maximum 1-day precipitation (P25)', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Road', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Upgrading of the drainage system due to increase in heavy rain', 'Preliminary climate Indicator': '25-year return period for maximum 1-day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to heavy rain', 'Preliminary climate Indicator': '25-year return period for maximum 1-day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Road', 'Asset': 'Road Structure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the road infrastructure caused by flash floods.', 'Preliminary climate Indicator': '25-year return period for maximum 1-day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased pavement maintenance due to increase in precipitation', 'Preliminary climate Indicator': 'Monthly mean precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Road', 'Asset': 'Slopes and Embankments', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of slopes due to increase in precipitation', 'Preliminary climate Indicator': 'Substantial relative increase in annual precipitation\nRelative change in annual precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Soil slope deformation & Soil creep', 'Landslides < 2 m depth', 'Sheet erosion & rill erosion']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to increase in precipitation', 'Preliminary climate Indicator': 'Substantial relative increase in annual precipitation\nRelative change in annual precipitation', 'Proposed climate Indicator': ' Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation\n', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial flood']},
    {'Infrastructure': 'Road', 'Asset': 'Road Structure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the road caused by increased precipitations', 'Preliminary climate Indicator': 'Substantial relative increase in annual precipitation\nRelative change in annual precipitation', 'Proposed climate Indicator': ' Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation\n', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion']},
    {'Infrastructure': 'Road', 'Asset': 'Road', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to strong winds ', 'Preliminary climate Indicator': 'Number of windy days\nNumber of very windy days\nNumber of high wind days\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Road', 'Asset': 'Roadside Equipment', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages associated to strong winds', 'Preliminary climate Indicator': 'Number of windy days\nNumber of very windy days\nNumber of high wind days\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Road', 'Asset': 'Road', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to strong winds ', 'Preliminary climate Indicator': 'Number of windy days\nNumber of very windy days\nNumber of high wind days\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Air surface temperature increase (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased pavement maintenance due to temperature increase', 'Preliminary climate Indicator': 'Monthly mean temperature', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages associated to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages associated to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Road', 'Asset': 'Pavement', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']}
]

railway_data = [
    {'Infrastructure': 'Railway', 'Asset': 'Structures (excluding tunnels and bridges)', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation on superstructure elements.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Railway', 'Asset': 'Structures (excluding tunnels and bridges)', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation on superstructure elements.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Railway', 'Asset': 'Facilities, equipment and safety', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintentance due to snow accumulation on trains and increased energy consumption. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintentance due to snow accumulation on the catenary elements.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the catenary caused by snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Railway', 'Asset': 'Facilities, equipment and safety', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance for ensuring system reliability due to snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Railway', 'Asset': 'Slopes and embankments', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to embankment failure due to changes in precipitation.', 'Preliminary climate Indicator': 'Relative change in annual mean precipitation\\nSubstantial relative increase in mean annual precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Soil slope deformation & Soil creep', 'Landslides < 2 m depth', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Railway', 'Asset': 'Slopes and embankments', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by embankment failure due to changes in precipitation.', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Soil slope deformation & Soil creep', 'Landslides < 2 m depth', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Railway', 'Asset': 'Slopes and embankments', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of slopes due to changes in precipitation.', 'Preliminary climate Indicator': 'Relative change in annual mean precipitation\\nSubstantial relative increase in mean annual precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Soil slope deformation & Soil creep', 'Sheet erosion & rill erosion', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to heavy rain', 'Preliminary climate Indicator': 'Substantial relative increase in mean annual precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial flood']},
    {'Infrastructure': 'Railway', 'Asset': 'Drainage systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of the drainage system due to increased precipitation', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Railway', 'Asset': 'Drainage systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the drainage system due to increased precipitation', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to damage to the track bed', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)\\nSubstantial relative increase in mean annual precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion', 'Fluvial flood']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damage in the track bed due to acumulated sedimentation or flooding.', 'Preliminary climate Indicator': '?', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport', 'Fluvial flood']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance for damage to the track bed (ballast) due to changes in precipitation', 'Preliminary climate Indicator': 'Frequency of precipitation\\nReturn period of 10, 20, 25, 50 and 100 years of maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion']},
    {'Infrastructure': 'Railway', 'Asset': 'Structures (excluding tunnels and bridges)', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenange of the steel elements due to changes in precipitation.', 'Preliminary climate Indicator': 'Substantial relative increase in mean annual precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the ballast caused by changes in precipitation.', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion']},
    {'Infrastructure': 'Railway', 'Asset': 'Facilities, equipment and safety', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to signal and electrical systems malfunction due to heavy rains.', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Storms & strong winds']},
    {'Infrastructure': 'Railway', 'Asset': 'Facilities, equipment and safety', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the signal and electrical systems caused by heavy rains.', 'Preliminary climate Indicator': '25‐year return period for maximum 1‐day precipitation (P25)', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Storms & strong winds']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to strong winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to strong winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by strong winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive Capex due to damages on the rail track and platform associated to strong winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive Capex due to damages on the catenary elements due to strong winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of the catenary elements due to high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to power outages caused by high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Snow drift']},
    {'Infrastructure': 'Railway', 'Asset': 'Buildings', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased energy consumption due to temperature increase (stations)', 'Preliminary climate Indicator': 'Cooling degree days', 'Proposed climate Indicator': 'Cooling degree days?', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance on track rails due to buckling caused by high temperatures', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nAverage number of days per year with daily maximum temperature >=45°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Railway', 'Asset': 'Rail Track and Platform', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nAverage number of days per year with daily maximum temperature >=45°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to thermal expansion of the catenary', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nAverage number of days per year with daily maximum temperature >=45°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high temperatures affecting the power lines.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nAverage number of days per year with daily maximum temperature >=45°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Railway', 'Asset': 'Facilities, equipment and safety', 'Climate driver': 'Changes in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high temperatures affecting the signaling and control systems.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nAverage number of days per year with daily maximum temperature >=45°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive Capex due to lack of electrical contact between pantograph and catenary', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to lack of electrical contact between pantograph and catenary', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C\\nMean annual temperature', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Railway', 'Asset': 'Electrical facilities', 'Climate driver': 'Changes in Temperature (Low temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to lack of electrical contact between pantograph and catenary', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']}
]

tunnels_data = [
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation causing blockage of entrances and exits', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation  to avoid blockage of entrances and exits', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Ventilation Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation causing the overloading of the ventilation systems. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Ventilation Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation  to avoid the malfunction of the ventilation systems.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to snow collapse in the entrances or structures of the tunnel. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow avalanches', 'Snow drift', 'Snow creep & slide']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to damages on the infrastructure equipments or assets due to snow collapse in the entrances/exits. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow avalanches', 'Snow drift']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to drainage systems saturation. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation  to avoid the saturation of drainage systems. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Fluvial sediment transport']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to structural damages caused by structural damages caused by additional snow loads on the infrastructure. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow creep & slide', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to the closure of the tunnel caused by structural damages. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow creep & slide', 'Snow avalanches']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': "Increased maintenance due to snow accumulation to avoid additional snow loads to the tunnel's structure. ", 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow creep & slide', 'Snow drift']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintentance due to snow accumulation. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation on electrical and mechanical systems. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Tunnels ', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages associated to heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Landslides < 2 m depth']},
    {'Infrastructure': 'Tunnels ', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to the affection of tunnel equipments by heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to drainage systems saturation.', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to heavy rains to avoid the saturation of drainage systems. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to heavy rains.', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages associated to heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': ' Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to landslides/debris affecting the tunnel entrances/exits.', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': ' Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Landslides < 2 m depth', 'Debris flow (Volumetric Sediment Concentration >40%)', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Ventilation Systems', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased energy consumption to maintain airflow balance. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the external structure or equipments of the tunnel due to high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Power & Communication Systems', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the power and communication systems connected to the tunnel. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Power & Communication Systems', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': "Stop of operations due to power and communication systems' disruption due to high winds. ", 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Tunnel Structure', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the tunnel structure due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Pavements & Rail Tracks', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the pavements or rail tracks infrastructure inside the tunnel due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\\nNumber of consecutive days with daily maximum temperature >40°C??', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Ventilation Systems', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased energy consumption to maintain safe temperatures. ', 'Preliminary climate Indicator': 'Cooling degree days', 'Proposed climate Indicator': 'Monthly mean temperature\\nCooling degree days', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': "Reactive CAPEX due to damages and deterioration of tunnel's equipment.", 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintentance due to cold temperatures. ', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Electrical & Mechanical Systems', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': "Reactive CAPEX due to damages and deterioration of tunnel's equipment.", 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Tunnels', 'Asset': 'Ventilation Systems', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased energy consumption to maintain safe temperatures. ', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']}
]

bridges_data = [
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)', 'Snow avalanches']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the bridge structure caused by snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow creep & slide', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to snow accumulation in the drainage systems. ', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to snow accumulation.', 'Preliminary climate Indicator': 'Winter months accumulated snow', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Substructure & Foundations', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to flooding caused by heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \\nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Pluvial flood, heavy rainfall and surface runoff', 'Stream bank & bed erosion']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages on the bridge structure caused by extreme precipitations. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Storms & strong winds']},
    {'Infrastructure': 'Bridges', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to heavy rains.', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Storms & strong winds']},
    {'Infrastructure': 'Bridges', 'Asset': 'Drainage Systems', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance to clear and upgrade the drainage systems due to heavy rains.', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Bridges', 'Asset': 'Substructure & Foundations', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance related to erosion control due to heavy rains. ', 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial sediment transport', 'Fluvial flood']},
    {'Infrastructure': 'Bridges', 'Asset': 'Substructure & Foundations', 'Climate driver': 'Changes in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': "Reactive CAPEX due to damages in the bridge's foundations due to heavy rains.", 'Preliminary climate Indicator': '25-year return period of maximun 1-day precipitation', 'Proposed climate Indicator': 'Daily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial flood', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': "Reactive CAPEX due to damages in the bridge's structure due to high winds.", 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance to prevent long-term damage and need for enhanced monitoring due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Bridges', 'Asset': 'Ancillary Assets (Signage, Gantries, Barriers)', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages in the auxiliary structures caused by high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Hail']},
    {'Infrastructure': 'Bridges', 'Asset': 'Ancillary Assets (Signage, Gantries, Barriers)', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of the protective and auxiliary structures due to high winds.', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Annual mean windspeed at 10 m', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in wind intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to high winds. ', 'Preliminary climate Indicator': 'Number of windy days\\nNumber of very windy days\\nNumber of high wind days\\nNumber of extreme wind days', 'Proposed climate Indicator': 'Average number of days per year with daily mean wind speed  >=20 km/h', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Storms & strong winds', 'Desertification', 'Snow drift']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to high temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow creep & slide']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow drift']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Superstructure', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to damages caused by low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Bridges', 'Asset': 'Bridge Deck & Pavement', 'Climate driver': 'Changes in temperature (Low temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to low temperatures.', 'Preliminary climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']}
]

green_spaces_data = [
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'low degree of green space utilization, due to decreasing aesthetic value and reduced user benefits...', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'low level of use of green space due to unsuitable conditions for citizens...', 'Preliminary climate Indicator': 'Ground-level heat wave frequency', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C\nMean temperature at ground level over threshold?', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance with plants and materials.', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to restoration servicies', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Increase in required time to generate specific benefits', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chemicals tratements due to the decrease in the natural immunity of plants.', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced benefits', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'low degree of use of green spaces due to their low attractiveness...', 'Preliminary climate Indicator': 'Biodiversity level', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chemicals tretements due to ecolgical disruption.', 'Preliminary climate Indicator': 'Biodiversity level', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Irrigation & Water Systems', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with water supplies.', 'Preliminary climate Indicator': 'Soil humidity', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chemical tretements due to ecolgical disruption.', 'Preliminary climate Indicator': 'Annual average temperature', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Irrigation & Water Systems', 'Climate driver': 'Extreme heat (including heatwaves)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with irrigation costs due to depletion in soil water resources.', 'Preliminary climate Indicator': 'Soil humidity', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Reduced atmosferic humidity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced benefits', 'Preliminary climate Indicator': 'Air humidity', 'Proposed climate Indicator': 'Number of days with relative humidity under 40%', 'Dictionary Key': 'hurs40_days', 'Possible Hazards': ['Drought', 'Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Irrigation & Water Systems', 'Climate driver': 'Reduced atmosferic humidity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased irrigation costs to compensate for reduced soil water resources due to lack of water condensation.', 'Preliminary climate Indicator': 'Air humidity', 'Proposed climate Indicator': 'Number of days with relative humidity under 40%', 'Dictionary Key': 'hurs40_days', 'Possible Hazards': ['Drought', 'Extreme high temperatures (Heatwave)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Reduced atmosferic humidity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chelicals tretements due to ecolgical disruption.', 'Preliminary climate Indicator': 'Biodiversity level', 'Proposed climate Indicator': 'Number of days with relative humidity under 40%', 'Dictionary Key': 'hurs40_days', 'Possible Hazards': ['Drought', 'Extreme high temperatures (Heatwave)', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Low precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'low degree of green space utilization and consequently a reduced level of ecosystem services provided by it', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought...', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'green spaces', 'Asset': 'Irrigation & Water Systems', 'Climate driver': 'Low precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with water supplies.', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Low precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chemicals tretements due to the decrease in the natural immunity of plants...', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Irrigation & Water Systems', 'Climate driver': 'Low precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'The increasing maintenance costs of irrigation systems due to deposits (limestone, iron, algae) from the water used for irrigation', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Low precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to green space restoration services by replacing dead plants ', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought...', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Desertification', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Low precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chelicals tretements due to ecolgical disruption.', 'Preliminary climate Indicator': 'Biodiversity level', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Increased solar intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'low level of use of green space due to unsuitable conditions for citizens...', 'Preliminary climate Indicator': 'Solar intensity', 'Proposed climate Indicator': 'Solar radiation intensity at plant level', 'Dictionary Key': 'par_plant_level', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Green Space Areas', 'Climate driver': 'Increased solar intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced benefits', 'Preliminary climate Indicator': 'Solar intensity', 'Proposed climate Indicator': 'Solar radiation intensity at plant level', 'Dictionary Key': 'par_plant_level', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'green spaces', 'Asset': 'Vegetation (Plants & Trees)', 'Climate driver': 'Increased solar intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increase in maintenance costs with chemicals tretements due to the decrease in the natural immunity of plants...', 'Preliminary climate Indicator': 'Biodiversity level', 'Proposed climate Indicator': 'Solar radiation intensity at plant level', 'Dictionary Key': 'par_plant_level', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']}
]

dams_data = [
    {'Infrastructure': 'Dams', 'Asset': 'Spillways & Intakes', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to spillway blockage causing damage to the dam structure.', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flood (Volumetric Sediment Concentration 20-40%)', 'Pluvial flood, heavy rainfall and surface runoff', 'Fluvial sediment transport']},
    {'Infrastructure': 'Dams', 'Asset': 'Reservoir Basin', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to extreme water conditions.', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Pluvial flood, heavy rainfall and surface runoff', 'Fluvial flood']},
    {'Infrastructure': 'Dams', 'Asset': 'Catchment Area & Slopes', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to erosion', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Sheet erosion & rill erosion', 'Gully erosion', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Dams', 'Asset': 'Reservoir Basin', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to sedimentation and reservoir capacity reduction', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial sediment transport', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Dams', 'Asset': 'Dam Structure', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Increased water levels in the reservoir may cause damage to the dam', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Dams', 'Asset': 'Catchment Area & Slopes', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Increased maintenance due to landslide', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Landslides 2-10 m depth', 'Mud or Earth flow', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Dams', 'Asset': 'Catchment Area & Slopes', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Increased mainenance cost due to rockflow', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Small Rockfall (Diameter <25cm)', 'Large Rockfall (Diameter >25-100 cm)', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'Dams', 'Asset': 'Power Generation Equipment', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced Power Generation due to debris accumulation', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flood (Volumetric Sediment Concentration 20-40%)', 'Fluvial sediment transport']},
    {'Infrastructure': 'Dams', 'Asset': 'Power Generation Equipment', 'Climate driver': 'Extreme precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced Power Generation due to landslide and rockfall ', 'Preliminary climate Indicator': 'Annual average precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Landslides 2-10 m depth', 'Small Rockfall (Diameter <25cm)']},
    {'Infrastructure': 'Dams', 'Asset': 'Access Roads', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations of the road', 'Preliminary climate Indicator': 'Winter months', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Snow avalanches', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Dams', 'Asset': 'Operational Buildings', 'Climate driver': 'Changes in snow intensity', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to the blockage of the operational building', 'Preliminary climate Indicator': 'Winter months', 'Proposed climate Indicator': 'Winter months accumulated snow', 'Dictionary Key': 'solidprcptot_winter', 'Possible Hazards': ['Snow drift', 'Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Dams', 'Asset': 'Access Roads', 'Climate driver': 'Extreme temperature (low)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Delay in maintaning operations due to blockage of the road', 'Preliminary climate Indicator': 'Low tempearature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Snow drift']},
    {'Infrastructure': 'Dams', 'Asset': 'Operational Buildings', 'Climate driver': 'Extreme temperature (low)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Delay in maintaning operations due to operational building', 'Preliminary climate Indicator': 'Low tempearature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Dams', 'Asset': 'Power Generation Equipment', 'Climate driver': 'Extreme temperature (low)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced Power Generation due to landslide and rockfall ', 'Preliminary climate Indicator': 'Low tempearature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)', 'Small Rockfall (Diameter <25cm)', 'Snow creep & slide']},
    {'Infrastructure': 'Dams', 'Asset': 'Reservoir Basin', 'Climate driver': 'Extreme temperature (low)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Stop of operations due to ice formation ', 'Preliminary climate Indicator': 'Low temperature', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Dams', 'Asset': 'Catchment Area & Slopes', 'Climate driver': 'Reduced atmosferic humidity', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced protection for landslide and erosion', 'Preliminary climate Indicator': 'Low tempearature', 'Proposed climate Indicator': '?', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Soil slope deformation & Soil creep', 'Aeolian erosion']},
    {'Infrastructure': 'Dams', 'Asset': 'Catchment Area & Slopes', 'Climate driver': 'Low precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Greater potential for erosion', 'Preliminary climate Indicator': 'Level of precipitations', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought...', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Aeolian erosion', 'Desertification']}
]

river_data = [
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Stream bank & bed erosion', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Stream bank & bed erosion', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excess bank collapses potentially leading to channel migration/shifting.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Landslides < 2 m depth', 'Fluvial flood']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX in case of large structural damages to embankments and leeves.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Stream bank & bed erosion']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean temperature', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Channel & Bed', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excessive scour.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial flood']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to hydraulic overloading and structural damage.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Fluvial flood', 'Stream bank & bed erosion']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Fluvial flood', 'Pluvial flood, heavy rainfall and surface runoff']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Channel & Bed', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excessive deposition lowering hydrualic conveyance.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Fluvial sediment transport', 'Fluvial flood']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Concrete Revetments & Walls', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance for protecting concrete surfaces in contact with river flow.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial flood']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX if channel shifts to the edge of the river corridor causing levees undermining.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial flood']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX in the first few years after execution of soil bioengineering works when vegetation is not fully rooted yet.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Sheet erosion & rill erosion']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Low degree of river space utilization, due to decreasing aesthetic value and reduced user benefits, and consequently a reduced level of ecosystem services\xa0provided\xa0by\xa0it', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to restoration works (planting new vegetation).', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'River Ecosystem & Amenity', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services of living plants.', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20 (Proxy)', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'River training infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX after frosty periods/years to replace frost-bitten vegetation.', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20 (Proxy)', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']}
]

torrent_data = [
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Check Dams & Weirs', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flow (Volumetric Sediment Concentration >40%)', 'Debris flood (Volumetric Sediment Concentration 20-40%)', 'Fluvial flood']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Check Dams & Weirs', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation \nDaily probability of three or more consecutive days exceeding the 90th percentile of daily mean precipitation', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flow (Volumetric Sediment Concentration >40%)', 'Debris flood (Volumetric Sediment Concentration 20-40%)', 'Fluvial flood']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excess bank collapses potentially leading to channel migration/shifting.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Debris flood (Volumetric Sediment Concentration 20-40%)', 'Landslides < 2 m depth']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX in case of large structural damages to embankments and leeves.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flow (Volumetric Sediment Concentration >40%)', 'Stream bank & bed erosion', 'Fluvial flood']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Check Dams & Weirs', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flow (Volumetric Sediment Concentration >40%)', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Channel Bed', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excessive scour.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Stream bank & bed erosion', 'Fluvial sediment transport']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Check Dams & Weirs', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance due to hydraulic overloading and structural damage.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Debris flood (Volumetric Sediment Concentration 20-40%)', 'Fluvial sediment transport']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Check Dams & Weirs', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to hydraulic overloading and needed reconstruction works.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Debris flow (Volumetric Sediment Concentration >40%)', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Channel Bed', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance in case of excessive deposition lowering hydrualic conveyance.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Fluvial sediment transport', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Concrete Surfaces', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance for protecting concrete surfaces in contact with torrential flow.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Fluvial sediment transport', 'Debris flood (Volumetric Sediment Concentration 20-40%)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Embankments & Levees', 'Climate driver': 'Change in precipitation', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX if channel shifts to the edge of the river corridor causing levees undermining.', 'Preliminary climate Indicator': 'Maximum daily precipitation', 'Proposed climate Indicator': 'Return period of 100 years of maximum daily precipitation ', 'Dictionary Key': 'rx1day_rp100', 'Possible Hazards': ['Stream bank & bed erosion', 'Debris flood (Volumetric Sediment Concentration 20-40%)', 'Fluvial flood']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Ecosystem Services', 'Climate driver': 'Change in precipitation (Low)', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in precipitation (Low)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'Monthly mean precipitation', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in precipitation (Low)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX in the first few years after execution of soil bioengineering works when vegetation is not fully rooted yet.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm & Maximum consecutive days without rain', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Desertification', 'Sheet erosion & rill erosion']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Ecosystem Services', 'Climate driver': 'Change in precipitation (Low)', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Number of days with precipitation below 1mm', 'Proposed climate Indicator': 'SPEI - The annual probability of experiencing  SEVERE short-term term drought, determined by the Standardized Precipitation Evaporation Index (SPEI)', 'Dictionary Key': 'spei3_severe_prob', 'Possible Hazards': ['Drought', 'Desertification']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Ecosystem Services', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Low degree of river space utilization, due to decreasing aesthetic value and reduced user benefits, and consequently a reduced level of ecosystem services\xa0provided\xa0by\xa0it', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX due to restoration works (planting new vegetation).', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought', 'Wildfire (Forest fire or Bush fire)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Ecosystem Services', 'Climate driver': 'Change in Temperature (High temperatures)', 'Type of impact': 'Operations', 'Consequences': 'Revenues loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services.', 'Preliminary climate Indicator': 'Annual average temperature - Number of days with temperatures over 35 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature >=40°C', 'Dictionary Key': 'tx40', 'Possible Hazards': ['Extreme high temperatures (Heatwave)', 'Drought']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Operations', 'Consequences': 'Revenue loss', 'Impact model': 'Reduced benefits and reduced levels of ecosystem services of living plants.', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Maintenance', 'Consequences': 'Increase OPEX', 'Impact model': 'Increased maintenance of soil bioengineering works (living plants).', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Monthly mean temperature', 'Dictionary Key': 'Not found', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']},
    {'Infrastructure': 'Torrent control infrastructure', 'Asset': 'Bioengineering & Vegetation', 'Climate driver': 'Change in temperature (Low temperature)', 'Type of impact': 'Damages', 'Consequences': 'Increase CAPEX', 'Impact model': 'Reactive CAPEX after frosty periods/years to replace frost-bitten vegetation.', 'Preliminary climate Indicator': 'Number of days with temperatures below -20 degrees C', 'Proposed climate Indicator': 'Average number of days per year with daily maximum temperature < - 31°C', 'Dictionary Key': 'tn20', 'Possible Hazards': ['Extreme cold temperatures (Coldwave, cold snap)']}
]

NbS_list = [{
  "Extreme high temperatures (Heatwave)": {
    "Yes": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Open green spaces", "Green pavers", "Green roofs", "Vertical greenery", "Urban forests", "Rain gardens", "Bio-retention cells, basins and ponds", "Infiltration trenches"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Riparian buffer zones", "Floodplain restoration", "Meandering channel planform", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Living shorelines", "Salt marsh restoration", "Mangroves", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Bioswales"]
  },
  "Extreme cold temperatures (Coldwave, cold snap)": {
    "Yes": [],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Living shorelines", "Mangroves", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Green roofs", "Vertical greenery", "Urban forests"]
  },
  "Drought": {
    "Yes": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Afforestation and reforestation", "Protection forest management", "Wetland conservation and restoration", "Agroforestry", "Horticulture", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Controlled grazing", "Contour trenching", "Conservation tillage", "Mulching", "Cover cropping", "Soil amendments (previosly organic amendments)", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Floodplain restoration", "Meandering channel planform", "Channel widening", "Sills", "Water retention basins and ponds (storage ponds)", "Constructed wetlands", "Salt marsh restoration", "Live staking", "Live slope grids or contour logs", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Live fascines", "Brush mattress", "Open green spaces", "Green pavers", "Green roofs", "Vertical greenery", "Urban forests", "Rain gardens", "Bio-retention cells, basins and ponds", "Infiltration trenches", "Bioswales"]
  },
  "Wildfire (Forest fire or Bush fire)": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Firebreaks and firestrips", "Fire-resistant tree species & plants", "Prescribed burning", "Channel widening", "Controlled grazing", "Fire-smart agriculture"],
    "Supportive": ["NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Salt marsh restoration", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)"]
  },
  "Desertification": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Dune restoration and coastal vegetation", "Sand dune stabilization", "Agroforestry", "Horticulture", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Controlled grazing", "Contour trenching", "Conservation tillage", "Mulching", "Cover cropping", "Soil amendments (previosly organic amendments)", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)"],
    "Supportive": ["Buffer vegetation strips and coppice management", "Riparian buffer zones", "Floodplain restoration", "Meandering channel planform", "Channel widening", "Sills", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Living shorelines", "Salt marsh restoration", "Mangroves", "Sod (turves)", "Live staking", "Live slope grids or contour logs", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Live fascines", "Brush mattress", "Open green spaces", "Green pavers", "Green roofs", "Vertical greenery", "Urban forests", "Rain gardens", "Bio-retention cells, basins and ponds", "Infiltration trenches"]
  },
  "Storms & strong winds": {
    "Yes": ["Agroforestry", "Live fencing (for slope engineering)"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Floodplain restoration", "Living shorelines", "Mangroves", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Vegetated cribwall (layer-based design)", "Live palisades and live weirs", "Wooden log fences"]
  },
  "Hail": {
    "Yes": ["Can be supportive to conventional structural measures", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Wildfire-forest management"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "Agroforestry", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences", "Green roofs"]
  },
  "Aeolian erosion": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Living shorelines", "Dune restoration and coastal vegetation", "Sand dune stabilization", "Mangroves", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Controlled grazing", "Fire-smart agriculture", "Contour trenching", "Conservation tillage", "Mulching", "Soil amendments (previosly organic amendments)", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "Floodplain restoration", "Cover cropping", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences"]
  },
  "Pluvial flood, heavy rainfall and surface runoff": {
    "Yes": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Earth dams and barriers (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Vegetated flood protection dams, dikes & levees", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Salt marsh restoration", "Agroforestry", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)", "Green corridors & tree rows", "Meadow & grassland restoration", "Vegetated buffer zones", "Contour trenching", "Mulching", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Vegetated riprap", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Open green spaces", "Green pavers", "Green roofs", "Urban forests", "Rain gardens", "Bio-retention cells, basins and ponds", "Infiltration trenches"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Controlled grazing", "Conservation tillage", "Cover cropping", "Soil amendments (previosly organic amendments)", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Tree revetment (tree spurs)", "Root wad", "Wooden log fences", "Vertical greenery", "Bioswales"]
  },
  "Fluvial flood": {
    "Yes": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Riparian buffer zones", "Floodplain restoration", "Meandering channel planform", "Channel widening", "Sills", "Groynes (vegetated)", "Vegetated flood protection dams, dikes & levees", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Salt marsh restoration", "Agroforestry", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)", "Green corridors & tree rows", "Meadow & grassland restoration", "Vegetated buffer zones", "Contour trenching", "Mulching", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Vegetated riprap", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Open green spaces", "Urban forests", "Bioswales"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Controlled grazing", "Conservation tillage", "Cover cropping", "Soil amendments (previosly organic amendments)", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Tree revetment (tree spurs)", "Root wad", "Wooden log fences", "Green pavers", "Green roofs", "Vertical greenery", "Rain gardens", "Bio-retention cells, basins and ponds", "Infiltration trenches"]
  },
  "Coastal flood (e.g. storm surge)": {
    "Yes": ["Mitigation of ongoing Hazard Process", "Vegetated flood protection dams, dikes & levees", "Living shorelines", "Dune restoration and coastal vegetation", "Sand dune stabilization", "Salt marsh restoration", "Mangroves", "Live staking", "Wattle fence (for water enginering)"],
    "Supportive": ["Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Wetland conservation and restoration", "Constructed wetlands", "Coral reef conservation and restoration", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques"]
  },
  "Impact floods and Tsunami": {
    "Yes": ["Can be supportive to conventional structural measures"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Buffer vegetation strips and coppice management", "Living shorelines", "Dune restoration and coastal vegetation", "Sand dune stabilization", "Mangroves"]
  },
  "Fluvial sediment transport": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Floodplain restoration", "Meandering channel planform", "Channel widening", "Sills", "Groynes (vegetated)", "Vegetated flood protection dams, dikes & levees", "Salt marsh restoration", "Green corridors & tree rows", "Vegetated buffer zones", "Vegetated crib wall (fascine-based design)", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences"],
    "Supportive": ["Avalanche mounds", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Agroforestry", "Horticulture", "Water retention, harvesting & cisterns", "Biodiverse hedgerows", "Meadow & grassland restoration", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Vegetated cribwall (layer-based design)", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Urban forests", "Infiltration trenches", "Bioswales"]
  },
  "Stream bank & bed erosion": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Riparian buffer zones", "Floodplain restoration", "Meandering channel planform", "Channel widening", "Sills", "Groynes (vegetated)", "Vegetated flood protection dams, dikes & levees", "Salt marsh restoration", "Vegetated buffer zones", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences"],
    "Supportive": ["Avalanche mounds", "Water retention basins and ponds (storage ponds)", "Wetland conservation and restoration", "Constructed wetlands", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Wattle fence (for water enginering)", "Urban forests", "Infiltration trenches", "Bioswales"]
  },
  "Sheet erosion & rill erosion": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Salt marsh restoration", "Agroforestry", "Horticulture", "Water retention, harvesting & cisterns", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Contour trenching", "Conservation tillage", "Mulching", "Cover cropping", "Soil amendments (previosly organic amendments)", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Wooden log fences"],
    "Supportive": ["Avalanche mounds", "Controlled grazing", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Infiltration trenches"]
  },
  "Gully erosion": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Salt marsh restoration", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Vegetated drainage systems", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences"],
    "Supportive": ["Avalanche mounds", "Agroforestry", "Vegetated buffer zones", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Wattle fence (for water enginering)"]
  },
  "Coastal and shoreline erosion (includes freshwater environments)": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Living shorelines", "Dune restoration and coastal vegetation", "Sand dune stabilization", "Salt marsh restoration", "Mangroves", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Vegetated cribwall (layer-based design)", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs"],
    "Supportive": ["Avalanche mounds", "Vegetated flood protection dams, dikes & levees", "Seagrass bed restoration", "Coral reef conservation and restoration", "Green corridors & tree rows", "Biodiverse hedgerows", "Vegetated buffer zones"]
  },
  "Debris flood (Volumetric Sediment Concentration 20-40%)": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Earth dams and barriers (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Buffer vegetation strips and coppice management", "Channel widening", "Vegetated flood protection dams, dikes & levees"],
    "Supportive": ["NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Avalanche mounds", "3-D steel grids (vegetated)", "Riparian buffer zones", "Sills", "Groynes (vegetated)", "Salt marsh restoration", "Agroforestry", "Horticulture", "Water retention, harvesting & cisterns", "Managed aquifer recharge (MAR)", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Sod (turves)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Wattle fence (for water enginering)", "Tree revetment (tree spurs)", "Vegetated riprap", "Root wad", "Vegetated crib wall (fascine-based design)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Vegetated log/stone barriers and live/rock check dams", "Wooden log fences", "Open green spaces", "Urban forests", "Rain gardens", "Infiltration trenches"]
  },
  "Debris flow (Volumetric Sediment Concentration >40%)": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Retention forest", "Vegetated flood protection dams, dikes & levees", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Vegetated riprap", "Vegetated crib wall (fascine-based design)", "Vegetated log/stone barriers and live/rock check dams", "Urban forests"],
    "Supportive": ["3-D steel grids (vegetated)", "Riparian buffer zones", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live fascines", "Brush mattress", "Live palisades and live weirs", "Wooden log fences"]
  },
  "Small Rockfall (Diameter <25cm)": {
    "Yes": ["Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "Afforestation and reforestation", "Protection forest management", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated riprap", "Wooden log fences", "Urban forests"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "Can be supportive to conventional structural measures", "Retention forest", "3-D steel grids (vegetated)", "Vegetated cribwall (layer-based design)"]
  },
  "Large Rockfall (Diameter >25-100 cm)": {
    "Yes": ["Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "Afforestation and reforestation", "Protection forest management", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated riprap", "Wooden log fences", "Urban forests"]
  },
  "Landslides < 2 m depth": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Vegetated riprap", "Urban forests"],
    "Supportive": ["Can be supportive to conventional structural measures", "Retention forest", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones"]
  },
  "Landslides 2-10 m depth": {
    "Yes": ["Vegetated drainage systems"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Urban forests"]
  },
  "Landslides > 10 m depths": {
    "Yes": ["Can be supportive to conventional structural measures", "Vegetated drainage systems"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Afforestation and reforestation", "Protection forest management"]
  },
  "Mud or Earth flow": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Avalanche mounds", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Urban forests"],
    "Supportive": ["NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Retention forest", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Vegetated riprap"]
  },
  "Soil slope deformation & Soil creep": {
    "Yes": ["Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Avalanche mounds", "3-D steel grids (vegetated)", "Reinforced soil and earth packs (vegetated)", "Afforestation and reforestation", "Protection forest management", "Live layered techniques", "Vegetated cribwall (layer-based design)", "Vegetated drainage systems", "Urban forests"],
    "Supportive": ["Mitigation of Formation or Trigger mechanism", "Can be supportive to conventional structural measures", "Retention forest", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Biodiverse hedgerows", "Meadow & grassland restoration", "Vegetated buffer zones", "Hydro and mulch seeding", "Vegetated biodegradeable erosion control meshes", "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)", "Live staking", "Live fencing (for slope engineering)", "Live slope grids or contour logs", "Vegetated riprap"]
  },
  "Snow avalanches": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Can be supportive to conventional structural measures", "Earth dams and barriers (vegetated)", "Avalanche mounds", "Afforestation and reforestation", "Protection forest management"],
    "Supportive": ["Mitigation of ongoing Hazard Process", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Vegetated cribwall (layer-based design)", "Vegetated crib wall (fascine-based design)", "Vegetated log/stone barriers and live/rock check dams"]
  },
  "Snow drift": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "Earth dams and barriers (vegetated)", "Avalanche mounds", "Afforestation and reforestation", "Protection forest management", "Green corridors & tree rows", "Biodiverse hedgerows", "Vegetated buffer zones", "Vegetated cribwall (layer-based design)", "Vegetated crib wall (fascine-based design)", "Wooden log fences", "Urban forests"],
    "Supportive": ["NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Agroforestry", "Horticulture", "Meadow & grassland restoration", "Live staking", "Live fencing (for slope engineering)"]
  },
  "Snow creep & slide": {
    "Yes": ["Mitigation of Formation or Trigger mechanism", "Mitigation of ongoing Hazard Process", "Can be supportive to conventional structural measures", "NbS-Type: Terracing (slope shaping, reduction of slope inclination)", "Earth dams and barriers (vegetated)", "Avalanche mounds", "Afforestation and reforestation", "Protection forest management", "Vegetated buffer zones", "Live fencing (for slope engineering)", "Vegetated cribwall (layer-based design)", "Vegetated crib wall (fascine-based design)", "Wooden log fences", "Urban forests"],
    "Supportive": ["Retention forest", "Wildfire-forest management", "Buffer vegetation strips and coppice management", "Riparian buffer zones", "Agroforestry", "Horticulture", "Green corridors & tree rows", "Meadow & grassland restoration"]
  }
}]
def calculate_exposure(rev, cap, r_l, r_h, c_l, c_h):
    """Calculates Exposure Index based on user-defined thresholds."""
    if rev < r_l:
        if cap < c_l: return 1
        elif c_l <= cap <= c_h: return 2
        else: return 3
    elif r_l <= rev <= r_h:
        if cap < c_l: return 2
        elif c_l <= cap <= c_h: return 3
        else: return 4
    else: 
        if cap < c_l: return 3
        elif c_l <= cap <= c_h: return 4
        else: return 5
def polygon_style_function(feature):
    return {'fillColor': 'blue', 'color': 'blue'}

def generate_koppen_map_plot(lat, lon, zoom_range=1.0):
    cmap = ListedColormap(KOPPEN_COLORS)
    class_labels = [KOPPEN_CLASSES[i] for i in range(1, 31)]

    min_lon, max_lon = lon - zoom_range, lon + zoom_range
    min_lat, max_lat = lat - zoom_range, lat + zoom_range

    try:
        response = requests.get(KOPPEN_TIFF_URL, timeout=30)
        response.raise_for_status()

        with rasterio.open(io.BytesIO(response.content)) as src:
            data = src.read(1)
            row_min, col_min = src.index(min_lon, max_lat)
            row_max, col_max = src.index(max_lon, min_lat)

            row_start, row_end = sorted([row_min, row_max])
            col_start, col_end = sorted([col_min, col_max])

            data_cropped = data[row_start:row_end, col_start:col_end]

    except requests.exceptions.RequestException as e:
        return f"Error downloading Köppen TIFF: {e}", None
    except Exception as e:
        return f"Error processing Köppen map data: {e}", None

    data_cropped = np.where(data_cropped == 0, np.nan, data_cropped)

    koppen_code = "N/A"
    if data_cropped.size > 0:
        center_row = (data_cropped.shape[0]) // 2
        center_col = (data_cropped.shape[1]) // 2

        center_code = int(data_cropped[center_row, center_col]) if not np.isnan(
            data_cropped[center_row, center_col]) else None
        koppen_code = KOPPEN_CLASSES.get(
            center_code, "N/A") if center_code else "N/A"

    else:
        koppen_code = "N/A"

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(
        data_cropped,
        cmap=cmap,
        extent=(min_lon, max_lon, min_lat, max_lat),
        origin='upper',
        alpha=0.6,
        zorder=2
    )

    try:
        cx.add_basemap(ax, crs='EPSG:4326',
                       source=cx.providers.OpenTopoMap, alpha=0.8, zorder=1)
    except Exception:
        pass

    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_title(
        f"Köppen-Geiger Climate Classification (Center: {koppen_code})")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    cbar = plt.colorbar(im, ticks=range(1, 31), ax=ax,
                        fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(class_labels, fontsize=8)

    return fig, koppen_code

def generate_context_report(center_lat, center_lon, area_sq_km, elements):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    center_coord_str = f"{center_lat:.4f}, {center_lon:.4f}"

    infra_counts = {}
    for element in elements:
        tags = element.get('tags', {})
        for tag_key, tag_value in tags.items():
            if tag_key in ['building', 'highway', 'railway', 'water', 'power', 'amenity', 'leisure', 'natural']:
                category = tag_key.capitalize()
                infra_counts[category] = infra_counts.get(category, 0) + 1
                break

    extracted_infrastructure_list = "\n".join(
        [f"- {k}: {v} items" for k,
            v in sorted(infra_counts.items(), key=lambda item: item[1], reverse=True)]
    )
    if not extracted_infrastructure_list:
        extracted_infrastructure_list = "- No specific infrastructure elements found using the simple filters."

    detailed_elements = []
    for element in elements:
        elem_info = {
            'type': element.get('type', 'Unknown'),
            'id': element.get('id', 'N/A'),
            'tags': element.get('tags', {})
        }
        detailed_elements.append(elem_info)

    detailed_str = json.dumps(detailed_elements, indent=2)

    system_instruction = (
        "You are an expert geographical and infrastructure analyst. Your task is to generate a report "
        "by analyzing the provided OpenStreetMap data and geographical coordinate. "
        "**You must use the Google Search tool** to find contextual data, elevation, and topography for the given coordinate. "
        "Follow the specified structured output format strictly. DO NOT include any climate or weather information."
        " Analyze all provided tags in the detailed infrastructure data for deeper insights, such as materials or surfaces."
    )

    user_prompt = f"""
    Analyze the following geographical data for a selected area:

    1. **Geographical Area Details:**
        - **Approximate Center Coordinate (Latitude, Longitude):** {center_coord_str}
        - **Approximate Area:** {area_sq_km:.2f} square kilometers
        
    2. **Extracted OpenStreetMap Infrastructure Data (Summary of {len(elements)} Items):**
    {extracted_infrastructure_list}
    
    3. **Detailed OpenStreetMap Elements (Full Tags and Metadata):**
    {detailed_str}

    **REPORT INSTRUCTIONS:**
    Please use the coordinate and the extracted infrastructure details to search the internet for more contextual information about this geographical area.
    
    **Provide the report in the following structured format:**...
    """

    try:
        response = st.session_state["gemini_client"].models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt],
            config={
                "system_instruction": system_instruction,
                "tools": [{"google_search": {}}]
            }
        )
        return response.text
    except APIError as e:
        return f"Gemini API Error (Context Report): {e}."
    except Exception as e:
        st.error(f"An unexpected error occurred during context report generation: {e}")
        return "An unexpected error occurred during context report generation."

def generate_koppen_interpretation(koppen_code):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate climate interpretation."

    if koppen_code in ["N/A", "Unknown"]:
        return "Cannot generate interpretation. The Köppen climate code could not be determined from the map."

    system_instruction = (
        "You are an expert climatologist. Your task is to provide a detailed, easy-to-understand interpretation "
        "of the given Köppen Climate Classification code. **You must use the Google Search tool** "
        "to find detailed climate conditions. Ensure all temperatures are provided in Celcius. "
        "The response must focus purely on climate conditions and meaning."
    )

    user_prompt = f"""
    Provide a detailed interpretation of the following Köppen Climate Classification code: **{koppen_code}**.

    Your report must cover:
    1.  **Full Classification Name:** (e.g., 'Humid subtropical climate').
    2.  **Key Characteristics:** The general weather patterns, typical seasonal changes, and defining temperature and precipitation features (e.g., hot/cold summers, dry/wet winters).
    3.  **Ecological Implications:** Briefly mention the types of vegetation or agriculture typically found in this climate.
    
    Structure the answer logically using headings and bullet points.
    """

    try:
        response = st.session_state["gemini_client"].models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt],
            config={
                "system_instruction": system_instruction,
                "tools": [{"google_search": {}}]
            }
        )
        return response.text
    except APIError as e:
        return f"Gemini API Error (Köppen Interpretation): {e}."
    except Exception as e:
        st.error(f"An unexpected error occurred during Köppen interpretation generation: {e}")
        return "An unexpected error occurred during Köppen interpretation generation."

def generate_risk_interpretation(df_risks: pd.DataFrame, kpis: list, scenarios: dict):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate risk interpretation."

    df_risks_prompt = df_risks.rename_axis('').to_markdown()

    example_table = """
| KPI / Indicator | CI_H | CI_HG |
| :--- | :---: | :---: |
| Safety, Reliability and Security (SRS) | 5 | 4 |
| Availability and Maintainability (AM) | 3 | 2 |
| Economy (EC) | 4 | 2 |
| Environment (EV) | 3 | 3 |
| Health and Politics (HP) | 4 | 3 |
"""
    example_text = (
        "As indicated in the assessment, the implementation of a Grey Protective Infrastructure (GPI) "
        "from the “Water engineering” family, such as selected “Flood walls” and “Floodway”, leads to a "
        "noticeable improvement in the condition of the CI, apart from Environment (EV) that stays the same (3 → 3). "
        "Specifically, these GPI solutions contribute to enhancing the Structural and Resilience Stability (SRS) (5 → 4), "
        "Availability and Maintainability (AM) (3 → 2), and Health and Politics (HP) (4 → 3) indicators, raising their "
        "condition levels each for one grade in the scoring table. Furthermore, the Economy (EC) shows even greater "
        "improvement – for two grades in the scoring table, reaching a “Good” (4 → 2) condition. These results were "
        "based on expert judgement, how classical grey infrastructure being flood resilient for itself if designed "
        "properly, improves hydraulic conveyance, decreases flooding of the neighbouring area, and stabilises channel "
        "banks and thus protect nearby infrastructure. It is to be mentioned here, that even higher grades cannot be "
        "reached with only grey infrastructure, even though it is flood resistant per se."
    )

    scenario_desc = "\n".join([f"- **{abbr}**: {desc}" for abbr, desc in scenarios.items()])
    kpi_list = "\n".join([f"- {k}" for k in kpis])

    system_instruction = (
        "You are an expert risk and resilience analyst. Your task is to interpret a stakeholder "
        "risk assessment matrix. The ratings are from $1$ (best) to $5$ (worst). "
        "You must follow the logical structure and professional tone provided in the 'EXAMPLE ANALYSIS' section. "
        "Specifically, focus on comparing the Hazard scenario (CI_H) with the protected scenarios "
        "and explain the numerical differences (e.g., $4 \rightarrow 3$) based on the engineering logic provided."
    )

    user_prompt = f"""
    ### EXAMPLE ANALYSIS (Learning Reference)
    **Example Data Table:**
    {example_table}

    **Example Interpretation:**
    {example_text}

    ---

    ### ACTUAL DATA TO ANALYZE
    Analyze the following risk matrix provided by stakeholders. 

    **KPIs (Rows):**
    {kpi_list}

    **Scenarios (Columns):**
    {scenario_desc}
    
    **Risk Assessment Matrix:**
    {df_risks_prompt}

    **REPORT INSTRUCTIONS:**
    Provide a professional interpretation following the style of the example. 
    1. Compare CI_H to the protection scenarios (CI_HG, CI_HN, CI_HNG).
    2. Explicitly mention the numerical grade changes (e.g., $X \rightarrow Y$).
    3. Use professional reasoning to explain why certain measures (Grey vs. Nature-based) improve specific KPIs.
    """

    try:
        response = st.session_state["gemini_client"].models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt],
            config={
                "system_instruction": system_instruction, 
                "tools": [{"google_search": {}}] 
            }
        )
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

def generate_hazard_report_gemini(calculated_df):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    # Convert the current hazard table to markdown for the prompt
    hazard_table_md = calculated_df.to_markdown(index=False)
    
    system_instruction = (
        "You are an expert climate hazard analyst. Your task is to generate a professional report "
        "interpreting a climate hazard table calculated for a specific infrastructure project. "
        "The input data is a markdown table with columns: Infrastructure, Climate driver, Impact model, Hazard Index, and Hazard Level. "
        "You must follow the style, tone, and depth of the provided EXAMPLE REPORT strictly. "
        "Do NOT hallucinate data not present in the table. Use the provided Example Data and Example Report "
        "as a few-shot learning reference to understand how to map the table rows to a narrative text."
    )

    user_prompt = f"""
    ### REFERENCE EXAMPLE (LEARNING MATERIAL)
    
    **1. Example Data Source (Table Format):**
    {EXAMPLE_HAZARD_TABLE}

    **2. Example Report Interpretation (Based on above table):**
    {EXAMPLE_HAZARD_REPORT}

    ---

    ### ACTUAL TASK
    
    **Actual Hazard Data Table (to be analyzed):**
    {hazard_table_md}

    **INSTRUCTIONS:**
    1. Analyze the 'Actual Hazard Data Table' above.
    2. Write a narrative report similar in structure and tone to the 'Example Report Interpretation'.
    3. Group hazards logically (e.g., Temperature-related, Water-related, etc.) if applicable based on the 'Climate driver' column.
    4. Explicitly mention the 'Hazard Level' (e.g., EXTREME, HIGH, LOW) and 'Hazard Index' where relevant.
    5. Discuss the implications for the specific 'Infrastructure' and 'Asset' types listed in the table (Impact model column describes the asset/impact).
    6. If a hazard shows "No variation", explain what that implies for stability vs. potential shifts in intensity not captured by the mean.
    """

    try:
        response = st.session_state["gemini_client"].models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt],
            config={
                "system_instruction": system_instruction,
                "temperature": 0.3 
            }
        )
        return response.text
    except Exception as e:
        return f"Error generating hazard report: {e}"
def generate_pri_report_gemini(calculated_df):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    # Filter and Rename columns to match the standard abbreviations (HI, EI, VI)
    # This helps the AI map the data to the prompt logic easily
    df_prompt = calculated_df.copy()
    
    # Ensure we have the necessary columns
    required_cols = ['Infrastructure', 'Climate driver', 'Impact model', 
                     'Hazard Index', 'Exposure Index', 'Vulnerability Index', 
                     'PRI scores', 'PRI values']
    
    available_cols = [c for c in required_cols if c in df_prompt.columns]
    df_prompt = df_prompt[available_cols]

    # Convert to Markdown
    pri_table_md = df_prompt.to_markdown(index=False)
    
    system_instruction = (
        "You are a senior infrastructure risk analyst. Your task is to write a formal "
        "'Potential Risk Index (PRI) Assessment Report' based on the provided data table. "
        "You must follow the **Structure**, **Tone**, and **Logic** of the provided EXAMPLE REPORT. "
        "Use the abbreviations HI (Hazard), EI (Exposure), VI (Vulnerability), and PRI (Potential Risk Index)."
    )

    user_prompt = f"""
    ### REFERENCE EXAMPLE (LEARNING MATERIAL)
    
    **1. Example Data Source:**
    {EXAMPLE_PRI_TABLE}

    **2. Example Report Interpretation:**
    {EXAMPLE_PRI_REPORT}

    ---

    ### ACTUAL TASK
    
    **Actual PRI Data Table (to be analyzed):**
    {pri_table_md}

    **INSTRUCTIONS:**
    1. Analyze the 'Actual PRI Data Table' above.
    2. Write a narrative report similar in structure to the Example Report.
    3. **Categorize** the risks: Identify the Highest PRI scores first, then Moderate/Low, then Zero.
    4. **Explain the Drivers:** For the highest risks, explicitly explain *why* the score is high (e.g., "Driven by high Exposure (EI=X) despite moderate Hazard...").
    5. **Conclusion:** Summarize the overall risk landscape and suggest where adaptation focuses might be needed based on high VI or HI scores.
    """

    try:
        response = st.session_state["gemini_client"].models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt],
            config={
                "system_instruction": system_instruction,
                "temperature": 0.3
            }
        )
        return response.text
    except Exception as e:
        return f"Error generating PRI report: {e}"
@st.cache_resource(ttl=3600)
def build_folium_map_object(center, zoom, polygon_data, drawing_key):
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

    folium.raster_layers.TileLayer(
        tiles='https://tiles.arcgis.com/tiles/SDXw0l5jQ3C1QO7x/arcgis/rest/services/Koeppen_Geiger_Climate_Classification_2020/MapServer/tile/{z}/{y}/{x}',
        attr='Köppen-Geiger / Esri',
        name='Köppen-Geiger Climate Classification (Overlay)',
        overlay=True,
        opacity=0.6,
        control=True,
    ).add_to(m)

    draw = folium.plugins.Draw(export=False, draw_options={'polygon': True, 'rectangle': True})
    draw.add_to(m)
    folium.LayerControl().add_to(m)

    if polygon_data:
        folium.GeoJson(polygon_data, name="Drawn Polygon",
                       style_function=polygon_style_function).add_to(m)
    return m

@st.cache_data(ttl=3600)
def geocode_location(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': location_name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'GeneralDecisionSupportTool/1.0'}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        if results:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            return [lat, lon]
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Geocoding error: {e}")
        return None

def reset_polygon():
    st.session_state["last_polygon"] = None
    st.session_state["drawing_key"] += 1
    st.session_state["extract_clicked"] = False
    st.session_state["extracted_data"] = None
    st.rerun()

def get_polygon_coords(geo_json):
    coords = geo_json["geometry"]["coordinates"][0]
    return [(lat, lon) for lon, lat in coords]

def build_query(coords, selected_infras):
    coord_str = " ".join([f"{lat} {lon}" for lat, lon in coords])
    filters = []
    for infra_name in selected_infras:
        tag_filters = infra_options[infra_name]
        for tag_filter in tag_filters:
            filters.append(f'nwr{tag_filter.strip()}(poly:"{coord_str}");')

    query_body = "\n".join(filters)
    return f"[out:json][timeout:90];\n(\n{query_body}\n);\nout body geom;"

def make_overpass_request(query, max_retries=2):
    overpass_url = "https://overpass-api.de/api/interpreter"
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(overpass_url, params={'data': query}, timeout=180)
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                st.error("Overpass API Error: Bad Request (400). Check query syntax.")
                return response
            elif response.status_code == 429:
                st.error("**Overpass API Error: Too Many Requests (429).**")
                return response
            elif response.status_code == 504:
                if attempt < max_retries:
                    time.sleep(5)
                    continue
                else:
                    st.error("⚠️ Overpass API Error: Server timeout (504).")
                    return response
            else:
                st.error(f"⚠️ Overpass API Error: HTTP Status Code {response.status_code}")
                return response
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                time.sleep(5)
                continue
            else:
                st.error("⚠️ Request timeout after multiple attempts")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Network error: {str(e)}")
            return None
    return None

def element_matches_infrastructure(element, infra_keys):
    if 'tags' not in element or not element['tags']:
        return False
    for key in infra_keys:
        if key in element['tags']:
            return True
    return False

def create_detailed_dataframe(elements):
    if not elements:
        return pd.DataFrame()
    data_rows = []
    for element in elements:
        row_data = {'type': element.get('type', ''), 'id': element.get('id', '')}
        if 'tags' in element and element['tags']:
            for tag_key, tag_value in element['tags'].items():
                row_data[f'tag.{tag_key}'] = tag_value
        data_rows.append(row_data)
    return pd.DataFrame(data_rows).fillna('')

def create_radar_chart_plotly(kpis_df: pd.DataFrame, selected_series: list, title: str):
    df = kpis_df.copy()
    if df.columns.size < 2:
        return None
    categories = df.iloc[:, 0].astype(str).tolist()
    fig = go.Figure()
    for col in selected_series:
        if col not in df.columns:
            continue
        vals = pd.to_numeric(df[col], errors="coerce").tolist()
        if len(vals) == 0:
            continue
        vals_loop = vals + [vals[0]]
        cats_loop = categories + [categories[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals_loop, theta=cats_loop, fill="toself", name=col))
    fig.update_layout(polar=dict(radialaxis=dict(
        range=[1, 5], tickvals=[1, 2, 3, 4, 5])), title=title, height=650)
    return fig

def create_risk_heatmap_plotly(df_risk: pd.DataFrame, df_loss: pd.DataFrame, scenario_key: str, kpis: list):
    risk_values = pd.to_numeric(df_risk[scenario_key], errors='coerce')
    loss_values = pd.to_numeric(df_loss[scenario_key], errors='coerce')

    plot_df = pd.DataFrame({
        "Risk Rating (X)": risk_values,
        "Loss Rating (CI)": loss_values,
        "KPI": kpis
    }).dropna()

    plot_df["Severity"] = plot_df["Risk Rating (X)"] * plot_df["Loss Rating (CI)"]

    fig = px.scatter(
        plot_df,
        x="Risk Rating (X)",
        y="Loss Rating (CI)",
        color="Severity",
        text="KPI",
        size=[10] * len(plot_df),
        hover_data=["KPI", "Risk Rating (X)", "Loss Rating (CI)", "Severity"],
        title=f"Consequence Matrix: Scenario {scenario_key}",
        labels={
            "Risk Rating (X)": "Critical Infrastructure Condition Rating (1-5)",
            "Loss Rating (CI)": "Extent of Loss Rating (1-5)"
        },
        color_continuous_scale=px.colors.sequential.Reds,
        range_x=[0.5, 5.5],
        range_y=[0.5, 5.5],
        height=480,
    )

    fig.update_layout(
        xaxis=dict(tickvals=list(range(1, 6)), tickmode='array', showgrid=True, zeroline=False),
        yaxis=dict(tickvals=list(range(1, 6)), tickmode='array', showgrid=True, zeroline=False),
        height=480,
        coloraxis_showscale=False
    )

    grid_x, grid_y = np.meshgrid(np.arange(1, 6), np.arange(1, 6))
    grid_z = grid_x * grid_y

    fig.add_trace(go.Heatmap(
        z=grid_z,
        x=np.arange(1, 6),
        y=np.arange(1, 6),
        colorscale=px.colors.sequential.Reds,
        showscale=False,
        zmin=1,
        zmax=25,
        hoverinfo='skip',
        opacity=0.3,
    ))
    fig.update_traces(selector={'type': 'scatter'}, textposition='top center')
    return fig


if "map_center" not in st.session_state:
    st.session_state["map_center"] = [51.1657, 10.4515]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 6
if "drawing_key" not in st.session_state:
    st.session_state["drawing_key"] = 0
if "last_polygon" not in st.session_state:
    st.session_state["last_polygon"] = None
if "extract_clicked" not in st.session_state:
    st.session_state["extract_clicked"] = False
if "extracted_data" not in st.session_state:
    st.session_state["extracted_data"] = None

initial_data = {scenario_key: {k: 3 for k in kpis} for scenario_key in scenarios}
if "risk_matrix_data" not in st.session_state:
    st.session_state["risk_matrix_data"] = pd.DataFrame(initial_data, index=kpis).to_dict()

initial_loss_data = {scenario_key: {k: 3 for k in kpis} for scenario_key in scenarios}
if "loss_matrix_data" not in st.session_state:
    st.session_state["loss_matrix_data"] = pd.DataFrame(initial_loss_data, index=kpis).to_dict()

if "interpretation_report" not in st.session_state:
    st.session_state["interpretation_report"] = ""

if "hazard_report" not in st.session_state:
    st.session_state["hazard_report"] = ""

try:
    all_lvl2_data = (road_data + railway_data + tunnels_data + bridges_data + 
                green_spaces_data + dams_data + river_data + torrent_data)
    df_lvl2_base = pd.DataFrame(all_lvl2_data)

    for col in df_lvl2_base.columns:
        if df_lvl2_base[col].apply(lambda x: isinstance(x, list)).any():
            df_lvl2_base[col] = df_lvl2_base[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)

    if 'Infrastructure' in df_lvl2_base.columns:
        df_lvl2_base['Infrastructure'] = df_lvl2_base['Infrastructure'].str.strip()
    
    df_lvl2_base = df_lvl2_base.rename(columns={
        'Infraestructure': 'Infrastructure',
        'Effect on the insfrastructure': 'Effect on the infrastructure',
        'Proposed climate indicators': 'Proposed climate Indicator'
    })
except Exception as e:
    st.error(f"Error initializing data: {e}")
    df_lvl2_base = pd.DataFrame()

if 'saved_data' not in st.session_state:
    st.session_state.saved_data = pd.DataFrame(columns=df_lvl2_base.columns)

if 'calculated_results' not in st.session_state:
    st.session_state.calculated_results = pd.DataFrame()

if 'capex_df' not in st.session_state:
    st.session_state.capex_df = pd.DataFrame()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        st.session_state["gemini_client"] = client
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        st.session_state["gemini_client"] = None
else:
    st.warning("⚠️ GEMINI_API_KEY not found. AI report feature disabled. Please set the key.")
    st.session_state["gemini_client"] = None

st.set_page_config(page_title="General Decision Support Tool", layout="wide")

st.markdown("""
<style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 32px !important;  /* Adjust this value for even larger font */
        font-weight: bold !important;
        color: #000000 !important;   /* Black for high contrast; change to #FF0000 for red if needed */
    }
    button[data-baseweb="tab"] {
        padding: 10px 20px !important;  /* Makes tabs physically larger */
        border-bottom: 3px solid transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #FF4B4B !important;  /* Red underline for active tab */
    }
</style>
""", unsafe_allow_html=True)

st.title("General Decision Support Tool")

with st.sidebar:
    st.markdown(f"""
        <a href="https://www.nature-demo.eu" target="_blank">
            <img src="https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png" width="300" />
        </a>
    """, unsafe_allow_html=True)

tab_extraction, tab_lvl1, tab_lvl2 = st.tabs(["**Information Extraction and Mapping**", "**Level 1**", "**Level 2**"])

with tab_extraction:
    st.markdown(
        """
        Use the search box to find a location, then draw a polygon on the map and click **"Extract Information"** below the map.
        """
    )

    st.header("Select Infrastructure Types")
    cols = st.columns(4)
    checkbox_states = {}
    all_infra_keys = list(infra_options.keys())

    for i, infra_name in enumerate(all_infra_keys):
        col_index = i % 4
        with cols[col_index]:
            if f"check_{infra_name}" not in st.session_state:
                default_state = infra_name in ["Buildings", "Roads", "Water"]
                st.session_state[f"check_{infra_name}"] = default_state

            checkbox_states[infra_name] = st.checkbox(
                infra_name,
                value=st.session_state[f"check_{infra_name}"],
                key=f"check_{infra_name}"
            )

    selected_infras = [
        k for k, is_selected in checkbox_states.items() if is_selected]
    if len(selected_infras) > 5:
        st.warning(
            "⚠️ Selecting many infrastructure types may cause timeouts for large areas.")
    st.markdown("---")

    st.header("Search Location and Draw Polygon")
    search_col, _ = st.columns([3, 1])

    with search_col:
        location_name = st.text_input(
            "Search for a location to center the map:", value="Berlin, Germany")
        if st.button("Go to Location"):
            with st.spinner(f"Geocoding '{location_name}'..."):
                coords = geocode_location(location_name)
                if coords:
                    st.session_state["map_center"] = coords
                    st.session_state["map_zoom"] = 12
                    st.session_state["drawing_key"] += 1
                    st.success(
                        f"Map centered on {location_name}. Now draw a polygon.")
                else:
                    st.error(
                        f"Could not find coordinates for '{location_name}'.")

    map_object = build_folium_map_object(
        st.session_state["map_center"],
        st.session_state["map_zoom"],
        st.session_state["last_polygon"],
        st.session_state["drawing_key"]
    )

    output = st_folium(
        map_object,
        height=600,
        width=1200,
        key=st.session_state["drawing_key"]
    )

    if output and output.get("last_active_drawing") and output["last_active_drawing"].get("geometry"):
        if output["last_active_drawing"].get("geometry").get("type") in ["Polygon", "Rectangle"]:
            if st.session_state["last_polygon"] != output["last_active_drawing"]:
                st.session_state["last_polygon"] = output["last_active_drawing"]
                st.session_state["extract_clicked"] = False
        elif output["last_active_drawing"].get("geometry").get("coordinates") is None:
            st.session_state["last_polygon"] = None

    st.markdown("---")
    button_col, reset_col, _ = st.columns([2, 1, 3])

    with button_col:
        if st.button("Extract Information", type="primary", key="extract_btn", help="Trigger data extraction and AI report generation."):
            if st.session_state["last_polygon"] is None:
                st.error("Please draw a polygon on the map first.")
            else:
                st.session_state["extract_clicked"] = True
                st.session_state["extracted_data"] = None
                st.rerun()

    with reset_col:
        if st.button("Reset Polygon", help="Clear the current drawn polygon.", key="reset_poly_btn"):
            reset_polygon()

    if st.session_state["extract_clicked"]:

        if st.session_state["extracted_data"] is None:

            geo_json = st.session_state["last_polygon"]

            try:
                coords = get_polygon_coords(geo_json)
                polygon = Polygon(coords)
                area_sq_km = polygon.area * (111**2)

                center_lat = sum(c[0] for c in coords) / len(coords)
                center_lon = sum(c[1] for c in coords) / len(coords)

                query = build_query(coords, selected_infras)
                with st.spinner("Retrieving data from OpenStreetMap..."):
                    response = make_overpass_request(query)
                    if response is None or response.status_code != 200:
                        st.session_state["extract_clicked"] = False
                        st.stop()
                    data = response.json()
                elements = data.get("elements", [])

                if not elements:
                    st.warning(
                        "No data found in the selected area for the chosen types.")

                with st.spinner("Analyzing climate map data..."):
                    _, center_koppen_code = generate_koppen_map_plot(
                        center_lat, center_lon)

                context_report = ""
                if st.session_state.get("gemini_client"):
                    with st.spinner(f"Generating Geographical & Infrastructure Report (Internet Search)..."):
                        context_report = generate_context_report(
                            center_lat, center_lon, area_sq_km, elements)

                koppen_report = ""
                if st.session_state.get("gemini_client"):
                    with st.spinner(f"Generating Köppen Interpretation Report for code {center_koppen_code} (Internet Search)..."):
                        koppen_report = generate_koppen_interpretation(
                            center_koppen_code)

                st.session_state["extracted_data"] = {
                    "elements": elements, "coords": coords, "area_sq_km": area_sq_km,
                    "context_report": context_report,
                    "koppen_report": koppen_report,
                    "koppen_code": center_koppen_code,
                    "center_lat": center_lat, "center_lon": center_lon
                }

            except Exception as e:
                st.error(
                    f"⚠️ An unexpected error occurred during extraction: {str(e)}")
                st.code(traceback.format_exc())
                st.session_state["extract_clicked"] = False
                st.stop()

        if st.session_state["extracted_data"]:
            elements = st.session_state["extracted_data"].get("elements", [])
            area_sq_km = st.session_state["extracted_data"].get(
                "area_sq_km", 0)
            context_report = st.session_state["extracted_data"].get(
                "context_report", "")
            koppen_report = st.session_state["extracted_data"].get(
                "koppen_report", "")
            center_lat = st.session_state["extracted_data"].get("center_lat")
            center_lon = st.session_state["extracted_data"].get("center_lon")

            if st.session_state["extracted_data"].get("elements"):
                st.success(
                    f"Successfully processed {len(elements)} OSM items (Area: {area_sq_km:.4f} km²)")

            st.markdown("---")
            st.subheader("Geographical & Infrastructure Context Report")
            if context_report:
                st.markdown(context_report)
            else:
                st.warning(
                    "The Geographical & Infrastructure Report failed to generate or the AI feature is disabled.")

            st.markdown("---")
            st.subheader("Köppen-Geiger Climate Classification Map (Visual)")

            if center_lat is not None and center_lon is not None:
                plot_result, _ = generate_koppen_map_plot(
                    center_lat, center_lon)

                if isinstance(plot_result, str):
                    st.error(plot_result)
                else:
                    st.pyplot(plot_result)
            else:
                st.warning(
                    "Cannot display Köppen map: Center coordinates for the drawn polygon could not be determined.")

            st.markdown("---")
            st.subheader("Climate Interpretation Report")
            if koppen_report:
                st.markdown(koppen_report)
            else:
                st.warning(
                    "The Climate Interpretation Report failed to generate or the AI feature is disabled.")

            with st.expander("View Extracted Infrastructure Data Tables (OpenStreetMap Raw Data)"):
                st.subheader("Detailed Infrastructure Data Tables")
                has_data_for_any_infra = False

                for infra in selected_infras:
                    keys_to_check = set()
                    for filter_str in infra_options[infra]:
                        key_match = re.search(r'\["(.+?)"', filter_str)
                        if key_match:
                            keys_to_check.add(key_match.group(1))

                    infra_elements = [
                        element for element in elements
                        if element_matches_infrastructure(element, keys_to_check)
                    ]

                    if infra_elements:
                        has_data_for_any_infra = True
                        infra_df = create_detailed_dataframe(infra_elements)
                        st.subheader(
                            f"{infra} ({len(infra_elements)} infrastructure items)")
                        st.dataframe(infra_df[[col for col in infra_df.columns if not col.startswith(
                            'geometry')]].head(15), width=1200)

                if not has_data_for_any_infra:
                    st.info(
                        "No detailed data to display for the selected infrastructure types.")


with tab_lvl1:

    st.header("Perceived Risks Assessment")

    df_data = st.session_state["risk_matrix_data"]
    df = pd.DataFrame(df_data, index=kpis)
    df.index.name = "KPI / Indicator"

    st.subheader("Input Ratings: Risk and Loss")
    st.info("Please provide integers between **1 (best/lowest)** and **5 (worst/highest)** for each cell.")

    matrix_tab, scenario_key_tab = st.tabs(
        ["Input Matrices (1-5)", "Scenario & KPI Definitions"])

    with scenario_key_tab:
        st.markdown("### Key Performance Indicators (KPIs)")
        st.markdown("""
        These indicators cover various dimensions of risk and resilience:
        * **SRS:** Safety, Reliability, and Security.
        * **AM:** Availability and Maintainability.
        * **EC:** Economy (cost, efficiency).
        * **EV:** Environment (environmental impact, sustainability).
        * **HP:** Health and Politics (public health, political stability).
        """)

        st.markdown("### Scenario Definitions")
        for abbr, desc in scenarios.items():
            html_abbr = abbr.replace("CI_HNG", "CI<sub>HNG</sub>").replace("CI_HN", "CI<sub>HN</sub>").replace(
                "CI_HG", "CI<sub>HG</sub>").replace("CI_H", "CI<sub>H</sub>").replace("CI", "CI")
            st.markdown(f"**{html_abbr}** ({desc})", unsafe_allow_html=True)

    with matrix_tab:

        column_config = {
            "KPI / Indicator": st.column_config.TextColumn(
                "KPI / Indicator",
                disabled=True
            )
        }

        for key, desc in scenarios.items():
            column_config[key] = st.column_config.NumberColumn(
                label=key,
                help=desc,
                min_value=1,
                max_value=5,
                default=3,
                format="%d",
                width="small"
            )

        st.markdown("### 1. Risk Rating (Critical infrastructure Condition)")
        
        with st.form("risk_rating_form"):
            risk_edited_df = st.data_editor(
                df,
                column_config=column_config,
                num_rows="fixed",
                key="risk_matrix_editor_widget"
            )
            submit_risk = st.form_submit_button("Save Risk Ratings")
        
        if submit_risk:
            st.session_state["risk_matrix_data"] = risk_edited_df.to_dict()
            st.rerun()

        st.markdown("### 2. Extent of Loss Rating (CI)")
        
        df_loss_data = st.session_state["loss_matrix_data"]
        df_loss = pd.DataFrame(df_loss_data, index=kpis)
        df_loss.index.name = "KPI / Indicator"

        loss_display_columns = [col for col in df_loss.columns if col != 'CI']
        df_loss_display = df_loss[loss_display_columns]

        column_config_loss = column_config.copy()
        if 'CI' in column_config_loss:
            del column_config_loss['CI']

        with st.form("loss_rating_form"):
            loss_edited_df_display = st.data_editor(
                df_loss_display,
                column_config=column_config_loss,
                num_rows="fixed",
                key="loss_matrix_editor_widget"
            )
            submit_loss = st.form_submit_button("Save Loss Ratings")

        if submit_loss:
            if 'CI' in df_loss.columns:
                ci_column_original = df_loss['CI'].copy()
                reconstructed_df_loss = loss_edited_df_display.assign(
                    CI=ci_column_original)
                st.session_state["loss_matrix_data"] = reconstructed_df_loss.to_dict()
            else:
                st.session_state["loss_matrix_data"] = loss_edited_df_display.to_dict()
            st.rerun()

        st.markdown("---")
        st.subheader("Radar Plot of Input Risks")
        
        df_risk_current = pd.DataFrame(st.session_state["risk_matrix_data"], index=kpis)
        
        try:
            kpis_for_plot = df_risk_current.reset_index()
        except Exception:
            kpis_for_plot = pd.DataFrame(df_risk_current).reset_index()

        available_series = kpis_for_plot.columns[1:].tolist()

        if not available_series:
            st.info(
                "No scenario columns available to plot. Please configure the risk matrix columns.")
        else:
            st.markdown("Select scenarios to include in the radar plot:")
            cols_radar = st.columns(len(available_series))
            selected_series = []
            for i, s in enumerate(available_series):
                with cols_radar[i]:
                    checked = st.checkbox(
                        s, value=True, key=f"radar_checkbox_{s}")
                    if checked:
                        selected_series.append(s)

            if not selected_series:
                st.warning(
                    "Please select at least one scenario/column to plot.")
            else:
                try:
                    radar_fig = create_radar_chart_plotly(
                        kpis_for_plot, selected_series, title="Risk Radar - Risk Ratings (X)")
                    if radar_fig is None:
                        st.error(
                            "Unable to generate radar figure. Check your input format.")
                    else:
                        st.plotly_chart(radar_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to create radar plot: {e}")
                    st.exception(e)

        st.markdown("---")
        st.subheader("Consequence Assessment Matrices (Risk vs. Loss)")
        st.caption(
            "Each plot compares the Risk Rating (X) and Loss Rating (CI) for the selected scenario across all 5 KPIs.")

        scenarios_to_plot = ["CI_H", "CI_HG", "CI_HN", "CI_HNG"]
        plot_cols = st.columns(2)

        all_risk_values_flat = pd.DataFrame(
            st.session_state["risk_matrix_data"]).values.flatten()
        risk_values_series = pd.Series(pd.to_numeric(
            all_risk_values_flat, errors='coerce'))
        valid_risk_input = all(risk_values_series.between(
            1, 5, inclusive='both').fillna(False))

        all_loss_values_flat = pd.DataFrame(
            st.session_state["loss_matrix_data"]).values.flatten()
        loss_values_series = pd.Series(pd.to_numeric(
            all_loss_values_flat, errors='coerce'))
        valid_loss_input = all(loss_values_series.between(
            1, 5, inclusive='both').fillna(False))

        if not valid_risk_input or not valid_loss_input:
            st.warning(
                "Please ensure all cells in both tables contain valid integers between 1 and 5 to generate the matrix plots.")
        else:

            df_for_plot_loss = pd.DataFrame(
                st.session_state["loss_matrix_data"], index=kpis)
            
            df_for_plot_risk = pd.DataFrame(
                st.session_state["risk_matrix_data"], index=kpis)

            for i, scenario in enumerate(scenarios_to_plot):
                try:
                    fig = create_risk_heatmap_plotly(
                        df_for_plot_risk, df_for_plot_loss, scenario, kpis)
                    with plot_cols[i % 2]:
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    with plot_cols[i % 2]:
                        st.error(
                            f"Failed to generate plot for scenario {scenario}: {e}")

        st.markdown("---")
        with st.expander("Interpretation"):

            if st.session_state.get("gemini_client"):

                if st.button("Generate Interpretation Report", type="primary", help="Analyze the current risk matrix using Gemini with contextual search."):

                    if not 'risk_matrix_data' in st.session_state:
                        st.error(
                            "Please populate the Risk Matrix table first before generating an interpretation.")
                        st.stop()

                    try:
                        current_df = pd.DataFrame(
                            st.session_state["risk_matrix_data"], index=kpis)
                    except (KeyError, ValueError) as e:
                        st.error(
                            f"Error reading risk matrix data: {e}. Ensure 'kpis' and 'risk_matrix_data' are correctly structured.")
                        current_df = None

                    if current_df is not None:
                        with st.spinner("Generating Risk Matrix Interpretation (Gemini with Google Search)..."):
                            interpretation_report = generate_risk_interpretation(
                                current_df, kpis, scenarios)

                        st.session_state["interpretation_report"] = interpretation_report

                        st.subheader("Risk Matrix Interpretation Report")
                        if interpretation_report:
                            st.markdown(interpretation_report)
                        else:
                            st.warning(
                                "The Risk Matrix Interpretation Report failed to generate.")

                if st.session_state["interpretation_report"]:
                    st.subheader("Risk Matrix Interpretation Report")
                    st.markdown(st.session_state["interpretation_report"])
                else:
                    st.info(
                        "Click the button above to generate the AI interpretation report based on the current matrix data.")

            else:
                st.warning(
                    "Gemini client not initialized. AI interpretation feature disabled. Ensure GEMINI_API_KEY is available.")


with tab_lvl2:
    st.header('Infrastructure Impact & Hazard Analysis 🌍')

    infrastructure_col = 'Infrastructure'
    climate_driver_col = 'Climate driver'
    type_impact_col = 'Type of impact'
    impact_model_col = 'Impact model'
    dictionary_key_col = 'Dictionary Key'

    st.subheader("1. Filter Impact Models")
    col_f1, col_f2, col_f3 = st.columns(3)

    if df_lvl2_base.empty:
        st.warning("No infrastructure definitions found.")
    else:
        with col_f1:
            unique_infrastructures = sorted(df_lvl2_base[infrastructure_col].unique().tolist())
            selected_infrastructures = st.multiselect('Infrastructure', unique_infrastructures)
            df_filtered_infra = df_lvl2_base[df_lvl2_base[infrastructure_col].isin(selected_infrastructures)] if selected_infrastructures else df_lvl2_base

        with col_f2:
            unique_climate_drivers = sorted(df_filtered_infra[climate_driver_col].unique().tolist())
            selected_climate_drivers = st.multiselect('Climate Driver', unique_climate_drivers)
            df_filtered_driver = df_filtered_infra[df_filtered_infra[climate_driver_col].isin(selected_climate_drivers)] if selected_climate_drivers else df_filtered_infra

        with col_f3:
            unique_types = sorted(df_filtered_driver[type_impact_col].unique().tolist())
            selected_types = st.multiselect('Type of Impact', unique_types)
            final_filtered_df = df_filtered_driver[df_filtered_driver[type_impact_col].isin(selected_types)] if selected_types else df_filtered_driver

        if st.button("Add filtered items to Table", type="primary"):
            if not final_filtered_df.empty:
                st.session_state.saved_data = pd.concat(
                    [st.session_state.saved_data, final_filtered_df], 
                    ignore_index=True
                ).drop_duplicates()
                st.success(f"Added {len(final_filtered_df)} items.")
            else:
                st.warning("No items found to add.")

    st.divider()
    st.subheader("2. Selected Impact Models Table")
    if not st.session_state.saved_data.empty:
        # Action buttons for the table
        btn_col1, btn_col2, _ = st.columns([1, 1, 4])
        
        with btn_col1:
            if st.button("Reset Table", help="Clear all selected impact models and results", type="secondary"):
                st.session_state.saved_data = pd.DataFrame(columns=df_lvl2_base.columns)
                st.session_state.calculated_results = pd.DataFrame()
                st.session_state.capex_df = pd.DataFrame()
                st.rerun()

        cols_to_display = [impact_model_col, infrastructure_col, dictionary_key_col]
        st.session_state.saved_data = st.session_state.saved_data.reset_index(drop=True)

        selection_event = st.dataframe(
            st.session_state.saved_data[cols_to_display],
            on_select="rerun",
            selection_mode="multi-row",
            use_container_width=True,
            key="impact_table_selection"
        )

        with btn_col2:
            if st.button("Remove Selected Rows"):
                selected_indices = selection_event.selection.rows
                if selected_indices:
                    st.session_state.saved_data = st.session_state.saved_data.drop(selected_indices).reset_index(drop=True)
                    st.rerun()
                else:
                    st.warning("Select rows to remove.")
    else:
        st.info("Table is empty. Use filters above to add items.")

    st.divider()
    st.subheader("3. Hazard Variation Analysis")

    URL = "https://naturedemo-clima-ind.dic-cloudmate.eu/api/calculate"

    LEVEL_TO_INDEX = {
        "No variation": 0, "Low": 1, "Medium": 2, "High": 3, "Very High": 4, "Extreme": 5
    }
    INDEX_TO_LEVEL = {v: k for k, v in LEVEL_TO_INDEX.items()}

    has_extracted_coords = (
        st.session_state.get("extracted_data") is not None 
        and st.session_state["extracted_data"].get("center_lat") is not None
    )

    use_poly_center = st.checkbox(
        "Use Polygon Center Coordinates", 
        value=has_extracted_coords, 
        disabled=not has_extracted_coords,
        help="If checked, uses the center of the polygon drawn in the Information Extraction and Mapping tab."
    )

    if use_poly_center and has_extracted_coords:
        default_lat = st.session_state["extracted_data"]["center_lat"]
        default_lon = st.session_state["extracted_data"]["center_lon"]
        input_disabled = True 
    else:
        default_lat = st.session_state["map_center"][0] if st.session_state["map_center"] else 50.7764
        default_lon = st.session_state["map_center"][1] if st.session_state["map_center"] else 6.0839
        input_disabled = False

    row1_c1, row1_c2 = st.columns(2)
    
    with row1_c1:
        lat = st.number_input("Latitude:", value=float(default_lat), format="%.4f", disabled=input_disabled)
        
    with row1_c2:
        selected_scenario_label = st.radio("Select Scenario:", ("RCP4.5", "RCP8.5"), horizontal=True)

    row2_c1, row2_c2 = st.columns(2)
    
    with row2_c1:
        lon = st.number_input("Longitude:", value=float(default_lon), format="%.4f", disabled=input_disabled)
        
    with row2_c2:
        selected_term_label = st.radio("Select Time Horizon:", ("Short Term", "Medium Term", "Long Term"), horizontal=True)

    st.markdown(" ")
    if st.button("Calculate Hazard Variation & Level", type="primary", use_container_width=True):
        if st.session_state.saved_data.empty:
            st.error("Please add items to the table first.")
        else:
            scenario_map = {"RCP4.5": "rcp45", "RCP8.5": "rcp85"}
            term_map = {"Short Term": "short", "Medium Term": "medium", "Long Term": "long"}

            api_scenario = scenario_map[selected_scenario_label]
            api_term = term_map[selected_term_label]

            index_list = []
            level_list = []
            progress_bar = st.progress(0)
            total_rows = len(st.session_state.saved_data)
            
            for index, row in st.session_state.saved_data.iterrows():
                dict_key = row.get(dictionary_key_col)
                final_idx = 0
                final_lvl = "No variation"

                if dict_key and dict_key != "Not found":
                    val_selected = None
                    val_historical = None
                    
                    try:
                        payload_sel = {"index_type": dict_key, "scenario": api_scenario, "lat": lat, "lon": lon}
                        resp_sel = requests.post(URL, json=payload_sel, timeout=10)
                        if resp_sel.status_code == 200 and resp_sel.json().get('status') == 'success':
                            val_selected = resp_sel.json().get('results', {}).get(api_term, {}).get('value')

                        payload_hist = {"index_type": dict_key, "scenario": "historical", "lat": lat, "lon": lon}
                        resp_hist = requests.post(URL, json=payload_hist, timeout=10)
                        if resp_hist.status_code == 200 and resp_hist.json().get('status') == 'success':
                            val_historical = resp_hist.json().get('results', {}).get('historical', {}).get('value')
                    except:
                        pass

                    if val_selected is not None and val_historical is not None:
                        try:
                            if val_historical == 0:
                                variation_val = 0.0 if val_selected == 0 else float('inf')
                            else:
                                variation_val = abs((val_selected - val_historical) / val_historical) * 100
                            
                            if variation_val == 0: final_idx, final_lvl = 0, "No variation"
                            elif variation_val == float('inf') or variation_val > 75: final_idx, final_lvl = 5, "Extreme"
                            elif variation_val <= 10: final_idx, final_lvl = 1, "Low"
                            elif variation_val <= 25: final_idx, final_lvl = 2, "Medium"
                            elif variation_val <= 50: final_idx, final_lvl = 3, "High"
                            elif variation_val <= 75: final_idx, final_lvl = 4, "Very High"
                        except:
                            pass
                
                index_list.append(final_idx)
                level_list.append(final_lvl)
                progress_bar.progress((index + 1) / total_rows)

            result_df = st.session_state.saved_data[[infrastructure_col, climate_driver_col, impact_model_col]].copy()
            
            result_df["Hazard Index"] = index_list
            result_df["Hazard Level"] = level_list
            st.session_state.calculated_results = result_df
            st.success("Calculation complete!")
            st.rerun()

    if not st.session_state.calculated_results.empty:
        st.subheader("Natural Hazards Table")
        if st.button("Delete rows without climate information", type="primary", help="Permanently remove rows where Hazard Index is 0 or N/A from the dataset."):
            before_count = len(st.session_state.calculated_results)
            st.session_state.calculated_results = st.session_state.calculated_results[
                (st.session_state.calculated_results["Hazard Index"] != 0) & 
                (st.session_state.calculated_results["Hazard Index"].notna())
            ].reset_index(drop=True)
            
            after_count = len(st.session_state.calculated_results)
            st.toast(f"Deleted {before_count - after_count} rows.", icon="🗑️")
            st.rerun()

        display_df = st.session_state.calculated_results.copy()
        column_config = {
            "Hazard Index": st.column_config.NumberColumn(
                "Hazard Index", min_value=1, max_value=5, step=1, required=True
            ),
            "Hazard Level": st.column_config.SelectboxColumn(
                "Hazard Level", options=["No variation", "Low", "Medium", "High", "Very High", "Extreme"], required=True
            ),
            infrastructure_col: st.column_config.TextColumn(disabled=True),
            climate_driver_col: st.column_config.TextColumn(disabled=True),
            impact_model_col: st.column_config.TextColumn(disabled=True),
            
            "Sensitivity Index": None,
            "Exposure Index": None,
            "Vulnerability Index": None,
            "Asset": None,
            "PRI scores": None,
            "PRI values": None
        }

        temp_hazard_df = st.data_editor(
            display_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="hazard_editor"
        )

        if st.button("Save Hazard Changes", type="primary"):
            updated = False
            
            for i in temp_hazard_df.index:
                old_level = display_df.loc[i, "Hazard Level"]
                new_level = temp_hazard_df.loc[i, "Hazard Level"]
                old_index = display_df.loc[i, "Hazard Index"]
                new_index = temp_hazard_df.loc[i, "Hazard Index"]

                if new_level != old_level:
                    temp_hazard_df.at[i, "Hazard Index"] = LEVEL_TO_INDEX.get(new_level, 0)
                    updated = True
                elif new_index != old_index:
                    temp_hazard_df.at[i, "Hazard Level"] = INDEX_TO_LEVEL.get(new_index, "Low")
                    updated = True
                    
            if temp_hazard_df["Hazard Index"].max() > 5 or temp_hazard_df["Hazard Index"].min() < 0:
                 st.error("Error: Hazard Index values must be between 0 and 5.")
            else:
                st.session_state.calculated_results.update(temp_hazard_df)
                st.success("Values saved successfully!")
                st.rerun()

        st.markdown(
            """
            <span style='font-size: 20px; font-weight: bold;'>
                💡Tips: Values of the 'Hazard Level' and 'Hazard Index' columns are editable. 
                Click 'Save Hazard Changes' to apply updates.
            </span>
            """,
            unsafe_allow_html=True
        )

        # --- GEMINI REPORT BUTTON ---
        if st.button("Generate Climate Hazard Report", type="secondary", use_container_width=True, help="Analyze the generated hazard table using Gemini."):
            with st.spinner("Generating Report from Hazard Table (Gemini)..."):
                report_text = generate_hazard_report_gemini(st.session_state.calculated_results)
                st.session_state["hazard_report"] = report_text

        if st.session_state["hazard_report"]:
            with st.expander("View Climate Hazard Report", expanded=True):
                st.markdown(st.session_state["hazard_report"])

    st.divider()
    st.subheader("4. Exposure Index Analysis")

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        economic_available = st.checkbox("Economic data for infrastructure assets are available", value=False)
    with col_exp2:
        use_default_thresholds = st.checkbox("Use default threshold values for OPEX and Revenue", value=True)

    if 'capex_df' not in st.session_state or st.button("Refresh Asset List"):
        if not st.session_state.calculated_results.empty:
            if 'Asset' not in st.session_state.calculated_results.columns:
                try:
                    st.session_state.calculated_results['Asset'] = st.session_state.saved_data.loc[st.session_state.calculated_results.index, 'Asset']
                except:
                    pass

            if 'Asset' in st.session_state.calculated_results.columns:
                unique_assets = st.session_state.calculated_results['Asset'].unique()
            else:
                unique_assets = st.session_state.saved_data['Asset'].unique()
                
            st.session_state.capex_df = pd.DataFrame({
                "Exposed assets": unique_assets,
                "CAPEX (M€/year)": 0.0
            })

    exposure_val = 3 

    if economic_available:
        revenue_input = st.number_input("REVENUES (M€/year)", min_value=0.0, value=0.0, step=0.1)
        
        st.write("Enter CAPEX for each asset:")
        if not st.session_state.capex_df.empty:
            edited_capex = st.data_editor(
                st.session_state.capex_df,
                use_container_width=True,
                hide_index=True,
                key="capex_editor"
            )
        else:
            st.warning("No assets found. Run hazards calculation first.")
            edited_capex = pd.DataFrame()
        
        if not use_default_thresholds:
            st.info("Define your custom threshold boundaries:")
            ct1, ct2, ct3, ct4 = st.columns(4)
            with ct1: rev_low = st.number_input("Revenue Low Threshold", value=1.0)
            with ct2: rev_high = st.number_input("Revenue High Threshold", value=2.5)
            with ct3: cap_low = st.number_input("CAPEX Low Threshold", value=5.0)
            with ct4: cap_high = st.number_input("CAPEX High Threshold", value=10.0)

            # --- DYNAMIC EXPOSURE MATRIX TABLE ---
            colors = {1: "#6dbf7a", 2: "#a6d17b", 3: "#ffeb84", 4: "#f9a674", 5: "#f76d6d"}
            html_table = f"""
            <style>
                .exp-table {{ width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; border: 1px solid #000; }}
                .exp-table th, .exp-table td {{ border: 1px solid #444; padding: 12px; font-weight: bold; }}
                .header-dark {{ background-color: #2e4d23; color: white; }}
                .header-light {{ background-color: #ffffff; color: black; }}
            </style>
            <table class="exp-table">
                <tr>
                    <th rowspan="2" colspan="2" class="header-dark">Exposure Index thresholds</th>
                    <th colspan="3" class="header-dark">Assets CAPEX (M€/year)</th>
                </tr>
                <tr>
                    <th class="header-light">< {cap_low}</th>
                    <th class="header-light">{cap_low} - {cap_high}</th>
                    <th class="header-light">> {cap_high}</th>
                </tr>
                <tr>
                    <td rowspan="3" class="header-dark" style="width: 20%;">Annual revenues (M€/year)</td>
                    <td class="header-light">< {rev_low}</td>
                    <td style="background-color: {colors[1]};">1</td>
                    <td style="background-color: {colors[2]};">2</td>
                    <td style="background-color: {colors[3]};">3</td>
                </tr>
                <tr>
                    <td class="header-light">{rev_low} - {rev_high}</td>
                    <td style="background-color: {colors[2]};">2</td>
                    <td style="background-color: {colors[3]};">3</td>
                    <td style="background-color: {colors[4]};">4</td>
                </tr>
                <tr>
                    <td class="header-light">> {rev_high}</td>
                    <td style="background-color: {colors[3]};">3</td>
                    <td style="background-color: {colors[4]};">4</td>
                    <td style="background-color: {colors[5]};">5</td>
                </tr>
            </table>
            """
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            rev_low, rev_high, cap_low, cap_high = 1.0, 2.5, 5.0, 10.0

    if st.button("Calculate Exposure Indexes"):
        if economic_available and not edited_capex.empty:
            total_capex = edited_capex["CAPEX (M€/year)"].sum()
            exposure_val = calculate_exposure(revenue_input, total_capex, rev_low, rev_high, cap_low, cap_high)
            st.session_state.capex_df = edited_capex 
        else:
            exposure_val = 3
        
        if not st.session_state.calculated_results.empty:
            st.session_state.calculated_results["Exposure Index"] = exposure_val
            st.success(f"Exposure Index calculated: {exposure_val}")
        else:
            st.error("No impact models available to update.")

    if not st.session_state.calculated_results.empty and "Exposure Index" in st.session_state.calculated_results.columns:
        st.write("### Exposure Results")
        
        exp_col_config = {
             "Sensitivity Index": None,
             "Vulnerability Index": None,
             "Asset": None,
             "PRI scores": None,
             "PRI values": None,
             "Hazard Index": None,
             "Hazard Level": None
        }
        st.dataframe(
            st.session_state.calculated_results, 
            column_config=exp_col_config,
            use_container_width=True
        )

    st.divider()
    st.subheader("5. Vulnerability Index Analysis")

    if not st.session_state.calculated_results.empty:
        
        if 'Asset' not in st.session_state.calculated_results.columns:
            try:
                st.session_state.calculated_results['Asset'] = st.session_state.saved_data.loc[st.session_state.calculated_results.index, 'Asset']
            except Exception as e:
                st.error(f"Error aligning asset data: {e}. Please try resetting the table.")

        if 'Sensitivity Index' not in st.session_state.calculated_results.columns:
            st.session_state.calculated_results['Sensitivity Index'] = 3

        st.markdown("#### Step 5.1: Define Sensitivity Index")
        st.info("Edit the **Sensitivity Index** column (1-5) below. Changes are applied when you click 'Calculate'.")

        vuln_input_df = st.session_state.calculated_results.copy()

        vuln_col_config = {
            "Sensitivity Index": st.column_config.NumberColumn(
                "Sensitivity Index", min_value=1, max_value=5, step=1, required=True
            ),
            
            "Exposure Index": None,
            "Vulnerability Index": None, 
            "PRI scores": None,
            "PRI values": None,
            
            "Hazard Index": None,
            "Hazard Level": None,
            
            "Infrastructure": st.column_config.TextColumn(disabled=True),
            "Climate driver": st.column_config.TextColumn(disabled=True),
            "Impact model": st.column_config.TextColumn(disabled=True),
            "Asset": st.column_config.TextColumn(disabled=True),
        }

        temp_edited_df = st.data_editor(
            vuln_input_df,
            column_config=vuln_col_config,
            use_container_width=True,
            hide_index=True,
            key="sensitivity_editor_v2" 
        )

        st.markdown("#### Step 5.2: Adaptive Capacity Configuration")
        
        ac_available = st.checkbox("Adaptive capacity of the assets available?")
        
        asset_ac_params = {}
        unique_assets_list = st.session_state.calculated_results['Asset'].unique()

        if ac_available:
            st.write("Please configure the Adaptive Capacity parameters for each asset:")
            for asset in unique_assets_list:
                with st.expander(f"{asset}", expanded=False):
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        ac0 = st.number_input(
                            f"Initial Adaptive Capacity (AC0) for {asset}",
                            min_value=0.0, max_value=0.4, value=0.0, step=0.01,
                            help="Maximum value is 0.4",
                            key=f"ac0_{asset}"
                        )
                    
                    with c2:
                        lf_label = st.radio(
                            f"Lifetime of {asset}",
                            options=["Greenfield", "Intermediate", "High (> 25 years)"],
                            index=1,
                            key=f"lf_{asset}"
                        )
                        if lf_label == "Greenfield": lf_val = 10
                        elif lf_label == "High (> 25 years)": lf_val = -10
                        else: lf_val = 0
                    
                    c3, c4 = st.columns(2)
                    
                    with c3:
                        lm_label = st.radio(
                            f"Level of maintenance for {asset}",
                            options=["High", "Medium", "Low"],
                            index=1,
                            key=f"lm_{asset}"
                        )
                        if lm_label == "High": lm_val = 10
                        elif lm_label == "Low": lm_val = -10
                        else: lm_val = 0

                    with c4:
                        dt_label = st.radio(
                            f"Design topology for {asset}",
                            options=["Resilient", "Acceptable", "Not acceptable"],
                            index=1,
                            key=f"dt_{asset}"
                        )
                        if dt_label == "Resilient": dt_val = 10
                        elif dt_label == "Not acceptable": dt_val = -10
                        else: dt_val = 0
                    
                    asset_ac_params[asset] = {"AC0": ac0, "lf": lf_val, "lm": lm_val, "dt": dt_val}

        if st.button("Calculate Vulnerability Index", type="primary"):
            
            st.session_state.calculated_results['Sensitivity Index'] = temp_edited_df['Sensitivity Index']

            vulnerability_results = []
            
            for index, row in st.session_state.calculated_results.iterrows():
                asset_name = row['Asset']
                sensitivity_val = row['Sensitivity Index']
                
                final_ac = 0.0
                
                if ac_available and asset_name in asset_ac_params:
                    params = asset_ac_params[asset_name]
                    calculated_ac = params["AC0"] + ((params["lf"] + params["lm"] + params["dt"]) / 100.0)
                    final_ac = min(calculated_ac, 0.4)
                    final_ac = max(final_ac, 0.0) 
                
                vuln_index = sensitivity_val * (1 - final_ac)
                vulnerability_results.append(vuln_index)
                
            st.session_state.calculated_results['Vulnerability Index'] = vulnerability_results
            
            st.success("Vulnerability Index calculated successfully!")
            
            st.subheader("Vulnerability Results")
            
            final_col_config = {
                 "Sensitivity Index": None,
                 "Exposure Index": None,
                 "PRI scores": None,
                 "PRI values": None,
                 "Asset": None,
                 "Hazard Index": None,
                 "Hazard Level": None
            }
            
            st.dataframe(
                st.session_state.calculated_results,
                column_config=final_col_config,
                use_container_width=True
            )

    else:
        st.warning("Please complete the previous sections (Filters -> Hazards -> Exposure) to generate the data for analysis.")

    st.divider()
    st.subheader("6. Potential Risk Index")

    if st.button("Calculate the Potential Risk Index (PRI)"):
        if 'calculated_results' in st.session_state and not st.session_state.calculated_results.empty:
            df_pri = st.session_state.calculated_results.copy()
            
            hazard_col = 'Hazard Index'
            exposure_col = 'Exposure Index'
            vulnerability_col = 'Vulnerability Index'
            
            required_cols = [hazard_col, exposure_col, vulnerability_col]
            
            if all(col in df_pri.columns for col in required_cols):
                pri_scores = []
                pri_values = []
                
                pri_table = {
                    0: {'score': 0, 'value': 'NO RISK'},
                    25: {'score': 1, 'value': 'VERY LOW'},
                    50: {'score': 2, 'value': 'LOW'},
                    75: {'score': 3, 'value': 'MEDIUM'},
                    100: {'score': 4, 'value': 'HIGH'},
                    125: {'score': 5, 'value': 'EXTREME'}
                }
                allowed_levels = list(pri_table.keys()) 

                for index, row in df_pri.iterrows():
                    try:
                        h = float(row[hazard_col]) if pd.notnull(row[hazard_col]) else 0.0
                        v = float(row[vulnerability_col]) if pd.notnull(row[vulnerability_col]) else 0.0
                        e = float(row[exposure_col]) if pd.notnull(row[exposure_col]) else 0.0
                    except ValueError:
                        h, v, e = 0.0, 0.0, 0.0

                    raw_product = h * v * e
                    

                    lookup_key = min(allowed_levels, key=lambda x: abs(x - raw_product))

                    pri_scores.append(pri_table[lookup_key]['score'])
                    pri_values.append(pri_table[lookup_key]['value'])
                
                df_pri['PRI scores'] = pri_scores
                df_pri['PRI values'] = pri_values

                cols = list(df_pri.columns)
                core_cols = [c for c in cols if c not in [hazard_col, 'Hazard Level', exposure_col, 'Sensitivity Index', vulnerability_col, 'PRI scores', 'PRI values']]
                index_cols = [hazard_col, 'Hazard Level', exposure_col, 'Sensitivity Index', vulnerability_col]
                final_pri_cols = ['PRI scores', 'PRI values']
                
                new_order = core_cols + index_cols + final_pri_cols
                df_pri = df_pri[new_order]

                st.session_state.calculated_results = df_pri
                st.success("Potential Risk Index (PRI) calculated successfully!")
                st.rerun()
            else:
                missing = [c for c in required_cols if c not in df_pri.columns]
                st.error(f"Missing columns: {', '.join(missing)}. Please run previous steps (Hazards, Exposure, Vulnerability).")
        else:
            st.warning("Please complete previous sections to generate data.")

    if 'calculated_results' in st.session_state and 'PRI scores' in st.session_state.calculated_results.columns:
        
        final_config = {
            "Sensitivity Index": None,
            "PRI scores": st.column_config.NumberColumn("PRI Score", format="%d"),
            "PRI values": st.column_config.TextColumn("PRI Value"),
            "Hazard Index": st.column_config.NumberColumn("Hazard Index"),
            "Exposure Index": st.column_config.NumberColumn("Exposure Index"),
            "Vulnerability Index": st.column_config.NumberColumn("Vuln. Index"),
            "Hazard Level": st.column_config.TextColumn("Hazard Level"),
        }
        
        st.dataframe(
            st.session_state.calculated_results,
            column_config=final_config,
            use_container_width=True
        )

        if st.button("Generate PRI Assessment Report", type="primary", use_container_width=True):
            if not st.session_state.get("gemini_client"):
                 st.error("Please provide a valid API Key to generate the report.")
            else:
                with st.spinner("Analyzing Risk Indices and writing report (Gemini)..."):
                    pri_report_text = generate_pri_report_gemini(st.session_state.calculated_results)
                    st.session_state["pri_report"] = pri_report_text

        if "pri_report" in st.session_state and st.session_state["pri_report"]:
            with st.expander("View PRI Assessment Report", expanded=True):
                st.markdown(st.session_state["pri_report"])
            
            st.download_button(
                label="Download Report as Text",
                data=st.session_state["pri_report"],
                file_name="PRI_Assessment_Report.txt",
                mime="text/plain"
            )
    st.divider()
    st.subheader("7. Nature-based Solutions (NbS) Recommendations")
    st.markdown("#### Step 7.1: Potential Hazards Selection")
    all_hazards_for_selector = [
        "Extreme high temperatures (Heatwave)", "Extreme cold temperatures (Coldwave, cold snap)", "Drought", 
        "Wildfire (Forest fire or Bush fire)", "Desertification", "Storms & strong winds", "Hail", 
        "Aeolian erosion", "Pluvial flood, heavy rainfall and surface runoff", "Fluvial flood", 
        "Coastal flood (e.g. storm surge)", "Impact floods and Tsunami", "Fluvial sediment transport", 
        "Stream bank & bed erosion", "Sheet erosion & rill erosion", "Gully erosion", 
        "Coastal and shoreline erosion (includes freshwater environments)", 
        "Debris flood (Volumetric Sediment Concentration 20-40%)", "Debris flow (Volumetric Sediment Concentration >40%)", 
        "Small Rockfall (Diameter <25cm)", "Large Rockfall (Diameter >25-100 cm)", "Landslides < 2 m depth", 
        "Landslides 2-10 m depth", "Landslides > 10 m depths", "Mud or Earth flow", 
        "Soil slope deformation & Soil creep", "Snow avalanches", "Snow drift", "Snow creep & slide"
    ]

    if 'selected_nbs_hazards' not in st.session_state:
        st.session_state.selected_nbs_hazards = []

    if st.button("Automatic Extraction from PRI Table", type="secondary", help="Extracts hazards listed in the 'Possible Hazards' column."):
        if 'calculated_results' in st.session_state and not st.session_state.calculated_results.empty:
            extracted_hazards = set()
            
            if 'Possible Hazards' in st.session_state.calculated_results.columns:
                 for item in st.session_state.calculated_results['Possible Hazards']:
                    if isinstance(item, str):
                        clean_item = item.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                        parts = [h.strip() for h in clean_item.split(',')]
                        extracted_hazards.update(parts)
                    elif isinstance(item, list):
                        extracted_hazards.update(item)
            
            elif 'saved_data' in st.session_state and not st.session_state.saved_data.empty:
                 indices = st.session_state.calculated_results.index
                 if 'Possible Hazards' in st.session_state.saved_data.columns:
                     subset = st.session_state.saved_data.loc[indices, 'Possible Hazards']
                     for item in subset:
                        if isinstance(item, list):
                             extracted_hazards.update(item)
                        elif isinstance(item, str):
                             clean_item = item.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                             parts = [h.strip() for h in clean_item.split(',')]
                             extracted_hazards.update(parts)

            valid_extracted = [h for h in extracted_hazards if h in all_hazards_for_selector]
            
            if valid_extracted:
                current = set(st.session_state.selected_nbs_hazards)
                current.update(valid_extracted)
                st.session_state.selected_nbs_hazards = list(current)
                st.success(f"Extracted {len(valid_extracted)} hazards.")
                st.rerun()
            else:
                st.warning("No matching hazards found.")
        else:
            st.error("No calculated results available.")

    col1, col2, col3 = st.columns([3.5, 6, 1]) 
    with col2:
        current_indices = [
            all_hazards_for_selector.index(h) 
            for h in st.session_state.selected_nbs_hazards 
            if h in all_hazards_for_selector
        ]
        
        transfer_output = sac.transfer(
            items=all_hazards_for_selector,
            label="Select Hazards",
            index=current_indices, 
            titles=["Available", "Selected"],
            format_func="title",
            search=True,
            height=500,
            pagination=False,
            reload=True
        )
        
        if transfer_output is not None:
             st.session_state.selected_nbs_hazards = transfer_output

    if st.session_state.selected_nbs_hazards:
        st.markdown("### Recommended Solutions")
        nbs_data_source = NbS_list[0] if isinstance(NbS_list, list) and len(NbS_list) > 0 else {}
        
        for hazard in st.session_state.selected_nbs_hazards:
            with st.expander(f"**{hazard}**", expanded=False):
                if hazard in nbs_data_source:
                    rec_data = nbs_data_source[hazard]
                    
                    c_yes, c_supp = st.columns(2)
                    with c_yes:
                        st.markdown("#### ✅ Primary Solutions")
                        for item in rec_data.get("Yes", []):
                            st.success(f"- {item}")
                    with c_supp:
                        st.markdown("#### 🤝 Supportive Solutions")
                        for item in rec_data.get("Supportive", []):
                            st.warning(f"- {item}")
                else:
                    st.info("No specific NbS data found for this hazard.")
    
    st.markdown("#### Step 7.2. NbS Implementation Summary Table")

    if st.button("Generate NbS Summary Table"):
        if 'calculated_results' in st.session_state and not st.session_state.calculated_results.empty:
            df_nbs = st.session_state.calculated_results.copy()
            if 'Possible Hazards' not in df_nbs.columns and 'saved_data' in st.session_state:
                 df_nbs['Possible Hazards'] = st.session_state.saved_data.loc[df_nbs.index, 'Possible Hazards']
            
            if 'Possible Hazards' in df_nbs.columns:
                primary_sol_col = []
                supportive_sol_col = []
                nbs_db = NbS_list[0] if isinstance(NbS_list, list) and len(NbS_list) > 0 else {}
                valid_nbs_keys = list(nbs_db.keys())

                for _, row in df_nbs.iterrows():
                    hazards_item = row['Possible Hazards']
                    current_hazards = hazards_item if isinstance(hazards_item, list) else [k for k in valid_nbs_keys if k in str(hazards_item)]
                    
                    p_sols, s_sols = set(), set()
                    for h in current_hazards:
                        if h.strip() in nbs_db:
                            p_sols.update(nbs_db[h.strip()].get("Yes", []))
                            s_sols.update(nbs_db[h.strip()].get("Supportive", []))
                            
                    primary_sol_col.append(", ".join(sorted(list(p_sols))))
                    supportive_sol_col.append(", ".join(sorted(list(s_sols))))
                st.session_state.calculated_results["Primary Solutions"] = primary_sol_col
                st.session_state.calculated_results["Supportive Solutions"] = supportive_sol_col
                
                st.success("Solutions mapped and saved to session memory.")
                st.dataframe(st.session_state.calculated_results[["Infrastructure", "Asset", "Primary Solutions"]], use_container_width=True)
            else:
                st.error("Missing hazard data.")
        else:
            st.warning("Please run previous analysis steps first.")
    st.divider()
    st.markdown("#### 7.3. Sort NbS Solutions for Best Selection")
    if 'nbs_primary_options' not in st.session_state: st.session_state.nbs_primary_options = []
    if 'nbs_supportive_options' not in st.session_state: st.session_state.nbs_supportive_options = []
    if 'nbs_selection_primary' not in st.session_state: st.session_state.nbs_selection_primary = []
    if 'nbs_selection_supportive' not in st.session_state: st.session_state.nbs_selection_supportive = []
    if 'nbs_eval_df_primary' not in st.session_state: st.session_state.nbs_eval_df_primary = pd.DataFrame()
    if 'nbs_eval_df_supportive' not in st.session_state: st.session_state.nbs_eval_df_supportive = pd.DataFrame()
    col_btn_ext, col_chk_supp, col_btn_res, _ = st.columns([1.5, 2, 1.5, 2.5])
    
    with col_btn_ext:
        extract_solutions_btn = st.button("Extract Available Solutions", help="Parse solutions paired with assets from Section 7.2.")
    
    with col_chk_supp:
        include_supportive_chk = st.checkbox("Include Supportive Solutions in Analysis", value=False)
        
    with col_btn_res:
        if st.button("Reset All Selections", help="Clear all solution lists and evaluation data."):
            st.session_state.nbs_primary_options = []
            st.session_state.nbs_supportive_options = []
            st.session_state.nbs_selection_primary = []
            st.session_state.nbs_selection_supportive = []
            st.session_state.nbs_eval_df_primary = pd.DataFrame()
            st.session_state.nbs_eval_df_supportive = pd.DataFrame()
            st.toast("Selections and evaluation tables cleared.", icon="🧹")
            st.rerun()
    if extract_solutions_btn:
        if 'calculated_results' not in st.session_state or "Primary Solutions" not in st.session_state.calculated_results.columns:
            st.error("❌ No mapped solutions found. Please click 'Generate NbS Summary Table' in Section 7.2 first to link solutions to your specific assets.")
        else:
            df_source = st.session_state.calculated_results
            primary_context_set = set()
            supportive_context_set = set()

            for _, row in df_source.iterrows():
                asset_name = str(row.get('Asset', 'Asset'))
                p_raw = str(row.get("Primary Solutions", ""))
                if p_raw and p_raw != "nan" and p_raw.strip() != "":
                    for sol in [x.strip() for x in p_raw.split(',')]:
                        if sol: primary_context_set.add(f"{sol} for {asset_name}")
                s_raw = str(row.get("Supportive Solutions", ""))
                if s_raw and s_raw != "nan" and s_raw.strip() != "":
                    for sol in [x.strip() for x in s_raw.split(',')]:
                        if sol: supportive_context_set.add(f"{sol} for {asset_name}")
            
            st.session_state.nbs_primary_options = sorted(list(primary_context_set))
            st.session_state.nbs_supportive_options = sorted(list(supportive_context_set))
            
            if st.session_state.nbs_primary_options:
                st.success(f"✅ Successfully extracted {len(primary_context_set)} unique asset-solution pairs.")
                st.rerun()
            else:
                st.warning("No solutions were found in the 7.2 table for the current hazards.")
    if st.session_state.nbs_primary_options:
        st.markdown("##### Select Primary Solutions to Evaluate")
        st.session_state.nbs_selection_primary = sac.transfer(
            items=st.session_state.nbs_primary_options,
            label="Primary Solutions",
            titles=["Available", "Selected for Evaluation"],
            search=True,
            reload=True,
            key="sac_primary_filtered"
        )

        if include_supportive_chk and st.session_state.nbs_supportive_options:
            st.markdown("##### Select Supportive Solutions to Evaluate")
            st.session_state.nbs_selection_supportive = sac.transfer(
                items=st.session_state.nbs_supportive_options,
                label="Supportive Solutions",
                titles=["Available", "Selected for Evaluation"],
                search=True,
                reload=True,
                key="sac_supportive_filtered"
            )
        if st.button("Initialize Evaluation Tables"):
            if not st.session_state.nbs_selection_primary:
                st.warning("Please select at least one Primary solution for evaluation.")
            else:
                kpi_rows = [
                    "Safety, Reliability and Security (SRS)", 
                    "Availability and Maintainability (AM)", 
                    "Economy (EC)", 
                    "Environment (EV)", 
                    "Health and Politics (HP)"
                ]
                data_p = {col: [3]*5 for col in st.session_state.nbs_selection_primary}
                st.session_state.nbs_eval_df_primary = pd.DataFrame(data_p, index=kpi_rows)
                
                if include_supportive_chk and st.session_state.nbs_selection_supportive:
                    data_s = {col: [3]*5 for col in st.session_state.nbs_selection_supportive}
                    st.session_state.nbs_eval_df_supportive = pd.DataFrame(data_s, index=kpi_rows)
                else:
                    st.session_state.nbs_eval_df_supportive = pd.DataFrame()
                st.rerun()
    if not st.session_state.nbs_eval_df_primary.empty:
        st.markdown("#### Expert Evaluation: CI(HN) Scores (1-5)")
        st.caption("1 = Significant condition improvement, 5 = Minimal/No improvement. Default is 3.")
        
        st.markdown("**Primary Solutions Evaluation**")
        edited_primary = st.data_editor(
            st.session_state.nbs_eval_df_primary,
            use_container_width=True,
            key="editor_primary_final"
        )
        edited_supportive = pd.DataFrame()
        if not st.session_state.nbs_eval_df_supportive.empty:
            st.markdown("**Supportive Solutions Evaluation**")
            edited_supportive = st.data_editor(
                st.session_state.nbs_eval_df_supportive,
                use_container_width=True,
                key="editor_supportive_final"
            )
        if st.button("Validate and Rank Solutions"):
            all_valid = (edited_primary.values.min() >= 1 and edited_primary.values.max() <= 5)
            if not edited_supportive.empty:
                all_valid = all_valid and (edited_supportive.values.min() >= 1 and edited_supportive.values.max() <= 5)
            
            if not all_valid:
                st.error("All scores must be between 1 and 5.")
            else:
                st.session_state.nbs_eval_df_primary = edited_primary
                if not edited_supportive.empty:
                    st.session_state.nbs_eval_df_supportive = edited_supportive
                color_map = {1: "#6dbf7a", 2: "#a6d17b", 3: "#ffeb84", 4: "#f9a674", 5: "#f76d6d"}
                primary_results = []
                for col in edited_primary.columns:
                    primary_results.append({
                        "Context": col,
                        "Score": int(edited_primary[col].min())
                    })
                primary_results.sort(key=lambda x: x["Score"])

                st.subheader("🏆 Primary NbS Ranking for Infrastructure Condition Improvement")
                for rank, res in enumerate(primary_results, 1):
                    score = res['Score']
                    st.markdown(
                        f"""
                        <div style="background-color: {color_map.get(score, '#fff')}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ddd; color: black;">
                            <h4 style="margin:0;">#{rank}: {res['Context']}</h4>
                            <p style="margin:0;">Condition Improvement Score: <b>{score}</b></p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                if not edited_supportive.empty:
                    supportive_results = []
                    for col in edited_supportive.columns:
                        supportive_results.append({
                            "Context": col,
                            "Score": int(edited_supportive[col].min())
                        })
                    supportive_results.sort(key=lambda x: x["Score"])

                    st.markdown("---")
                    st.subheader("🏆 Supportive NbS Ranking for Infrastructure Condition Improvement")
                    for rank, res in enumerate(supportive_results, 1):
                        score = res['Score']
                        st.markdown(
                            f"""
                            <div style="background-color: {color_map.get(score, '#fff')}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ddd; color: black;">
                                <h4 style="margin:0;">#{rank}: {res['Context']}</h4>
                                <p style="margin:0;">Condition Improvement Score: <b>{score}</b></p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
