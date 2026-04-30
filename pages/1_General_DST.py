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

from modules.impact_models import get_all_impact_data
from modules.nbs import NbS_list

LOGO_URL = "https://raw.githubusercontent.com/NATURE-DEMO/Decision_Support_Tool/main/images/main_logo.png"
DOCS_URL = "https://nature-demo.github.io/Decision_Support_Tool/"
CLIMA_DOCS_URL = "https://nature-demo.github.io/clima-data/indicators/"

GEMINI_MODEL_VERSION = "gemini-2.5-flash-lite"

AI_DISCLAIMER_TEXT = (
    "**Disclaimer:** The AI-generated summaries and interpretations provided by this tool are "
    "intended to support understanding and exploration of geospatial and infrastructure data. "
    "These outputs are automatically generated and should **not** be used as the sole basis for "
    "any decisions. Users are advised to consult the detailed, tabular data provided within the "
    "tool and seek expert advice before making any decisions. "
    "The project does not bear responsibility for actions taken solely on the basis of AI-generated content."
)

AI_LIMITATIONS_TEXT = "- AI-generated content may occasionally contain inaccuracies or omissions.\n- The AI does not possess domain expertise and may misinterpret ambiguous or incomplete data.\n- This system is not designed for real-time operational decision-making or emergency response without expert validation."


def render_ai_header(report_title: str):
    """Renders the standardised AI transparency header above every AI-generated report."""
    st.markdown(
        f"""
        <div style="background-color:#fff8e1; border-left:5px solid #f9a825;
                    padding:12px 16px; border-radius:6px; margin-bottom:8px;">
            <span style="font-size:1.05em;">🤖 <strong>AI-Generated Content</strong>
            &nbsp;|&nbsp; Model: <code>{GEMINI_MODEL_VERSION}</code>
            &nbsp;|&nbsp; {report_title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(AI_DISCLAIMER_TEXT)


def render_ai_footer():
    """Renders the standardised limitations notice and feedback prompt below every AI-generated report."""
    with st.expander("⚠️ AI Limitations & Responsible Use", expanded=False):
        st.markdown(AI_LIMITATIONS_TEXT)
    st.info(
        "📣 **Feedback:** Found an inaccuracy or misleading interpretation? Please report it to the project team via the dedicated feedback channel so we can improve the AI component."
    )


KOPPEN_COLORS = (
    np.array(
        [
            [0, 0, 255],
            [0, 120, 255],
            [70, 170, 250],
            [255, 0, 0],
            [255, 150, 150],
            [245, 165, 0],
            [255, 220, 100],
            [255, 255, 0],
            [200, 200, 0],
            [150, 150, 0],
            [150, 255, 150],
            [100, 200, 100],
            [50, 150, 50],
            [200, 255, 80],
            [100, 255, 80],
            [50, 200, 0],
            [255, 0, 255],
            [200, 0, 200],
            [150, 50, 150],
            [150, 100, 150],
            [170, 175, 255],
            [90, 120, 220],
            [75, 80, 180],
            [50, 0, 135],
            [0, 255, 255],
            [55, 200, 255],
            [0, 125, 125],
            [0, 70, 95],
            [178, 178, 178],
            [102, 102, 102],
        ]
    )
    / 255.0
)

KOPPEN_CLASSES = {
    1: "Af",
    2: "Am",
    3: "Aw",
    4: "BWh",
    5: "BWk",
    6: "BSh",
    7: "BSk",
    8: "Csa",
    9: "Csb",
    10: "Csc",
    11: "Cwa",
    12: "Cwb",
    13: "Cwc",
    14: "Cfa",
    15: "Cfb",
    16: "Cfc",
    17: "Dsa",
    18: "Dsb",
    19: "Dsc",
    20: "Dsd",
    21: "Dwa",
    22: "Dwb",
    23: "Dwc",
    24: "Dwd",
    25: "Dfa",
    26: "Dfb",
    27: "Dfc",
    28: "Dfd",
    29: "ET",
    30: "EF",
}

KOPPEN_TIFF_URL = "https://raw.githubusercontent.com/saturngreen67/streamlit_tests/main/Koppen/1991-2020/koppen_geiger_0p1.tif"

infra_options = {
    "Roads & Highways": ['["highway"]'],
    "Railways": ['["railway"]'],
    "Bridges": ['["bridge"="yes"]', '["man_made"="bridge"]'],
    "Tunnels": ['["tunnel"="yes"]', '["man_made"="tunnel"]'],
    "Dams & Water Storage": [
        '["waterway"="dam"]',
        '["waterway"="weir"]',
        '["man_made"="dam"]',
        '["man_made"="dyke"]',
    ],
    "Urban Green Spaces": [
        '["leisure"="park"]',
        '["leisure"="garden"]',
        '["landuse"="forest"]',
        '["landuse"="grass"]',
        '["landuse"="meadow"]',
        '["natural"="wood"]',
        '["natural"="wetland"]',
    ],
    "Embankments & Levees": [
        '["man_made"="embankment"]',
        '["man_made"="groyne"]',
        '["man_made"="levee"]',
    ],
    "Slope Stabilization": [
        '["man_made"="check_dam"]',
        '["man_made"="retaining_wall"]',
        '["barrier"="retaining_wall"]',
    ],
    "Buildings": ['["building"]', '["amenity"]'],
    "Power & Utilities": ['["power"]'],
    "Water Bodies & Rivers": ['["water"]', '["waterway"]'],
    "Catchment Surface Cover": ['["landuse"]', '["natural"]'],
}

kpis = [
    "Safety, Reliability and Security (SRS)",
    "Availability and Maintainability (AM)",
    "Economy (EC)",
    "Environment (EV)",
    "Health and Politics (HP)",
]
scenarios = {
    "CI": "Current condition of the critical infrastructure",
    "CI_H": "Condition after natural hazard (H)",
    "CI_HG": "Condition after hazard but protected by grey measures (HG)",
    "CI_HN": "Condition after hazard but protected by nature-based solutions (HN)",
    "CI_HNG": "Condition after hazard but protected by both grey and nature-based solutions (HNG)",
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
climate_drivers = [
    "Air surface temperature increase (High temperatures)",
    "Change in Temperature (High temperatures)",
    "Change in precipitation",
    "Change in precipitation (Low)",
    "Change in temperature (Low temperature)",
    "Changes in Temperature (High temperatures)",
    "Changes in Temperature (Low temperatures)",
    "Changes in precipitation",
    "Changes in snow intensity",
    "Changes in temperature (High temperatures)",
    "Changes in temperature (Low temperatures)",
    "Changes in wind intensity",
    "Extreme heat (including heatwaves)",
    "Extreme precipitation",
    "Extreme temperature (low)",
    "Increased solar intensity",
    "Low precipitation",
    "Reduced atmosferic humidity",
]


def calculate_exposure(rev, cap, r_l, r_h, c_l, c_h):
    """Calculates Exposure Index based on user-defined thresholds."""
    if rev < r_l:
        if cap < c_l:
            return 1
        elif c_l <= cap <= c_h:
            return 2
        else:
            return 3
    elif r_l <= rev <= r_h:
        if cap < c_l:
            return 2
        elif c_l <= cap <= c_h:
            return 3
        else:
            return 4
    else:
        if cap < c_l:
            return 3
        elif c_l <= cap <= c_h:
            return 4
        else:
            return 5


def polygon_style_function(feature):
    return {"fillColor": "blue", "color": "blue"}


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

        center_code = (
            int(data_cropped[center_row, center_col])
            if not np.isnan(data_cropped[center_row, center_col])
            else None
        )
        koppen_code = KOPPEN_CLASSES.get(
            center_code, "N/A") if center_code else "N/A"

    else:
        koppen_code = "N/A"

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(
        data_cropped,
        cmap=cmap,
        extent=(min_lon, max_lon, min_lat, max_lat),
        origin="upper",
        alpha=0.6,
        zorder=2,
    )

    try:
        cx.add_basemap(ax, crs="EPSG:4326",
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


def generate_context_report(center_lat, center_lon, area_sq_km, elements, selected_infras=None):
    """Generate AI context report for the selected infrastructure types only.

    ``elements`` must already be filtered to the user-selected infra categories
    before calling this function. ``selected_infras`` is passed in so that the
    prompt can name the exact categories the user chose.
    """
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    center_coord_str = f"{center_lat:.4f}, {center_lon:.4f}"
    infra_counts = {}
    categories = selected_infras if selected_infras else list(
        infra_options.keys())
    for infra in categories:
        count = 0
        for element in elements:
            tags = element.get("tags", {})
            for filter_str in infra_options[infra]:
                m = re.search(r'\["(.+?)"(?:="(.+?)")?\]', filter_str)
                if m:
                    k, v = m.groups()
                    if k in tags and (v is None or tags[k] == v):
                        count += 1
                        break
        if count:
            infra_counts[infra] = count

    extracted_infrastructure_list = "\n".join(
        [
            f"- {k}: {v} items"
            for k, v in sorted(infra_counts.items(), key=lambda item: item[1], reverse=True)
        ]
    )
    if not extracted_infrastructure_list:
        extracted_infrastructure_list = (
            "- No specific infrastructure elements found for the selected types."
        )

    selected_types_str = ", ".join(
        selected_infras) if selected_infras else "all available types"

    detailed_elements = []
    for element in elements:
        elem_info = {
            "type": element.get("type", "Unknown"),
            "id": element.get("id", "N/A"),
            "tags": element.get("tags", {}),
        }
        detailed_elements.append(elem_info)

    detailed_str = json.dumps(detailed_elements, indent=2)

    system_instruction = (
        "You are an expert geographical and infrastructure analyst. Your task is to generate a report "
        "by analyzing the provided OpenStreetMap data and geographical coordinate.\n\n"
        "**STRICT COMPLIANCE & AI ETHICS PROTOCOLS (EU Guidelines for Trustworthy AI):**\n"
        "1. **Zero Hallucination (Technical Robustness):** Base your analysis EXCLUSIVELY on the provided OpenStreetMap data. Do not invent, assume, or infer the existence of infrastructure, materials, or features not explicitly present in the tags.\n"
        "2. **Acknowledge Uncertainty (Transparency):** If data for a specific infrastructure type is sparse, missing, or ambiguous, you MUST explicitly state that the data is limited. Do not attempt to fill in the blanks with assumptions.\n"
        "3. **Scope Restriction:** Only discuss the infrastructure types explicitly listed in the user's selection. DO NOT introduce or describe infrastructure categories that were not requested.\n"
        "4. **No Climate Speculation:** DO NOT include any climate, weather, or hazard risk forecasting in this specific report. Stick strictly to spatial and infrastructural facts."
    )

    user_prompt = f"""
    Analyze the following geographical data for a selected area:

    1. **Geographical Area Details:**
        - **Approximate Center Coordinate (Latitude, Longitude):** {center_coord_str}
        - **Approximate Area:** {area_sq_km:.2f} square kilometers
        - **Selected Infrastructure Types for this Analysis:** {selected_types_str}
        
    2. **Extracted OpenStreetMap Infrastructure Data (Summary of {len(elements)} Items):**
    {extracted_infrastructure_list}
    
    3. **Detailed OpenStreetMap Elements (Full Tags and Metadata):**
    {detailed_str}

    **REPORT INSTRUCTIONS:**
    Analyze the coordinates and the extracted infrastructure details provided above. 
    
    **Provide the report in the following narrative Markdown format. DO NOT output JSON:**
    
    ### 1. Geographical Context
    [Provide a factual overview of the area based strictly on the coordinates and infrastructure density.]
    
    ### 2. Infrastructure Overview
    [Provide a high-level summary of the extracted infrastructure types based ONLY on the provided JSON counts.]
    
    ### 3. Detailed Infrastructure Analysis
    [Break down the specific details found in the tags for each selected category. Discuss materials, surfaces, lanes, capacity, or specific asset types discovered. If specific details like surface material are missing from the tags, explicitly state "Data regarding materials is not available in the current dataset."]
    
    ### 4. Data Limitations & Key Observations
    [Provide 2-3 factual bullet points highlighting notable infrastructure features. You MUST include at least one bullet point addressing the completeness or limitations of the extracted OpenStreetMap data to ensure transparency.]
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = st.session_state["gemini_client"].models.generate_content(
                model=GEMINI_MODEL_VERSION,
                contents=[user_prompt],
                config={"system_instruction": system_instruction},
            )
            return response.text
        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    st.warning(
                        f"API Rate limit hit. Pausing for 45 seconds (Attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(45)
                    continue
                else:
                    return "Gemini API Error: Rate limit exceeded. Please try again later."
            return f"Gemini API Error (Context Report): {e.message}."
        except Exception as e:
            st.error(
                f"An unexpected error occurred during context report generation: {e}")
            return "An unexpected error occurred during context report generation."


def generate_koppen_interpretation(koppen_code):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate climate interpretation."

    if koppen_code in ["N/A", "Unknown"]:
        return "Cannot generate interpretation. The Köppen climate code could not be determined from the map."

    system_instruction = (
        "You are an expert climatologist. Your task is to provide a detailed, easy-to-understand interpretation "
        "of the given Köppen Climate Classification code. "
        "STRICT PROTOCOL: Base your interpretation solely on your training knowledge of Köppen classifications. "
        "Ensure all temperatures are provided in Celsius. The response must focus purely on established scientific climate conditions. "
        "Do not invent or speculate on localized weather events."
    )

    user_prompt = f"""
    Provide a detailed interpretation of the following Köppen Climate Classification code: **{koppen_code}**.

    **REPORT INSTRUCTIONS:**
    Provide the report in narrative Markdown format. DO NOT output JSON or code blocks.
    
    Your report must cover:
    ### 1. Full Classification Name
    (e.g., 'Humid subtropical climate').
    
    ### 2. Key Characteristics
    The general weather patterns, typical seasonal changes, and defining temperature and precipitation features (e.g., hot/cold summers, dry/wet winters).
    
    ### 3. Ecological Implications
    Briefly mention the types of vegetation or agriculture typically naturally found in this climate.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = st.session_state["gemini_client"].models.generate_content(
                model=GEMINI_MODEL_VERSION,
                contents=[user_prompt],
                config={"system_instruction": system_instruction},
            )
            return response.text
        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    st.warning(
                        f"API Rate limit hit. Pausing for 45 seconds (Attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(45)
                    continue
                else:
                    return "Gemini API Error: Rate limit exceeded. Please try again later."
            return f"Gemini API Error (Köppen Interpretation): {e}."
        except Exception as e:
            st.error(
                f"An unexpected error occurred during Köppen interpretation generation: {e}")
            return "An unexpected error occurred during Köppen interpretation generation."


def generate_risk_interpretation(df_risks: pd.DataFrame, kpis: list, scenarios: dict):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate risk interpretation."

    df_risks_prompt = df_risks.rename_axis("").to_markdown()

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
        "As indicated in the assessment matrix, the implementation of Grey Protective Infrastructure (CI_HG) "
        "leads to a noticeable improvement in the condition of the critical infrastructure compared to the unprotected hazard scenario (CI_H). "
        "The Environment (EV) indicator is the only metric that remains unchanged (3 -> 3). "
        "Specifically, the protective solutions contribute to enhancing the Safety, Reliability and Security (SRS) (5 -> 4), "
        "Availability and Maintainability (AM) (3 -> 2), and Health and Politics (HP) (4 -> 3) indicators, "
        "improving their condition levels by one grade each. Furthermore, the Economy (EC) metric shows the greatest "
        "improvement, advancing two grades to reach a 'Good' condition (4 -> 2). "
        "Overall, the matrix demonstrates that while the grey infrastructure significantly mitigates economic and operational vulnerabilities, "
        "it does not alter the environmental risk profile of the asset."
    )

    scenario_desc = "\n".join(
        [f"- **{abbr}**: {desc}" for abbr, desc in scenarios.items()])
    kpi_list = "\n".join([f"- {k}" for k in kpis])

    system_instruction = (
        "You are an expert risk and resilience analyst. Your task is to interpret a stakeholder "
        "risk assessment matrix. The ratings are from 1 (best) to 5 (worst).\n\n"
        "STRICT PROTOCOLS (EU AI Ethics Guidelines):\n"
        "1. Zero Hallucination: Base your analysis EXCLUSIVELY on the provided matrix numbers. "
        "Do not invent specific infrastructure types (e.g., 'flood walls'), hazards, or physical mechanisms not explicitly stated in the prompt.\n"
        "2. Output Format: You must output a narrative Markdown text. DO NOT output JSON or reconstruct the table.\n"
        "3. Tone: Follow the logical structure and professional tone provided in the 'EXAMPLE ANALYSIS'."
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
    Provide a professional interpretation following the style of the example in narrative Markdown format. DO NOT output JSON or tables.
    
    1. Compare CI_H to the protection scenarios (CI_HG, CI_HN, CI_HNG).
    2. Explicitly mention the numerical grade changes exactly as they appear in the data (e.g., 4 -> 3).
    3. Use professional engineering reasoning to explain the shifts in KPIs based on standard infrastructure resilience principles, WITHOUT hallucinating specific physical assets.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = st.session_state["gemini_client"].models.generate_content(
                model=GEMINI_MODEL_VERSION,
                contents=[user_prompt],
                config={"system_instruction": system_instruction},
            )
            return response.text
        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    st.warning(
                        f"API Rate limit hit. Pausing for 45 seconds (Attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(45)
                    continue
                else:
                    return "Gemini API Error: Rate limit exceeded. Please try again later."
            return f"Gemini API Error (Risk Interpretation): {e.message}."
        except Exception as e:
            return f"An error occurred: {e}"


def generate_hazard_report_gemini(calculated_df):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    hazard_table_md = calculated_df.to_markdown(index=False)

    system_instruction = (
        "You are an expert climate hazard analyst. Your task is to generate a professional report "
        "interpreting a climate hazard table calculated for a specific infrastructure project.\n\n"
        "STRICT PROTOCOLS (EU AI Ethics Guidelines):\n"
        "1. Zero Hallucination: Base your analysis EXCLUSIVELY on the provided markdown table. "
        "Do not invent climate drivers, impact models, or hazard indexes that are not explicitly present in the data.\n"
        "2. Output Format: You must output a narrative Markdown text. DO NOT output JSON or reconstruct the table.\n"
        "3. Style & Tone: Follow the depth and structure of the provided 'EXAMPLE REPORT' strictly."
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

    **REPORT INSTRUCTIONS:**
    Provide the response strictly in narrative Markdown format. DO NOT output JSON or tables.
    
    1. Analyze the 'Actual Hazard Data Table' above.
    2. Write a narrative report similar in structure and tone to the Example Report.
    3. Group hazards logically (e.g., Temperature-related, Water-related) based on the 'Climate driver' column.
    4. Explicitly mention the 'Hazard Level' (e.g., EXTREME, HIGH) and 'Hazard Index' exactly as they appear in the data.
    5. Discuss the implications for the specific 'Infrastructure' and 'Asset' types listed in the table based ONLY on the 'Impact model' column.
    6. ANTI-SPECULATION: If a hazard shows "No variation", state exactly that. Do not speculate about extreme events, unmeasured shifts, or secondary impacts not captured in the table.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = st.session_state["gemini_client"].models.generate_content(
                model=GEMINI_MODEL_VERSION,
                contents=[user_prompt],
                config={"system_instruction": system_instruction,
                        "temperature": 0.3},
            )
            return response.text

        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    st.warning(
                        f"API Rate limit hit during Hazard Analysis. Pausing for 45 seconds (Attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(45)
                    continue
                else:
                    return "Error: Gemini API rate limit exceeded. Please wait a few minutes before trying again."
            else:
                return f"Gemini API Error: {e.message}"
        except Exception as e:
            return f"Error generating hazard report: {e}"


def generate_pri_report_gemini(calculated_df):
    if not st.session_state.get("gemini_client"):
        return "Gemini client not initialized. Cannot generate report."

    df_prompt = calculated_df.copy()
    required_cols = [
        "Infrastructure",
        "Climate driver",
        "Impact model",
        "Hazard Index",
        "Exposure Index",
        "Vulnerability Index",
        "PRI scores",
        "PRI values",
    ]

    available_cols = [c for c in required_cols if c in df_prompt.columns]
    df_prompt = df_prompt[available_cols]
    pri_table_md = df_prompt.to_markdown(index=False)

    system_instruction = (
        "You are a senior infrastructure risk analyst. Your task is to write a formal "
        "'Potential Risk Index (PRI) Assessment Report' based on the provided data table.\n\n"
        "STRICT PROTOCOLS (EU AI Ethics Guidelines):\n"
        "1. Zero Hallucination: Base your analysis EXCLUSIVELY on the provided markdown table. "
        "Do not invent risks, infrastructure assets, or scores that are not explicitly present in the data.\n"
        "2. Output Format: You must output a narrative Markdown text. DO NOT output JSON or reconstruct the table.\n"
        "3. Tone & Style: Follow the Structure, Tone, and Logic of the provided 'EXAMPLE REPORT' strictly. "
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

    **REPORT INSTRUCTIONS:**
    Provide the response strictly in narrative Markdown format. DO NOT output JSON or tables.
    
    1. Analyze the 'Actual PRI Data Table' above.
    2. Write a narrative report similar in structure to the Example Report.
    3. **Categorize** the risks: Identify the Highest PRI scores first, then Moderate/Low, then Zero.
    4. **Explain the Drivers:** For the highest risks, explicitly explain *why* the score is high (e.g., "Driven by high Exposure (EI=4) despite moderate Hazard...").
    5. **ANTI-SPECULATION:** Summarize the overall risk landscape strictly based on the provided data. Do NOT invent or suggest specific engineering adaptation strategies.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = st.session_state["gemini_client"].models.generate_content(
                model=GEMINI_MODEL_VERSION,
                contents=[user_prompt],
                config={"system_instruction": system_instruction,
                        "temperature": 0.3},
            )
            return response.text

        except APIError as e:
            if e.code == 429:
                if attempt < max_retries - 1:
                    st.warning(
                        f"API Rate limit hit during PRI Analysis. Pausing for 45 seconds (Attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(45)
                    continue
                else:
                    return "Error: Gemini API rate limit exceeded. Please wait a few minutes before trying again."
            else:
                return f"Gemini API Error: {e.message}"
        except Exception as e:
            return f"Error generating PRI report: {e}"


@st.cache_resource(ttl=3600)
def build_folium_map_object(center, zoom, polygon_data, drawing_key):
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

    folium.raster_layers.TileLayer(
        tiles="https://tiles.arcgis.com/tiles/SDXw0l5jQ3C1QO7x/arcgis/rest/services/Koeppen_Geiger_Climate_Classification_2020/MapServer/tile/{z}/{y}/{x}",
        attr="Köppen-Geiger / Esri",
        name="Köppen-Geiger Climate Classification (Overlay)",
        overlay=True,
        opacity=0.6,
        control=True,
    ).add_to(m)

    draw = folium.plugins.Draw(export=False, draw_options={
                               "polygon": True, "rectangle": True})
    draw.add_to(m)
    folium.LayerControl().add_to(m)

    if polygon_data:
        folium.GeoJson(
            polygon_data, name="Drawn Polygon", style_function=polygon_style_function
        ).add_to(m)
    return m


@st.cache_resource
def build_base_map(center_lat, center_lon, zoom):
    """Lightweight static base map for the extraction tab.
    Does not embed the polygon in the HTML, avoiding the st_folium
    re-render / map-disappearing issue when session state changes."""
    m = folium.Map(location=[center_lat, center_lon],
                   zoom_start=zoom, tiles="CartoDB positron")
    folium.raster_layers.TileLayer(
        tiles="https://tiles.arcgis.com/tiles/SDXw0l5jQ3C1QO7x/arcgis/rest/services/Koeppen_Geiger_Climate_Classification_2020/MapServer/tile/{z}/{y}/{x}",
        attr="Köppen-Geiger / Esri",
        name="Köppen-Geiger Climate Classification (Overlay)",
        overlay=True,
        opacity=0.6,
        control=True,
    ).add_to(m)
    draw = folium.plugins.Draw(export=False, draw_options={
                               "polygon": True, "rectangle": True})
    draw.add_to(m)
    folium.LayerControl().add_to(m)
    return m


@st.cache_data(ttl=3600)
def geocode_location(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "GeneralDecisionSupportTool/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
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
    headers = {
        "User-Agent": "DecisionSupportTool/1.0 (contact@nature-demo.eu)",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                overpass_url, data={"data": query}, headers=headers, timeout=180)
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                st.error(
                    "Overpass API Error: Bad Request (400). Check query syntax.")
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
                st.error(
                    f"⚠️ Overpass API Error: HTTP Status Code {response.status_code}")
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
    if "tags" not in element or not element["tags"]:
        return False
    for key in infra_keys:
        if key in element["tags"]:
            return True
    return False


def create_detailed_dataframe(elements):
    if not elements:
        return pd.DataFrame()
    data_rows = []
    for element in elements:
        row_data = {"type": element.get(
            "type", ""), "id": element.get("id", "")}
        if "tags" in element and element["tags"]:
            for tag_key, tag_value in element["tags"].items():
                row_data[f"tag.{tag_key}"] = tag_value
        data_rows.append(row_data)
    return pd.DataFrame(data_rows).fillna("")


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
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[1, 5], tickvals=[1, 2, 3, 4, 5])),
        title=title,
        height=650,
    )
    return fig


def create_risk_heatmap_plotly(
    df_risk: pd.DataFrame, df_loss: pd.DataFrame, scenario_key: str, kpis: list
):
    risk_values = pd.to_numeric(df_risk[scenario_key], errors="coerce")
    loss_values = pd.to_numeric(df_loss[scenario_key], errors="coerce")

    plot_df = pd.DataFrame(
        {"Risk Rating (X)": risk_values,
         "Loss Rating (CI)": loss_values, "KPI": kpis}
    ).dropna()

    plot_df["Severity"] = plot_df["Risk Rating (X)"] * \
        plot_df["Loss Rating (CI)"]

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
            "Loss Rating (CI)": "Extent of Loss Rating (1-5)",
        },
        color_continuous_scale=px.colors.sequential.Reds,
        range_x=[0.5, 5.5],
        range_y=[0.5, 5.5],
        height=480,
    )

    fig.update_layout(
        xaxis=dict(tickvals=list(range(1, 6)), tickmode="array",
                   showgrid=True, zeroline=False),
        yaxis=dict(tickvals=list(range(1, 6)), tickmode="array",
                   showgrid=True, zeroline=False),
        height=480,
        coloraxis_showscale=False,
    )

    grid_x, grid_y = np.meshgrid(np.arange(1, 6), np.arange(1, 6))
    grid_z = grid_x * grid_y

    fig.add_trace(
        go.Heatmap(
            z=grid_z,
            x=np.arange(1, 6),
            y=np.arange(1, 6),
            colorscale=px.colors.sequential.Reds,
            showscale=False,
            zmin=1,
            zmax=25,
            hoverinfo="skip",
            opacity=0.3,
        )
    )
    fig.update_traces(selector={"type": "scatter"}, textposition="top center")
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

initial_data = {scenario_key: {k: 3 for k in kpis}
                for scenario_key in scenarios}
if "risk_matrix_data" not in st.session_state:
    st.session_state["risk_matrix_data"] = pd.DataFrame(
        initial_data, index=kpis).to_dict()

initial_loss_data = {scenario_key: {k: 3 for k in kpis}
                     for scenario_key in scenarios}
if "loss_matrix_data" not in st.session_state:
    st.session_state["loss_matrix_data"] = pd.DataFrame(
        initial_loss_data, index=kpis).to_dict()

if "interpretation_report" not in st.session_state:
    st.session_state["interpretation_report"] = ""

if "hazard_report" not in st.session_state:
    st.session_state["hazard_report"] = ""

try:
    all_lvl2_data = get_all_impact_data()
    df_lvl2_base = pd.DataFrame(all_lvl2_data)

    for col in df_lvl2_base.columns:
        if df_lvl2_base[col].apply(lambda x: isinstance(x, list)).any():
            df_lvl2_base[col] = df_lvl2_base[col].apply(
                lambda x: ", ".join(map(str, x)) if isinstance(x, list) else x
            )

    if "Infrastructure" in df_lvl2_base.columns:
        df_lvl2_base["Infrastructure"] = df_lvl2_base["Infrastructure"].str.strip()


except Exception as e:
    st.error(f"Error initializing data: {e}")
    df_lvl2_base = pd.DataFrame()

if "saved_data" not in st.session_state:
    st.session_state.saved_data = pd.DataFrame(columns=df_lvl2_base.columns)

if "calculated_results" not in st.session_state:
    st.session_state.calculated_results = pd.DataFrame()

if "capex_df" not in st.session_state:
    st.session_state.capex_df = pd.DataFrame()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        st.session_state["gemini_client"] = client
        st.session_state["gemini_model_version"] = GEMINI_MODEL_VERSION
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        st.session_state["gemini_client"] = None
else:
    st.warning(
        "⚠️ GEMINI_API_KEY not found. AI report feature disabled. Please set the key.")
    st.session_state["gemini_client"] = None

st.set_page_config(
    page_title="NATURE-DEMO's Decision Support Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
<style>
/* ── Google Font (Inter) ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design tokens — Forest Nature theme ────────────────────────────────── */
:root {
    --bg:         #ffffff;
    --surface:    #ffffff;
    --sidebar-bg: #1b3a2d;
    --accent:     #2d6a4f;
    --accent2:    #52b788;
    --grad:       linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #52b788 100%);
    --text:       #1a2e1f;
    --muted:      #5a7a65;
    --border:     #d8e8df;
    --shadow-sm:  0 1px 3px rgba(27,67,50,.08), 0 1px 2px rgba(27,67,50,.05);
    --shadow-md:  0 4px 14px rgba(27,67,50,.10), 0 2px 4px rgba(27,67,50,.06);
    --r:          10px;
    --r-lg:       14px;
}

/* ── Global base ─────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* 4 px gradient accent bar at the top */
[data-testid="stHeader"] {
    background: var(--grad) !important;
    height: 4px !important;
    min-height: 4px !important;
}

[data-testid="stHeader"] {
    z-index: 999;
}

/* ── Main content area ───────────────────────────────────────────────────── */
[data-testid="stMainBlockContainer"],
.main .block-container {
    position: relative;
    z-index: 1;
    background: transparent;
    padding: 1.6rem 2.6rem 3rem !important;
    max-width: 1440px;
}



/* ── SIDEBAR ── */
/* ── SIDEBAR ── */
[data-testid="stSidebar"] { 
    /* Gradient starts at Gray (#707070) and ends at your Green (#3a6e3a) */
    background: linear-gradient(180deg, #707070 0%, #3a6e3a 100%) !important; 
    background-attachment: fixed !important;
}

[data-testid="stSidebar"] * { 
    /* Brightened text for better contrast against the gray top */
    color: #fdfdfd !important; 
}

[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 7px !important;
    color: #ffffff !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}

[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(255,255,255,0.25) !important;
}

.sb-rule { 
    border: none; 
    border-top: 1px solid rgba(255,255,255,0.2); 
    margin: 0.8rem 0; 
}

.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.6) !important;
    margin: 0.9rem 0 0.35rem !important;
}

.sb-doc-link {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 0.45rem 0 0.6rem;
    transition: color 0.15s;
    letter-spacing: 0.01em;
}

.sb-doc-link:hover {
    color: #ffffff !important;
}

.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    text-decoration: none !important;
    color: #e0eee0 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #ffffff !important; }
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(180,230,160,0.3) !important;
    border-radius: 7px !important;
    color: #e0f0e0 !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(180,230,160,0.18) !important;
}
.sb-rule { border: none; border-top: 1px solid rgba(180,230,160,0.2); margin: 0.8rem 0; }
.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(180,230,160,0.55) !important;
    margin: 0.9rem 0 0.35rem !important;
}
.sb-doc-link {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: rgba(210,240,210,0.85) !important;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 0.45rem 0 0.6rem;
    transition: color 0.15s;
    letter-spacing: 0.01em;
}
.sb-doc-link:hover {
    color: #e8f6e8 !important;
    text-decoration: none !important;
}
.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(180,230,160,0.12);
    text-decoration: none !important;
    color: #c8e0c8 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #e8f6e8 !important; }

/* ── Typography ──────────────────────────────────────────────────────────── */
h1 {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}
h2 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    border-bottom: 2px solid var(--border);
    padding-bottom: 6px;
    margin-top: 1.4rem !important;
}
h3 {
    font-size: 1.02rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}
h4, h5 {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em !important;
}

/* ── Cards — st.container(border=True) ──────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1rem 1.3rem !important;
    margin-bottom: 0.9rem !important;
    transition: box-shadow .2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--shadow-md) !important;
}

/* ── Expanders ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1rem !important;
}

/* ── Native st.tabs ──────────────────────────────────────────────────────── */
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    letter-spacing: 0.01em;
}
button[data-baseweb="tab"][aria-selected="true"]
    > div[data-testid="stMarkdownContainer"] > p {
    color: var(--accent) !important;
}
button[data-baseweb="tab"] {
    padding: 8px 18px !important;
    border-bottom: 2px solid transparent !important;
    transition: border-color .15s, background .15s;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(45,106,79,.07) !important;
    border-radius: 6px 6px 0 0 !important;
}

/* ── sac.steps navigation ────────────────────────────────────────────────── */
.ant-steps-item-finish .ant-steps-item-icon,
.ant-steps-item-process .ant-steps-item-icon {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}
.ant-steps-item-title { font-size: 0.88rem !important; font-weight: 600 !important; }

/* ── Primary buttons ─────────────────────────────────────────────────────── */
[data-testid="baseButton-primary"],
button[kind="primary"] {
    background: var(--grad) !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    letter-spacing: 0.02em;
    box-shadow: 0 2px 8px rgba(45,106,79,.28) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
[data-testid="baseButton-primary"]:hover,
button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 16px rgba(45,106,79,.38) !important;
}
/* ── PRIMARY BUTTON ── */
.nd-launch-btn {
    display: inline-block;
    background: #2e6b2e;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 0.85rem 2.4rem;
    border-radius: 9px;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    box-shadow: 0 2px 10px rgba(46,107,46,0.28);
    transition: background 0.18s, transform 0.15s;
    margin-bottom: 0.75rem;
}
.nd-launch-btn:hover {
    background: #1a3a1a;
    transform: translateY(-1px);
    color: #c4dcc4 !important;
    text-decoration: none !important;
}

/* ── Secondary buttons ───────────────────────────────────────────────────── */
[data-testid="baseButton-secondary"],
button[kind="secondary"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    transition: border-color .15s, background .15s;
}
[data-testid="baseButton-secondary"]:hover,
button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    background: rgba(45,106,79,.04) !important;
}

/* ── Text / number inputs ────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    border-radius: var(--r) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    font-size: 0.87rem !important;
    transition: border-color .15s, box-shadow .15s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,.14) !important;
    outline: none !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 12px 18px;
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetricValue"] {
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
}

/* ── Dataframe / data-editor ─────────────────────────────────────────────── */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border-radius: var(--r) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

/* ── st.status widget ────────────────────────────────────────────────────── */
[data-testid="stStatus"] {
    border-radius: var(--r) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm);
}

/* ── Alert boxes (info / warning / success / error) ─────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--r) !important;
    border-left-width: 4px !important;
    font-size: 0.875rem !important;
}

/* ── Horizontal rules ────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.2rem 0 !important;
}

/* ── Slim, modern scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #52b788; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #2d6a4f; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] .stLinkButton > a {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(180,230,160,0.3) !important;
    border-radius: 7px !important;
    color: #e0f0e0 !important;
    font-size: 0.82rem !important;
    transition: background 0.18s !important;
}
[data-testid="stSidebar"] .stLinkButton > a:hover {
    background: rgba(180,230,160,0.18) !important;
}
.sb-rule { border: none; border-top: 1px solid rgba(180,230,160,0.2); margin: 0.8rem 0; }
.sb-section {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(180,230,160,0.55) !important;
    margin: 0.9rem 0 0.35rem !important;
}
.sb-doc-link {
    display: block;
    text-align: center;
    text-decoration: none !important;
    color: rgba(210,240,210,0.85) !important;
    font-size: 0.8rem;
    font-weight: 400;
    padding: 0.45rem 0 0.6rem;
    transition: color 0.15s;
    letter-spacing: 0.01em;
}
.sb-doc-link:hover {
    color: #e8f6e8 !important;
    text-decoration: none !important;
}
.sb-link {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(180,230,160,0.12);
    text-decoration: none !important;
    color: #c8e0c8 !important;
    font-size: 0.8rem;
    transition: color 0.15s;
}
.sb-link:last-child { border-bottom: none; }
.sb-link:hover { color: #e8f6e8 !important; }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    try:
        st.image(LOGO_URL, use_container_width=True)
    except Exception:
        st.markdown("**NATURE-DEMO**")

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Tools</p>', unsafe_allow_html=True)

    # Main DST button — Integrated DST (has documentation)
    st.link_button("🌿  NATURE-DEMO's DST", "/integrated_dst",
                   use_container_width=True)
    st.markdown(f"""
    <a class="sb-doc-link" href="{DOCS_URL}" target="_blank">
        📖&nbsp; Documentation
    </a>
    """, unsafe_allow_html=True)

    # Climate Data Visualisation button + docs
    st.link_button("🌡️  Climate Data Visualisation",
                   "https://naturedemo-clima-ind.dic-cloudmate.eu", use_container_width=True)
    st.markdown(f"""
    <a class="sb-doc-link" href="{CLIMA_DOCS_URL}" target="_blank">
        📖&nbsp; Documentation
    </a>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown('<p class="sb-section">Resources</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0 0.1rem;">
        <a class="sb-link" href="https://www.nature-demo.eu" target="_blank">🌐&nbsp; Project Website</a>
        <a class="sb-link" href="https://github.com/NATURE-DEMO/Decision_Support_Tool" target="_blank">⌨️&nbsp; GitHub</a>
        <a class="sb-link" href="https://nature-demo.eu/contact" target="_blank">📧&nbsp; Contact</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.66rem; color:rgba(180,230,160,0.4) !important; line-height:1.65; padding:0 0.1rem;">
        Horizon Europe · Grant 101157448<br>© 2026 NATURE-DEMO Consortium
    </p>
    """, unsafe_allow_html=True)


col1, col2 = st.columns([4, 3])
with col1:
    st.title("NATURE-DEMO's Decision Support Tool")

with col2:
    st.markdown("""
    <style>
    .tooltip-container {
        position: relative;
        display: inline-block;
    }

    .tooltip-container .tooltip-text {
        visibility: hidden;
        width: 260px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        top: 100%; 
        left: 50%;
        margin-left: -130px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 13px;
    }

    .tooltip-container:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>

    <div class="tooltip-container">
        <a href="/Specific_Site_DST_v2" class="nd-launch-btn">
            🔍 High Resolution DST &nbsp;→
        </a>
        <div class="tooltip-text">
            This part of the Platform requires an account and would enable access to pre-evaluated demo sites with their high-resolution analysis. 
            Future upgrades to this NATURE-DEMO's DST will allow saving your own data!
        </div>
    </div>
    """, unsafe_allow_html=True)


selected_step = sac.steps(
    items=[
        sac.StepsItem(title="Extraction",
                      subtitle="Mapping & Data", icon="geo-alt"),
        sac.StepsItem(title="Level 1",
                      subtitle="Perceived Risks", icon="1-circle"),
        sac.StepsItem(title="Level 2",
                      subtitle="Technical Analysis", icon="2-circle"),
    ],
    format_func="title",
    placement="horizontal",
    size="large",
    variant="navigation",
    color="dark",
    return_index=True,
)

if selected_step == 0:
    st.header("Select Infrastructure Types")
    all_infra_keys = list(infra_options.keys())

    infra_icon_map = {
        "roads & highways": "car-front",
        "railways": "train-lightrail",
        "bridges": "bezier2",
        "tunnels": "circle-half",
        "dams & water storage": "droplet-half",
        "urban green spaces": "tree",
        "embankments & levees": "moisture",
        "slope stabilization": "shield",
        "buildings": "building",
        "power & utilities": "lightning",
        "water bodies & rivers": "water",
        "catchment surface cover": "map",
    }

    selected_infras = sac.chip(
        items=[
            sac.ChipItem(label=k, icon=infra_icon_map.get(k.lower(), "gear"))
            for k in all_infra_keys
        ],
        label="Choose Infrastructure for Analysis:",
        multiple=True,
        variant="outline",
        color="blue",
        key="infra_chip_selector",
    )

    if len(selected_infras) > 5:
        st.warning(
            "⚠️ Selecting many infrastructure types may cause timeouts for large areas.")

    st.header("Search Location and Draw Polygon")
    search_col, _ = st.columns([3, 1])

    with search_col:
        location_name = st.text_input(
            "Search for a location to center the map:", value="Berlin, Germany"
        )
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

    center_lat_map = st.session_state["map_center"][0]
    center_lon_map = st.session_state["map_center"][1]
    map_object = build_base_map(
        center_lat_map, center_lon_map, st.session_state["map_zoom"])

    output = st_folium(
        map_object,
        height=600,
        width=1200,
        key=f"main_map_{st.session_state['drawing_key']}",
        returned_objects=["last_active_drawing"],
    )

    if output and output.get("last_active_drawing"):
        geom = output["last_active_drawing"].get("geometry")
        if geom and geom.get("type") in ["Polygon", "Rectangle"]:
            if st.session_state["last_polygon"] != output["last_active_drawing"]:
                st.session_state["last_polygon"] = output["last_active_drawing"]
                st.session_state["extract_clicked"] = False
        elif geom is None or geom.get("coordinates") is None:
            st.session_state["last_polygon"] = None

    st.markdown("---")
    button_col, reset_col, _ = st.columns([2, 1, 3])

    with button_col:
        if st.button(
            "Extract Information",
            type="primary",
            key="extract_btn",
            help="Trigger data extraction and AI report generation.",
        ):
            if st.session_state["last_polygon"] is None:
                st.error("Please draw a polygon on the map first.")
            else:
                st.session_state["extract_clicked"] = True
                st.session_state["extracted_data"] = None

    with reset_col:
        if st.button(
            "Reset Polygon",
            help="Clear the current drawn polygon.",
            key="reset_poly_btn",
        ):
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
                with st.status(
                    "Extracting and analyzing regional data...", expanded=True
                ) as status:
                    st.write("🌍 Fetching OpenStreetMap data...")
                    response = make_overpass_request(query)
                    if response is None or response.status_code != 200:
                        st.session_state["extract_clicked"] = False
                        st.stop()
                    data = response.json()
                    elements = data.get("elements", [])

                    if not elements:
                        st.warning(
                            "No data found in the selected area for the chosen types.")

                    st.write("🗺️ Analyzing climate map data...")
                    _, center_koppen_code = generate_koppen_map_plot(
                        center_lat, center_lon)
                    filtered_elements = []
                    seen_ids = set()
                    for infra in selected_infras:
                        for element in elements:
                            eid = (element.get("type"), element.get("id"))
                            if eid in seen_ids:
                                continue
                            tags = element.get("tags", {})
                            for filter_str in infra_options[infra]:
                                m = re.search(
                                    r'\["(.+?)"(?:="(.+?)")?\]', filter_str)
                                if m:
                                    k, v = m.groups()
                                    if k in tags and (v is None or tags[k] == v):
                                        filtered_elements.append(element)
                                        seen_ids.add(eid)
                                        break
                    st.session_state["selected_infras_for_report"] = selected_infras

                    context_report = ""
                    if st.session_state.get("gemini_client"):
                        st.write("🤖 Generating AI Context Report...")
                        context_report = generate_context_report(
                            center_lat,
                            center_lon,
                            area_sq_km,
                            filtered_elements,
                            selected_infras,
                        )

                    koppen_report = ""
                    if st.session_state.get("gemini_client"):
                        st.write(
                            "🌡️ Generating Köppen Climate Interpretation...")
                        koppen_report = generate_koppen_interpretation(
                            center_koppen_code)

                    status.update(label="Extraction Complete!",
                                  state="complete", expanded=False)

                st.session_state["extracted_data"] = {
                    "elements": elements,
                    "coords": coords,
                    "area_sq_km": area_sq_km,
                    "context_report": context_report,
                    "koppen_report": koppen_report,
                    "koppen_code": center_koppen_code,
                    "center_lat": center_lat,
                    "center_lon": center_lon,
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
                    f"Successfully processed {len(elements)} OSM items (Area: {area_sq_km:.4f} km²)"
                )

            with st.container(border=True):
                st.subheader("Geographical & Infrastructure Context Report")
            if context_report:
                render_ai_header(
                    "Geographical & Infrastructure Context Report")
                with st.expander(
                    "📊 View Raw Infrastructure Data Fed to AI (OpenStreetMap)",
                    expanded=False,
                ):
                    st.caption(
                        "This is the underlying tabular data that was provided to the AI model for analysis."
                    )
                    has_raw_data = False
                    for infra in selected_infras:
                        infra_elements = []
                        for element in elements:
                            tags = element.get("tags", {})
                            for filter_str in infra_options[infra]:
                                match = re.search(
                                    r'\["(.+?)"(?:="(.+?)")?\]', filter_str)
                                if match:
                                    k, v = match.groups()
                                    if k in tags and (v is None or tags[k] == v):
                                        infra_elements.append(element)
                                        break
                        if infra_elements:
                            has_raw_data = True
                            infra_df = create_detailed_dataframe(
                                infra_elements)
                            st.subheader(
                                f"{infra} ({len(infra_elements)} items)")
                            st.dataframe(
                                infra_df[
                                    [c for c in infra_df.columns if not c.startswith(
                                        "geometry")]
                                ].head(15)
                            )

                    if not has_raw_data:
                        st.info(
                            "No detailed data to display for the selected infrastructure types."
                        )
                st.markdown(context_report)
                render_ai_footer()
            else:
                st.warning(
                    "The Geographical & Infrastructure Report failed to generate or the AI feature is disabled."
                )

            with st.container(border=True):
                st.subheader(
                    "Köppen-Geiger Climate Classification Map (Visual)")

            if center_lat is not None and center_lon is not None:
                plot_result, _ = generate_koppen_map_plot(
                    center_lat, center_lon)

                if isinstance(plot_result, str):
                    st.error(plot_result)
                else:
                    st.pyplot(plot_result)
            else:
                st.warning(
                    "Cannot display Köppen map: Center coordinates for the drawn polygon could not be determined."
                )

            with st.container(border=True):
                st.subheader("Climate Interpretation Report")
            if koppen_report:
                render_ai_header("Köppen-Geiger Climate Interpretation Report")
                with st.expander(
                    "📊 View Raw Data Fed to AI (Köppen Climate Code)", expanded=False
                ):
                    st.caption(
                        "This is the climate classification code extracted from the Köppen-Geiger map that was provided to the AI model."
                    )
                    koppen_code_display = st.session_state["extracted_data"].get(
                        "koppen_code", "N/A"
                    )
                    st.markdown(
                        f"**Köppen Climate Code:** `{koppen_code_display}`")
                    st.markdown(
                        "The code was derived from the Köppen-Geiger Climate Classification raster (1991–2020) based on the centroid of your selected polygon."
                    )
                st.markdown(koppen_report)
                render_ai_footer()
            else:
                st.warning(
                    "The Climate Interpretation Report failed to generate or the AI feature is disabled."
                )

            with st.expander("View Extracted Infrastructure Data Tables (OpenStreetMap Raw Data)"):
                st.info(
                    "The raw OpenStreetMap data tables are shown inside the **'View Raw Infrastructure Data Fed to AI'** expander above, directly beneath the Context Report."
                )
    pass

elif selected_step == 1:
    st.header("Perceived Risks Assessment")
    st.subheader("1. Scope Definition")
    st.info(
        "Define the location, infrastructure, and hazard for this specific assessment.")

    has_lvl0_polygon = st.session_state.get("last_polygon") is not None
    use_previous_poly = st.checkbox(
        "Use same polygon from 'Information Extraction and Mapping' section",
        value=has_lvl0_polygon,
        disabled=not has_lvl0_polygon,
    )

    if use_previous_poly and has_lvl0_polygon:
        lvl1_poly = st.session_state["last_polygon"]
        lvl1_center = st.session_state["map_center"]
        lvl1_zoom = st.session_state["map_zoom"]
    else:
        lvl1_center = st.session_state.get("map_center", [51.1657, 10.4515])
        lvl1_zoom = st.session_state.get("map_zoom", 6)
        lvl1_poly = st.session_state.get("lvl1_polygon", None)

    m_lvl1 = build_folium_map_object(
        lvl1_center, lvl1_zoom, lvl1_poly, "lvl1_draw_key")

    if use_previous_poly and has_lvl0_polygon:
        with st.expander("🗺️ View / Edit Polygon", expanded=False):
            lvl1_map_output = st_folium(
                m_lvl1, height=400, width=1200, key="lvl1_map_editor")
    else:
        lvl1_map_output = st_folium(
            m_lvl1, height=400, width=1200, key="lvl1_map_editor")

    if lvl1_map_output and lvl1_map_output.get("last_active_drawing"):
        drawing = lvl1_map_output["last_active_drawing"]
        if drawing.get("geometry"):
            st.session_state["lvl1_polygon"] = drawing
            coords = drawing["geometry"]["coordinates"][0]
            lats = [c[1] for c in coords]
            lons = [c[0] for c in coords]
            st.session_state["lvl1_bbox"] = [
                min(lats), min(lons), max(lats), max(lons)]

    col_scope1, col_scope2 = st.columns(2)
    with col_scope1:
        if not df_lvl2_base.empty and "Infrastructure" in df_lvl2_base.columns:
            dynamic_infras = sorted(
                df_lvl2_base["Infrastructure"].unique().tolist())
        else:
            dynamic_infras = [
                "Road", "Railway", "Tunnels", "Bridges", "green spaces",
                "Dams", "River training infrastructure", "Torrent control infrastructure"
            ]

        selected_infra_type = st.selectbox(
            "Select Infrastructure Type",
            options=dynamic_infras,
        )
    with col_scope2:
        selected_hazard_type = st.selectbox(
            "Select Climate Driver", options=climate_drivers)

    if not df_lvl2_base.empty and "Infrastructure" in df_lvl2_base.columns:
        filtered_df_lvl1 = df_lvl2_base[df_lvl2_base["Infrastructure"]
                                        == selected_infra_type]
        available_impact_models = sorted(
            filtered_df_lvl1["Impact model"].dropna().unique().tolist())
        available_assets = sorted(
            filtered_df_lvl1["Asset"].dropna().unique().tolist())
    else:
        available_impact_models = []
        available_assets = []

    all_hazards_list_lvl1 = [
        "Extreme high temperatures (Heatwave)", "Extreme cold temperatures (Coldwave, cold snap)",
        "Drought", "Wildfire (Forest fire or Bush fire)", "Desertification",
        "Storms & strong winds", "Hail", "Aeolian erosion",
        "Pluvial flood, heavy rainfall and surface runoff", "Fluvial flood",
        "Coastal flood (e.g. storm surge)", "Impact floods and Tsunami",
        "Fluvial sediment transport", "Stream bank & bed erosion",
        "Sheet erosion & rill erosion", "Gully erosion",
        "Coastal and shoreline erosion (includes freshwater environments)",
        "Debris flood (Volumetric Sediment Concentration 20-40%)",
        "Debris flow (Volumetric Sediment Concentration >40%)",
        "Small Rockfall (Diameter <25cm)", "Large Rockfall (Diameter >25-100 cm)",
        "Landslides < 2 m depth", "Landslides 2-10 m depth", "Landslides > 10 m depths",
        "Mud or Earth flow", "Soil slope deformation & Soil creep",
        "Snow avalanches", "Snow drift", "Snow creep & slide",
    ]

    col_lvl1_a, col_lvl1_b, col_lvl1_c = st.columns(3)

    with col_lvl1_a:
        selected_impact_model = st.selectbox(
            "Select Impact Model", options=available_impact_models)
    with col_lvl1_b:
        selected_asset = st.selectbox("Select Asset", options=available_assets)
    with col_lvl1_c:
        selected_hazards_lvl1 = st.multiselect(
            "Select Possible Hazards", options=all_hazards_list_lvl1)

    dynamic_primaries = set()
    dynamic_supportives = set()
    nbs_db = NbS_list if isinstance(NbS_list, dict) else (
        NbS_list[0] if isinstance(NbS_list, list) and len(NbS_list) > 0 else {})

    if selected_hazards_lvl1:
        for h in selected_hazards_lvl1:
            if h in nbs_db:
                dynamic_primaries.update(nbs_db[h].get("Yes", []))
                dynamic_supportives.update(nbs_db[h].get("Supportive", []))

    col_lvl1_d, col_lvl1_e = st.columns(2)
    with col_lvl1_d:
        selected_primary_nbs = st.multiselect(
            "Select Primary NbS Solutions", options=sorted(list(dynamic_primaries)))
    with col_lvl1_e:
        selected_supportive_nbs = st.multiselect(
            "Select Supportive NbS Solutions", options=sorted(list(dynamic_supportives)))

    if "lvl1_added_items" not in st.session_state:
        st.session_state["lvl1_added_items"] = pd.DataFrame(columns=[
            "Infrastructure", "Climate driver", "Asset", "Impact model", "Possible Hazards", "NbS Type", "NbS Solution"
        ])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➕ Add to Scope Table", type="primary", use_container_width=True):
        if selected_impact_model and selected_asset:
            hazards_str = ", ".join(
                selected_hazards_lvl1) if selected_hazards_lvl1 else "None"
            base_row = {
                "Infrastructure": selected_infra_type,
                "Climate driver": selected_hazard_type,
                "Asset": selected_asset,
                "Impact model": selected_impact_model,
                "Possible Hazards": hazards_str,
            }

            new_rows = []

            if not selected_primary_nbs and not selected_supportive_nbs:
                row = base_row.copy()
                row["NbS Type"] = "None"
                row["NbS Solution"] = "None"
                new_rows.append(row)
            else:

                for nbs in selected_primary_nbs:
                    row = base_row.copy()
                    row["NbS Type"] = "Primary"
                    row["NbS Solution"] = nbs
                    new_rows.append(row)

                for nbs in selected_supportive_nbs:
                    row = base_row.copy()
                    row["NbS Type"] = "Supportive"
                    row["NbS Solution"] = nbs
                    new_rows.append(row)

            new_rows_df = pd.DataFrame(new_rows)
            st.session_state["lvl1_added_items"] = pd.concat(
                [st.session_state["lvl1_added_items"], new_rows_df], ignore_index=True)
            st.toast(
                f"Added {len(new_rows)} item(s) to the scope table!", icon="✅")
        else:
            st.warning(
                "Please ensure both an Impact Model and an Asset are available and selected.")

    if not st.session_state["lvl1_added_items"].empty:
        display_df = st.session_state["lvl1_added_items"].copy()
        if "Risk Score" in display_df.columns:
            display_df = display_df.drop(columns=["Risk Score"])

        selection_event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            key="lvl1_scope_table"
        )

        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])

        with btn_col1:
            if st.button("❌ Remove Selected", type="secondary", use_container_width=True):
                selected_indices = selection_event.selection.rows
                if selected_indices:
                    st.session_state["lvl1_added_items"] = st.session_state["lvl1_added_items"].drop(
                        selected_indices).reset_index(drop=True)
                    st.rerun()
                else:
                    st.warning(
                        "Please select at least one row by clicking the checkbox on the left side of the table.")

        with btn_col2:
            if st.button("🗑️ Clear Scope Table", type="secondary", use_container_width=True):
                st.session_state["lvl1_added_items"] = pd.DataFrame(columns=[
                    "Infrastructure", "Climate driver", "Asset", "Impact model", "Possible Hazards", "NbS Type", "NbS Solution"
                ])
                st.rerun()

    st.markdown("---")
    st.subheader("Input Ratings: Risk and Loss")

    if "lvl1_added_items" not in st.session_state or st.session_state["lvl1_added_items"].empty:
        st.warning(
            "⚠️ Please add at least one item to the Scope Table above before inputting ratings.")
    else:
        scope_options = st.session_state["lvl1_added_items"].apply(
            lambda r: f"{r['Infrastructure']} | {r['Asset']} | {r['Impact model']} | {r['Climate driver']} | {r.get('NbS Solution', 'None')}", axis=1
        ).tolist()

        selected_rating_item = st.selectbox(
            "Select Scope Item to Rate:", options=scope_options)

        if "item_risk_matrices" not in st.session_state:
            st.session_state["item_risk_matrices"] = {}
        if "item_loss_matrices" not in st.session_state:
            st.session_state["item_loss_matrices"] = {}

        if selected_rating_item not in st.session_state["item_risk_matrices"]:
            initial_risk = {scenario_key: {k: 3 for k in kpis}
                            for scenario_key in scenarios}
            st.session_state["item_risk_matrices"][selected_rating_item] = pd.DataFrame(
                initial_risk, index=kpis).to_dict()

        if selected_rating_item not in st.session_state["item_loss_matrices"]:
            initial_loss = {scenario_key: {k: 3 for k in kpis}
                            for scenario_key in scenarios}
            st.session_state["item_loss_matrices"][selected_rating_item] = pd.DataFrame(
                initial_loss, index=kpis).to_dict()

        df_data = st.session_state["item_risk_matrices"][selected_rating_item]
        df = pd.DataFrame(df_data, index=kpis)
        df.index.name = "KPI / Indicator"

        st.info("Please select values between **1 (best/lowest)** and **5 (worst/highest)** from the dropdowns for each cell.")

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
                html_abbr = (
                    abbr.replace("CI_HNG", "CI<sub>HNG</sub>")
                    .replace("CI_HN", "CI<sub>HN</sub>")
                    .replace("CI_HG", "CI<sub>HG</sub>")
                    .replace("CI_H", "CI<sub>H</sub>")
                    .replace("CI", "CI")
                )
                st.markdown(f"**{html_abbr}** ({desc})",
                            unsafe_allow_html=True)

        with matrix_tab:
            risk_column_config = {
                "KPI / Indicator": st.column_config.TextColumn("KPI / Indicator", disabled=True)
            }
            for key, desc in scenarios.items():
                risk_column_config[key] = st.column_config.SelectboxColumn(
                    label=key,
                    help=desc,
                    options=[1, 2, 3, 4, 5, "Not Available"],
                    default=3,
                    width="small",
                    required=True,
                )

            st.markdown(
                "### 1. Risk Rating (Critical infrastructure Condition)")

            with st.form("risk_rating_form"):
                risk_edited_df = st.data_editor(
                    df,
                    column_config=risk_column_config,
                    num_rows="fixed",
                    key=f"risk_matrix_editor_{selected_rating_item}",
                )
                submit_risk = st.form_submit_button("Save Risk Ratings")

            if submit_risk:
                st.session_state["item_risk_matrices"][selected_rating_item] = risk_edited_df.to_dict(
                )
                if "CI_HN" in risk_edited_df.columns:
                    ci_hn_series = pd.to_numeric(
                        risk_edited_df["CI_HN"], errors="coerce")
                    final_score = int(ci_hn_series.max()
                                      ) if ci_hn_series.notna().any() else 0
                else:
                    final_score = 0
                temp_df = st.session_state["lvl1_added_items"].copy()
                if "Risk Score" not in temp_df.columns:
                    temp_df["Risk Score"] = None

                # --- UPDATED: Match logic updated to find the exploded row ---
                mask = temp_df.apply(
                    lambda r: f"{r['Infrastructure']} | {r['Asset']} | {r['Impact model']} | {r['Climate driver']} | {r.get('NbS Solution', 'None')}",
                    axis=1
                ) == selected_rating_item

                if mask.any():
                    temp_df.loc[mask, "Risk Score"] = final_score
                    st.session_state["lvl1_added_items"] = temp_df
                    st.success(
                        f"Saved! Risk Score (max CI_HN) = **{final_score}** for the selected item.")
                else:
                    st.error(
                        "Could not match the selected item back to the scope table. Please try saving again.")

                st.rerun()

            st.markdown("### 2. Extent of Loss Rating (CI)")

            df_loss_data = st.session_state["item_loss_matrices"][selected_rating_item]
            df_loss = pd.DataFrame(df_loss_data, index=kpis)
            df_loss.index.name = "KPI / Indicator"

            loss_display_columns = [
                col for col in df_loss.columns if col != "CI"]
            df_loss_display = df_loss[loss_display_columns]

            column_config_loss = {
                "KPI / Indicator": st.column_config.TextColumn("KPI / Indicator", disabled=True)
            }
            for key, desc in scenarios.items():
                if key != "CI":
                    column_config_loss[key] = st.column_config.SelectboxColumn(
                        label=key,
                        help=desc,
                        options=[1, 2, 3, 4, 5],
                        default=3,
                        width="small",
                    )

            with st.form("loss_rating_form"):
                loss_edited_df_display = st.data_editor(
                    df_loss_display,
                    column_config=column_config_loss,
                    num_rows="fixed",
                    key=f"loss_matrix_editor_{selected_rating_item}",
                )
                submit_loss = st.form_submit_button("Save Loss Ratings")

            if submit_loss:
                if "CI" in df_loss.columns:
                    ci_column_original = df_loss["CI"].copy()
                    reconstructed_df_loss = loss_edited_df_display.assign(
                        CI=ci_column_original)
                    st.session_state["item_loss_matrices"][selected_rating_item] = reconstructed_df_loss.to_dict(
                    )
                else:
                    st.session_state["item_loss_matrices"][selected_rating_item] = loss_edited_df_display.to_dict(
                    )
                st.success(f"Loss Ratings saved for: {selected_rating_item}")
                st.rerun()

        st.markdown("---")
        st.subheader(
            f"Radar Plot of Input Risks: {selected_rating_item.split(' | ')[0]}")

        df_risk_current = pd.DataFrame(
            st.session_state["item_risk_matrices"][selected_rating_item], index=kpis)

        try:
            kpis_for_plot = df_risk_current.reset_index()
        except Exception:
            kpis_for_plot = pd.DataFrame(df_risk_current).reset_index()

        available_series = kpis_for_plot.columns[1:].tolist()

        if not available_series:
            st.info("No scenario columns available to plot.")
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
                        kpis_for_plot,
                        selected_series,
                        title="Risk Radar - Risk Ratings (X)",
                    )
                    if radar_fig is None:
                        st.error(
                            "Unable to generate radar figure. Check your input format.")
                    else:
                        st.plotly_chart(radar_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Failed to create radar plot: {e}")

        st.markdown("---")
        st.subheader("Consequence Assessment Matrices (Risk vs. Loss)")
        st.caption(
            f"Showing Consequence Matrix for: **{selected_rating_item}**")

        scenarios_to_plot = ["CI_H", "CI_HG", "CI_HN", "CI_HNG"]
        plot_cols = st.columns(2)

        df_for_plot_loss = pd.DataFrame(
            st.session_state["item_loss_matrices"][selected_rating_item], index=kpis)
        df_for_plot_risk = pd.DataFrame(
            st.session_state["item_risk_matrices"][selected_rating_item], index=kpis)

        for i, scenario in enumerate(scenarios_to_plot):
            try:
                fig = create_risk_heatmap_plotly(
                    df_for_plot_risk, df_for_plot_loss, scenario, kpis
                )
                with plot_cols[i % 2]:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                with plot_cols[i % 2]:
                    st.error(
                        f"Failed to generate plot for scenario {scenario}: {e}")

        st.subheader("Summary: Assessed Risks and Scores")
        st.caption(
            "Overview of all scoped items and their calculated Risk Scores (based on the maximum CI_HN value).")

        if "lvl1_added_items" in st.session_state and not st.session_state["lvl1_added_items"].empty:
            st.dataframe(
                st.session_state["lvl1_added_items"],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No risks have been assessed yet. Add items to the Scope Table and save their risk ratings to see the summary here.")

        with st.expander("Interpretation"):
            if st.session_state.get("gemini_client"):
                if st.button(
                    "Generate Interpretation Report",
                    type="primary",
                    help="Analyze the current risk matrix using Gemini.",
                ):
                    try:
                        current_df = pd.DataFrame(
                            st.session_state["item_risk_matrices"][selected_rating_item], index=kpis)
                    except (KeyError, ValueError) as e:
                        st.error(f"Error reading risk matrix data: {e}.")
                        current_df = None

                    if current_df is not None:
                        with st.spinner("Generating Risk Matrix Interpretation (Gemini)..."):
                            interpretation_report = generate_risk_interpretation(
                                current_df, kpis, scenarios
                            )

                        st.session_state["interpretation_report"] = interpretation_report

                        st.subheader("Risk Matrix Interpretation Report")
                        if interpretation_report:
                            render_ai_header(
                                f"Risk Matrix Interpretation Report: {selected_rating_item.split(' | ')[0]}")
                            with st.expander("📊 View Raw Data Fed to AI", expanded=False):
                                st.dataframe(
                                    current_df, use_container_width=True)
                            st.markdown(interpretation_report)
                            render_ai_footer()

                elif st.session_state.get("interpretation_report"):
                    st.subheader("Risk Matrix Interpretation Report")
                    render_ai_header("Risk Matrix Interpretation Report")
                    with st.expander("📊 View Raw Data Fed to AI", expanded=False):
                        try:
                            persistent_df = pd.DataFrame(
                                st.session_state["item_risk_matrices"][selected_rating_item], index=kpis
                            )
                            st.dataframe(
                                persistent_df, use_container_width=True)
                        except Exception:
                            pass
                    st.markdown(st.session_state["interpretation_report"])
                    render_ai_footer()
            else:
                st.warning(
                    "Gemini client not initialized. AI interpretation feature disabled. Ensure GEMINI_API_KEY is available."
                )

        pass

    st.markdown("---")
    st.subheader("3. NbS Selection and Risk Mitigation")
    st.info("Evaluate potential Nature-based Solutions for your identified hazards across strategic criteria.")
    primary_sols = {}
    supp_sols = {}
    has_valid_hazards = False

    if "lvl1_added_items" in st.session_state and not st.session_state["lvl1_added_items"].empty:
        for _, row in st.session_state["lvl1_added_items"].iterrows():
            nbs_type = row.get("NbS Type", "None")
            sol = row.get("NbS Solution", "None")
            hazards_str = str(row.get("Possible Hazards", ""))

            if hazards_str != "None" and hazards_str.strip():
                has_valid_hazards = True

            if sol == "None" or not str(sol).strip():
                continue
            hazards = [h.strip() for h in hazards_str.split(
                ",") if h.strip() and h.strip() != "None"]

            if nbs_type == "Primary":
                if sol not in primary_sols:
                    primary_sols[sol] = set()
                primary_sols[sol].update(hazards)
            elif nbs_type == "Supportive":
                if sol not in supp_sols:
                    supp_sols[sol] = set()
                supp_sols[sol].update(hazards)

    if not has_valid_hazards:
        st.warning(
            "⚠️ No hazards have been identified in the Scope Table yet. Please add items to generate NbS criteria.")
    elif not primary_sols and not supp_sols:
        st.info("ℹ️ No specific NbS Solutions were added to the Scope Table. Please select and add NbS solutions above.")
    primary_sols = {sol: sorted(list(hazards))
                    for sol, hazards in primary_sols.items()}
    supp_sols = {sol: sorted(list(hazards))
                 for sol, hazards in supp_sols.items()}

    def build_lvl1_nbs_rows(sols_dict):
        rows = []
        for sol, haz_list in sorted(sols_dict.items()):
            rows.append({
                "Include": True,
                "NbS Solution": sol,
                "Addressed Hazards": ", ".join(haz_list),
                "Technical Efficacy": 3,
                "Implementation Costs": 3,
                "Implementation Time": 3,
                "Environmental Impact": 3,
                "Social Acceptance": 3
            })
        return rows

    nbs_lvl1_column_config = {
        "Include": st.column_config.CheckboxColumn("Include", width="small", default=True),
        "NbS Solution": st.column_config.TextColumn("NbS Solution", disabled=True, width="medium"),
        "Addressed Hazards": st.column_config.TextColumn("Addressed Hazards", disabled=True, width="medium"),
        "Technical Efficacy": st.column_config.SelectboxColumn("Technical Efficacy", options=[1, 2, 3, 4, 5, "Not Acceptable"], required=True, default=3),
        "Implementation Costs": st.column_config.SelectboxColumn("Implementation Costs", options=[1, 2, 3, 4, 5, "Not Acceptable"], required=True, default=3),
        "Implementation Time": st.column_config.SelectboxColumn("Implementation Time", options=[1, 2, 3, 4, 5, "Not Acceptable"], required=True, default=3),
        "Environmental Impact": st.column_config.SelectboxColumn("Environmental Impact", options=[1, 2, 3, 4, 5, "Not Acceptable"], required=True, default=3),
        "Social Acceptance": st.column_config.SelectboxColumn("Social Acceptance", options=[1, 2, 3, 4, 5, "Not Acceptable"], required=True, default=3),
    }

    if primary_sols:
        st.markdown("##### ✅ Primary NbS Solutions")
        st.caption(
            "Select the criteria that make each primary solution suitable for your project.")

        if "lvl1_primary_nbs_df" not in st.session_state or len(st.session_state["lvl1_primary_nbs_df"]) != len(primary_sols):
            st.session_state["lvl1_primary_nbs_df"] = pd.DataFrame(
                build_lvl1_nbs_rows(primary_sols))

        with st.form("lvl1_primary_nbs_form"):
            edited_primary_lvl1 = st.data_editor(
                st.session_state["lvl1_primary_nbs_df"],
                column_config=nbs_lvl1_column_config,
                hide_index=True,
                use_container_width=True,
                key="lvl1_primary_nbs_editor"
            )

            btn_col1, btn_col2, _ = st.columns([2, 2, 4])
            with btn_col1:
                save_primary = st.form_submit_button(
                    "Save Primary NbS Criteria", type="primary", use_container_width=True)
            with btn_col2:
                remove_primary = st.form_submit_button(
                    "❌ Remove Checked Rows", use_container_width=True)

            if save_primary:
                st.session_state["lvl1_primary_nbs_df"] = edited_primary_lvl1
                st.success("Primary NbS criteria saved!")
                st.rerun()

            if remove_primary:
                remaining_df = edited_primary_lvl1[~edited_primary_lvl1["Include"]].reset_index(
                    drop=True)
                st.session_state["lvl1_primary_nbs_df"] = remaining_df
                st.success("Checked rows removed!")
                st.rerun()

    show_lvl1_supp = False
    if supp_sols:
        st.markdown("<br>", unsafe_allow_html=True)
        show_lvl1_supp = st.toggle(
            "🔄 View Supportive Solutions", value=False, key="lvl1_supp_toggle")

        if show_lvl1_supp:
            st.markdown("##### 🔄 Supportive NbS Solutions")
            st.caption(
                "Select the criteria that make each supportive solution suitable for your project.")

            if "lvl1_supp_nbs_df" not in st.session_state or len(st.session_state["lvl1_supp_nbs_df"]) != len(supp_sols):
                st.session_state["lvl1_supp_nbs_df"] = pd.DataFrame(
                    build_lvl1_nbs_rows(supp_sols))

            with st.form("lvl1_supp_nbs_form"):
                edited_supp_lvl1 = st.data_editor(
                    st.session_state["lvl1_supp_nbs_df"],
                    column_config=nbs_lvl1_column_config,
                    hide_index=True,
                    use_container_width=True,
                    key="lvl1_supp_nbs_editor"
                )

                btn_col1, btn_col2, _ = st.columns([2, 2, 4])
                with btn_col1:
                    save_supp = st.form_submit_button(
                        "Save Supportive NbS Criteria", type="primary", use_container_width=True)
                with btn_col2:
                    remove_supp = st.form_submit_button(
                        "❌ Remove Checked Rows", use_container_width=True)

                if save_supp:
                    st.session_state["lvl1_supp_nbs_df"] = edited_supp_lvl1
                    st.success("Supportive NbS criteria saved!")
                    st.rerun()

                if remove_supp:
                    remaining_df = edited_supp_lvl1[~edited_supp_lvl1["Include"]].reset_index(
                        drop=True)
                    st.session_state["lvl1_supp_nbs_df"] = remaining_df
                    st.success("Checked rows removed!")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### Filtration of the Recommended NbS Solutions")
    st.info("Filter and refine NbS selection by integrating Site-Specific Feasibility (SSF), Socio-Economic acceptance (SEI), and Hazard Impact Attenuation (HIA).")

    approved_primary = set()
    if "lvl1_primary_nbs_df" in st.session_state and not st.session_state["lvl1_primary_nbs_df"].empty:
        active_primary = st.session_state["lvl1_primary_nbs_df"][
            st.session_state["lvl1_primary_nbs_df"]["Include"] == True]
        approved_primary = set(active_primary["NbS Solution"])

    approved_supportive = set()
    if "lvl1_supp_nbs_df" in st.session_state and not st.session_state["lvl1_supp_nbs_df"].empty:
        active_supp = st.session_state["lvl1_supp_nbs_df"][st.session_state["lvl1_supp_nbs_df"]["Include"] == True]
        approved_supportive = set(active_supp["NbS Solution"])

    show_lvl1_supp = st.session_state.get("lvl1_supp_toggle", False)

    _lvl1_sei_dropdown_options = sorted(
        list(approved_primary | approved_supportive))
    if "lvl1_sei_lookup" not in st.session_state:
        st.session_state.lvl1_sei_lookup = {}
    if "global_site_conditions" not in st.session_state:
        st.session_state.global_site_conditions = {
            "Slope instability": False,
            "Limited vegetation and low quality of soil": False,
            "Limited access for implementation": False,
            "Cold temperatures": False,
            "Limited water availability": False,
            "Lack of connection to major services": False,
            "Space Constraints": False,
            "Exposure to soil, water and/or air pollution": False,
            "Limitations due to high population density": False
        }

    sei_factors_list = [
        "Community Engagement", "Cultural Preferences", "Workforce Availability",
        "Economic Viability", "Long term O&M costs", "Land Ownership", "Regulatory Constraints",
    ]
    ssf_labels = {
        "Slope instability": "Unstable/Steep Slopes",
        "Limited vegetation and low quality of soil": "Poor Soil/Low Vegetation",
        "Limited access for implementation": "Difficult Site Access",
        "Cold temperatures": "Cold Temperatures / Frost Risk",
        "Limited water availability": "Water Scarcity",
        "Lack of connection to major services": "No Infrastructure/Services Access",
        "Space Constraints": "Very Limited Space",
        "Exposure to soil, water and/or air pollution": "Polluted Soil/Water/Air",
        "Limitations due to high population density": "Urban/Densely Populated Area",
    }
    if _lvl1_sei_dropdown_options:
        selected_nbs_for_sei = st.selectbox(
            "Select an NbS Solution to configure SEI factors:", _lvl1_sei_dropdown_options, key="lvl1_sei_dropdown"
        )
        if selected_nbs_for_sei not in st.session_state.lvl1_sei_lookup:
            st.session_state.lvl1_sei_lookup[selected_nbs_for_sei] = {
                f: 1 for f in sei_factors_list}
    else:
        selected_nbs_for_sei = None

    if "lvl1_ssf_lookup" not in st.session_state:
        st.session_state.lvl1_ssf_lookup = {}

    edit_ssf_toggle = st.toggle("🛠️ Customize Site-Specific Feasibility (SSF) Rules", key="lvl1_edit_ssf_toggle",
                                help="Modify the baseline assumptions for how site constraints affect each NbS method.")

    if edit_ssf_toggle:
        st.markdown("##### Edit SSF Rulebook")
        val_to_str = {100: "Highly Feasible",
                      50: "Moderately Feasible", 0: "Not Feasible"}
        str_to_val = {v: k for k, v in val_to_str.items()}

        edit_data = []
        for method in sorted(_lvl1_sei_dropdown_options):
            row_dict = {"NbS Method": method}
            for crit in ssf_labels.keys():
                crit_data = st.session_state.lvl1_ssf_lookup.get(
                    method, {}).get(crit, {})
                val = crit_data.get("Value", 100) if isinstance(
                    crit_data, dict) else 100
                row_dict[crit] = val_to_str.get(val, "Highly Feasible")
            edit_data.append(row_dict)

        if edit_data:
            col_config = {
                "NbS Method": st.column_config.TextColumn(disabled=True)}
            for crit in ssf_labels.keys():
                col_config[crit] = st.column_config.SelectboxColumn(
                    options=["Highly Feasible", "Moderately Feasible", "Not Feasible"], required=True
                )
            edited_df = st.data_editor(
                pd.DataFrame(edit_data), column_config=col_config, hide_index=True, use_container_width=True, key="lvl1_ssf_rule_editor"
            )
            for _, row in edited_df.iterrows():
                method = row["NbS Method"]
                if method not in st.session_state.lvl1_ssf_lookup:
                    st.session_state.lvl1_ssf_lookup[method] = {}
                for crit in ssf_labels.keys():
                    st.session_state.lvl1_ssf_lookup[method][crit] = {
                        "Value": str_to_val[row[crit]]}
        else:
            st.info("No identified solutions found to edit.")
        st.divider()

    with st.expander("⚙️ Configure Site Conditions & Socio-Economic Factors", expanded=True):
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            with st.container(border=True):
                st.markdown("##### 🌍 Site-Specific Conditions (SSF)")
                st.caption(
                    "These physical conditions apply globally to your specific site.")
                for crit, label in ssf_labels.items():
                    current_val = st.session_state.global_site_conditions.get(
                        crit, False)
                    val = st.toggle(
                        label,
                        value=current_val,
                        key=f"lvl1_ssf_global_cond_{crit}"
                    )
                    st.session_state.global_site_conditions[crit] = val
        with col_input2:
            with st.container(border=True):
                st.markdown("##### 👥 Socio-Economic & Institutional (SEI)")
                if selected_nbs_for_sei:
                    st.caption(
                        f"Configuring SEI factors for: **{selected_nbs_for_sei}**")
                    for f in sei_factors_list:
                        current_val = st.session_state.lvl1_sei_lookup[selected_nbs_for_sei].get(
                            f, 1)
                        val = st.select_slider(
                            f"{f}",
                            options=[1, 2, 3],
                            value=current_val,
                            key=f"lvl1_sei_{selected_nbs_for_sei}_{f}",
                            help="1: Favorable, 2: Neutral, 3: Unfavorable"
                        )
                        st.session_state.lvl1_sei_lookup[selected_nbs_for_sei][f] = val
                else:
                    st.info(
                        "Select an NbS solution from the dropdown above to configure SEI factors.")

    st.session_state.lvl1_filtered_nbs_pool = []
    low_perf_pool = []

    unique_pairs = {}
    method_to_hazards = {}
    source_df = st.session_state.get("lvl1_added_items", pd.DataFrame())

    for row_idx, row in source_df.iterrows():
        raw_pri = row.get("Risk Score", 0)
        try:
            pri_score = float(raw_pri) if raw_pri is not None and str(
                raw_pri).strip() not in ["None", ""] else 0.0
        except (ValueError, TypeError):
            pri_score = 0.0

        asset_val = str(row.get("Asset", "")).strip() or "—"
        impact_val = str(row.get("Impact model", "")).strip() or "—"
        infra_val = str(row.get("Infrastructure", "")).strip() or ""
        row_label = f"{asset_val} — {impact_val}"

        raw_hazards = str(row.get("Possible Hazards", ""))
        hazards = [h.strip() for h in raw_hazards.split(
            ",")] if raw_hazards and raw_hazards != "None" else []
        if "Primary Solutions" in row:
            p_raw = str(row.get("Primary Solutions", ""))
            row_p_sols = [s.strip() for s in p_raw.split(
                " | ") if s.strip() and s.strip() in approved_primary]
            s_raw = str(row.get("Supportive Solutions", ""))
            row_s_sols = [s.strip() for s in s_raw.split(" | ") if s.strip(
            ) and show_lvl1_supp and s.strip() in approved_supportive]
        else:
            sol = str(row.get("NbS Solution", "")).strip()
            nbs_type = str(row.get("NbS Type", "")).strip()
            row_p_sols = [
                sol] if nbs_type == "Primary" and sol in approved_primary else []
            row_s_sols = [
                sol] if nbs_type == "Supportive" and show_lvl1_supp and sol in approved_supportive else []

        all_sols = list(dict.fromkeys(row_p_sols + row_s_sols))

        for h in hazards:
            for sol in all_sols:
                pair_name = f"{sol} method for {h}"
                up_key = (row_idx, pair_name)
                is_prim = sol in row_p_sols

                if up_key not in unique_pairs:
                    unique_pairs[up_key] = {
                        "original_pri": pri_score,
                        "status": "scored",
                        "pair_name": pair_name,
                        "method_only": sol,
                        "row_label": row_label,
                        "asset": asset_val,
                        "impact_model": impact_val,
                        "infrastructure": infra_val,
                        "is_primary": is_prim,
                    }
                elif unique_pairs[up_key]["original_pri"] < pri_score:
                    unique_pairs[up_key]["original_pri"] = pri_score
                    if is_prim:
                        unique_pairs[up_key]["is_primary"] = True

                if sol not in method_to_hazards:
                    method_to_hazards[sol] = set()
                method_to_hazards[sol].add(h)

    for _, data in unique_pairs.items():
        name = data["pair_name"]
        method_base = data["method_only"]

        m_ssf_data = st.session_state.lvl1_ssf_lookup.get(method_base, {})
        method_site_conditions = st.session_state.global_site_conditions
        ssf_scores = []

        for crit in ssf_labels.keys():
            if method_site_conditions.get(crit, False):
                c_info = m_ssf_data.get(crit, {})
                val = c_info.get("Value", 100) if isinstance(
                    c_info, dict) else 100
                ssf_scores.append(val)
            else:
                ssf_scores.append(100)

        avg_ssf = sum(ssf_scores) / len(ssf_scores) if ssf_scores else 100
        method_sei_vals = st.session_state.lvl1_sei_lookup.get(
            method_base, {f: 1 for f in sei_factors_list})
        sei_scores = [100 if v == 1 else (
            50 if v == 2 else 0) for v in method_sei_vals.values()]
        avg_sei = sum(sei_scores) / len(sei_scores) if sei_scores else 100

        all_lvl1_hazards = set()
        for _, r in source_df.iterrows():
            raw_h = str(r.get("Possible Hazards", ""))
            all_lvl1_hazards.update([h.strip() for h in raw_h.split(
                ",") if h.strip() and h.strip() != "None"])

        relevant_hazards = all_lvl1_hazards

        hia_scores = []
        for haz_key in relevant_hazards:
            haz_data = nbs_db.get(haz_key, {})
            if method_base in haz_data.get("Yes", []):
                hia_scores.append(100)
            elif method_base in haz_data.get("Supportive", []):
                hia_scores.append(50)
            else:
                hia_scores.append(0)

        avg_hia = sum(hia_scores) / len(hia_scores) if hia_scores else 0
        total_score = (avg_ssf + avg_sei + avg_hia) / 3
        if total_score < 10:
            tech_eff = 1
        elif total_score <= 33.34:
            tech_eff = 2
        elif total_score < 60:
            tech_eff = 3
        elif total_score < 80:
            tech_eff = 4
        else:
            tech_eff = 5

        af = 1.0 - tech_eff / 5.0
        pri_score = data.get("original_pri", 0)
        rpri = pri_score * af

        data.update({
            "name": name, "method_only": method_base, "ssf": avg_ssf,
            "sei": avg_sei, "hia": avg_hia, "total": total_score,
            "tech_eff": tech_eff, "eff_percent": total_score, "rpri": rpri,
        })
        if total_score > 33.34:
            st.session_state.lvl1_filtered_nbs_pool.append(data)
        else:
            low_perf_pool.append(data)

    if not st.session_state.lvl1_filtered_nbs_pool:
        if unique_pairs:
            st.warning(
                "⚠️ No solutions strictly passed the 33.34% feasibility threshold. Showing all potential methods for your review.")
            st.session_state.lvl1_filtered_nbs_pool = list(
                unique_pairs.values())

    if st.session_state.lvl1_filtered_nbs_pool:
        st.markdown("---")
        st.subheader("NbS Feasibility Spider Diagram")
        df_final = pd.DataFrame(st.session_state.lvl1_filtered_nbs_pool).sort_values(
            by="total", ascending=False)
        df_final = df_final.drop_duplicates(subset=["name"])

        fig = go.Figure()
        for _, r in df_final.head(5).iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[r["ssf"], r["sei"], r["hia"], r["ssf"]],
                theta=["Site Feasibility (SSF)", "Socio-Economic (SEI)",
                       "Hazard Attenuation (HIA)", "Site Feasibility (SSF)"],
                fill="toself", name=r["name"]
            ))
        fig.update_layout(polar=dict(radialaxis=dict(
            visible=True, range=[0, 100])), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📊 View Full Site-Specific Filtration Summary", expanded=False):
            filt_config = {
                "name": st.column_config.TextColumn("NbS Method"),
                "ssf": st.column_config.ProgressColumn("SSF (%)", format="%.0f%%", min_value=0, max_value=100),
                "sei": st.column_config.ProgressColumn("SEI (%)", format="%.0f%%", min_value=0, max_value=100),
                "hia": st.column_config.ProgressColumn("HIA (%)", format="%.0f%%", min_value=0, max_value=100),
                "total": st.column_config.ProgressColumn("Final Index (%)", format="%.0f%%", min_value=0, max_value=100),
            }
            st.dataframe(df_final[["name", "ssf", "sei", "hia", "total"]],
                         column_config=filt_config, use_container_width=True, hide_index=True)

        if low_perf_pool:
            st.markdown("##### ⚠️ Threshold Analysis")
            with st.expander(f"View {len(low_perf_pool)} methods scoring 33.34% or below", expanded=False):
                for item in low_perf_pool:
                    st.warning(
                        f"**{item['name']}** is not recommended (Score: {item['total']:.1f}%).")
    st.markdown("---")
    st.markdown("#### Final NbS Recommendation Strategy")
    st.info("Ranking Based on Suitability Score (Risk Score × Suitability Index)")

    method_max_total = {}
    try:
        for data_dict in unique_pairs.values():
            m_name = str(data_dict.get("method_only", "")).strip()
            t_score = data_dict.get("total", 0.0)
            if m_name:
                if m_name not in method_max_total or t_score > method_max_total[m_name]:
                    method_max_total[m_name] = t_score
    except NameError:
        pass

    def get_si_for_method(nbs_name, row_data):
        final_index = method_max_total.get(nbs_name, 100.0)
        if final_index <= 33.34:
            return 0.0

        factors = [
            row_data.get("Technical Efficacy", 3),
            row_data.get("Implementation Costs", 3),
            row_data.get("Implementation Time", 3),
            row_data.get("Environmental Impact", 3),
            row_data.get("Social Acceptance", 3)
        ]
        for f in factors:
            if f == "Not Acceptable" or pd.isna(f):
                return 0.0

        try:
            numeric_factors = [float(f) for f in factors]
            if any(pd.isna(x) for x in numeric_factors):
                return 0.0
            sum_val = sum((6.0 - f) for f in numeric_factors)
            si = sum_val / 25.0
            return si if not pd.isna(si) else 0.0
        except Exception:
            return 0.0

    si_dict = {}
    if "lvl1_primary_nbs_df" in st.session_state and not st.session_state["lvl1_primary_nbs_df"].empty:
        for _, row in st.session_state["lvl1_primary_nbs_df"].iterrows():
            if row.get("Include"):
                m_name = str(row.get("NbS Solution", "")).strip()
                si_dict[m_name] = get_si_for_method(m_name, row)

    if "lvl1_supp_nbs_df" in st.session_state and not st.session_state["lvl1_supp_nbs_df"].empty:
        for _, row in st.session_state["lvl1_supp_nbs_df"].iterrows():
            if row.get("Include"):
                m_name = str(row.get("NbS Solution", "")).strip()
                si_dict[m_name] = get_si_for_method(m_name, row)
    for item in st.session_state.lvl1_filtered_nbs_pool:
        m_name = item.get("method_only", "")
        item["si"] = si_dict.get(m_name, 0.0)
        item["suitability_score"] = item.get("original_pri", 0.0) * item["si"]

    if st.session_state.lvl1_filtered_nbs_pool:
        df_strat = pd.DataFrame(st.session_state.lvl1_filtered_nbs_pool)

        df_table = df_strat[[
            "infrastructure", "asset", "impact_model", "method_only",
            "original_pri", "si", "suitability_score"
        ]].copy()

        df_table.rename(columns={
            "infrastructure": "Infrastructure",
            "asset": "Asset",
            "impact_model": "Impact model",
            "method_only": "NbS Solution",
            "original_pri": "Risk Score",
            "si": "Suitability Index (SI)",
            "suitability_score": "Suitability Score (NbS)"
        }, inplace=True)

        df_table = df_table.drop_duplicates().reset_index(drop=True)

        st.dataframe(
            df_table,
            column_config={
                "Suitability Index (SI)": st.column_config.NumberColumn(format="%.3f"),
                "Suitability Score (NbS)": st.column_config.NumberColumn(format="%.2f"),
                "Risk Score": st.column_config.NumberColumn(format="%.1f")
            },
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        def get_dynamic_color_si(score_val, min_val, max_val):
            if max_val == min_val:
                return "#1b5e20"
            norm = (score_val - min_val) / (max_val -
                                            min_val) if max_val != min_val else 1
            if norm >= 0.8:
                return "#1b5e20"
            elif norm >= 0.6:
                return "#2e7d32"
            elif norm >= 0.4:
                return "#aed581"
            elif norm >= 0.2:
                return "#ffb74d"
            else:
                return "#d32f2f"

        def render_suitability_ranking(pool, solution_filter="primary", show_row_badge=False):
            """
            pool: list of data dicts
            solution_filter: "primary", "supportive", or "all"
            """
            cons = {}
            for item in pool:
                is_p = item.get("is_primary", False)
                if solution_filter == "primary" and not is_p:
                    continue
                if solution_filter == "supportive" and is_p:
                    continue
                m = item["method_only"]
                if m not in cons or item.get("suitability_score", 0) > cons[m].get("suitability_score", 0):
                    cons[m] = item

            scored = sorted(
                [i for i in cons.values() if i["status"] == "scored"],
                key=lambda x: x["suitability_score"],
                reverse=True
            )

            if not scored:
                st.info(
                    f"No {solution_filter} solutions found for this selection.")
                return

            valid_vals = [i["suitability_score"] for i in scored]
            mn, mx = (min(valid_vals), max(valid_vals)
                      ) if valid_vals else (0, 0)

            for rank, item in enumerate(scored, 1):
                bg = get_dynamic_color_si(item["suitability_score"], mn, mx)
                tc = "black" if bg in ["#fff176",
                                       "#ffb74d", "#aed581"] else "white"
                score_val = item.get("suitability_score", 0.0)
                type_tag = ""
                if solution_filter == "all":
                    is_p = item.get("is_primary", False)
                    t_color = "#2d6a4f" if is_p else "#1565c0"
                    t_label = "Primary" if is_p else "Supportive"
                    type_tag = f'<span style="background:{t_color};color:white;border-radius:4px;padding:1px 6px;font-size:0.7em;margin-right:8px;vertical-align:middle;">{t_label}</span>'

                row_badge_html = ""
                if show_row_badge:
                    lbl = item.get("row_label", "")
                    if lbl:
                        row_badge_html = f'<span style="background:#e3f2fd;color:#1565c0;border-radius:4px;padding:1px 6px;font-size:0.78em;font-weight:normal;margin-left:6px;">{lbl}</span>'

                st.markdown(
                    f"""
                    <div style="
                        background:#ffffff;
                        border:1.5px solid #dee2e6;
                        border-left:5px solid {bg};
                        border-radius:8px;
                        padding:12px 16px;
                        margin-bottom:10px;
                        display:flex;
                        align-items:center;
                        gap:16px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.07);
                    ">
                      <div style="
                        background:{bg};color:{tc};
                        border-radius:50%;min-width:40px;height:40px;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:bold;font-size:18px;flex-shrink:0;">
                        {rank}
                      </div>
                      <div style="flex:1;color:#212529;">
                        <div style="font-weight:600;font-size:1em;margin-bottom:3px;">
                          {type_tag}{item["method_only"]}{row_badge_html}
                        </div>
                        <div style="font-size:0.9em;margin-bottom:2px;">
                          🔹 <b>Suitability Score:</b> {score_val:.2f} &nbsp;|&nbsp;
                          <b>Total Feasibility: {item["eff_percent"]:.1f}%</b>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("##### 🏆 Ranked NbS Solutions by Suitability Score")

        seen_labels = []
        for item in st.session_state.lvl1_filtered_nbs_pool:
            lbl = item.get("row_label", "")
            if lbl and lbl not in seen_labels:
                seen_labels.append(lbl)
        OPT_PRIMARY = "✅ All Primary Solutions"
        OPT_SUPPORTIVE = "🔄 All Supportive Solutions"
        OPT_ALL = "✨ All Solutions (Primary + Supportive)"

        view_options = [OPT_PRIMARY, OPT_SUPPORTIVE, OPT_ALL] + seen_labels

        st.info(
            "Use the selector below to view rankings. You can now view Primary, Supportive, or All solutions across the entire project scope.",
            icon="ℹ️",
        )

        selected_view = st.selectbox(
            "📋 View ranking for:", view_options, key="si_view_selector"
        )

        if selected_view == OPT_PRIMARY:
            render_suitability_ranking(
                st.session_state.lvl1_filtered_nbs_pool, solution_filter="primary", show_row_badge=True)
        elif selected_view == OPT_SUPPORTIVE:
            render_suitability_ranking(
                st.session_state.lvl1_filtered_nbs_pool, solution_filter="supportive", show_row_badge=True)
        elif selected_view == OPT_ALL:
            render_suitability_ranking(
                st.session_state.lvl1_filtered_nbs_pool, solution_filter="all", show_row_badge=True)
        else:
            row_pool = [
                item for item in st.session_state.lvl1_filtered_nbs_pool
                if item.get("row_label") == selected_view
            ]
            if row_pool:
                infra = row_pool[0].get("infrastructure", "")
                asset = row_pool[0].get("asset", "")
                imp = row_pool[0].get("impact_model", "")
                parts = [p for p in [infra, asset, imp] if p and p != "—"]
                st.markdown(
                    f'<div style="background:#f3e5f5;border-left:4px solid #7b1fa2;padding:8px 14px;border-radius:6px;margin-bottom:12px;color:#4a148c;"><strong>Row:</strong> {" &nbsp;›&nbsp; ".join(parts)}</div>',
                    unsafe_allow_html=True,
                )
            render_suitability_ranking(
                row_pool, solution_filter="all", show_row_badge=False)

    else:
        st.info("No active NbS solutions found. Ensure you have checked 'Include' and saved your criteria in the tables above.")

elif selected_step == 2:
    st.header("Infrastructure Impact & Hazard Analysis")

    infrastructure_col = "Infrastructure"
    climate_driver_col = "Climate driver"
    type_impact_col = "Type of impact"
    impact_model_col = "Impact model"
    dictionary_key_col = "Dictionary Key"

    st.subheader("1. Filter Impact Models")
    col_f1, col_f2, col_f3 = st.columns(3)

    if df_lvl2_base.empty:
        st.warning("No infrastructure definitions found.")
    else:
        with col_f1:
            unique_infrastructures = sorted(
                df_lvl2_base[infrastructure_col].unique().tolist())
            selected_infrastructures = st.multiselect(
                "Infrastructure", unique_infrastructures)
            df_filtered_infra = (
                df_lvl2_base[df_lvl2_base[infrastructure_col].isin(
                    selected_infrastructures)]
                if selected_infrastructures
                else df_lvl2_base
            )

        with col_f2:
            unique_climate_drivers = sorted(
                df_filtered_infra[climate_driver_col].unique().tolist())
            selected_climate_drivers = st.multiselect(
                "Climate Driver", unique_climate_drivers)
            df_filtered_driver = (
                df_filtered_infra[
                    df_filtered_infra[climate_driver_col].isin(
                        selected_climate_drivers)
                ]
                if selected_climate_drivers
                else df_filtered_infra
            )

        with col_f3:
            unique_types = sorted(
                df_filtered_driver[type_impact_col].unique().tolist())
            selected_types = st.multiselect("Type of Impact", unique_types)
            final_filtered_df = (
                df_filtered_driver[df_filtered_driver[type_impact_col].isin(
                    selected_types)]
                if selected_types
                else df_filtered_driver
            )

        if st.button("Add filtered items to Table", type="primary", use_container_width=True):
            if not final_filtered_df.empty:
                st.session_state.saved_data = pd.concat(
                    [st.session_state.saved_data,
                        final_filtered_df], ignore_index=True
                ).drop_duplicates()
                st.success(f"Added {len(final_filtered_df)} items.")
            else:
                st.warning("No items found to add.")

    st.divider()
    st.subheader("2. Selected Impact Models Table")

    climate_indicators = {
        "tas": "Annual mean temperature",
        "tasmax": "Annual mean maximum temperature",
        "tasmin": "Annual mean minimum temperature",
        "tn20": "Annual days with minimum temperature < -20°C",
        "tx40": "Annual days with maximum temperature > 40°C",
        "cdd": "Maximum yearly Consecutive Dry Days",
        "cwd": "Maximum yearly Consecutive Wet Days",
        "prcptot_year": "Total yearly precipitation",
        "rx1day": "Maximum 1-day precipitation",
        "rx5day": "Maximum 5-day precipitation",
        "rx1day_rp100": "100-year return level of maximum 1-day precipitation",
        "rx5day_rp100": "100-year return level of maximum 5-day precipitation",
        "solidprcptot_winter": "Winter months accumulated solid precipitation",
        "solidprcptot_year": "Annual accumulated solid precipitation",
        "hi35": "Yearly days with heat index > 35°C",
        "hurs_year": "Annual mean relative humidity",
        "vpd": "Annual mean vapor pressure deficit",
        "par_plant_level": "Photosynthetically active radiation at plant level",
        "hurs40_days": "Annual days with relative humidity under 40%",
        "spei3_severe_prob": "Annual probability of severe agricultural drought (SPEI-3)",
    }

    btn_col1, btn_col2, btn_col3, _ = st.columns([1.2, 1.4, 2.5, 3])

    with btn_col1:
        if st.button(
            "🗑️ Reset Table",
            help="Clear all selected impact models and results",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state.saved_data = pd.DataFrame(
                columns=df_lvl2_base.columns)
            st.session_state.calculated_results = pd.DataFrame()
            st.session_state.capex_df = pd.DataFrame()
            st.rerun()

    with btn_col3:
        with st.popover("➕ Add Custom Impact Model", use_container_width=True):
            st.markdown("##### Define Custom Impact Model")
            st.caption(
                "Manually define an asset and its climate sensitivity. All manual entries are recorded for AI transparency."
            )

            c1, c2 = st.columns(2)
            with c1:
                new_infra = st.selectbox(
                    "Infrastructure Category",
                    [
                        "Road",
                        "Railway",
                        "Tunnels",
                        "Bridges",
                        "green spaces",
                        "Dams",
                        "River training infrastructure",
                        "Torrent control infrastructure",
                    ],
                    key="manual_infra_sel",
                )
                new_driver = st.selectbox(
                    "Climate Driver", climate_drivers, key="manual_driver_sel"
                )
                new_impact = st.text_input(
                    "Impact Model Description",
                    placeholder="e.g., Structural buckling due to heat",
                    key="manual_impact_in",
                )

            with c2:
                new_asset = st.text_input(
                    "Specific Asset Name",
                    placeholder="e.g., Steel Rail Track",
                    key="manual_asset_in",
                )
                indicator_names = list(climate_indicators.values())
                new_indicator_name = st.selectbox(
                    "Select Climate Indicator", indicator_names, key="manual_ind_sel"
                )

            all_hazards_list = [
                "Extreme high temperatures (Heatwave)",
                "Extreme cold temperatures (Coldwave, cold snap)",
                "Drought",
                "Wildfire (Forest fire or Bush fire)",
                "Desertification",
                "Storms & strong winds",
                "Hail",
                "Aeolian erosion",
                "Pluvial flood, heavy rainfall and surface runoff",
                "Fluvial flood",
                "Coastal flood (e.g. storm surge)",
                "Impact floods and Tsunami",
                "Fluvial sediment transport",
                "Stream bank & bed erosion",
                "Sheet erosion & rill erosion",
                "Gully erosion",
                "Coastal and shoreline erosion (includes freshwater environments)",
                "Debris flood (Volumetric Sediment Concentration 20-40%)",
                "Debris flow (Volumetric Sediment Concentration >40%)",
                "Small Rockfall (Diameter <25cm)",
                "Large Rockfall (Diameter >25-100 cm)",
                "Landslides < 2 m depth",
                "Landslides 2-10 m depth",
                "Landslides > 10 m depths",
                "Mud or Earth flow",
                "Soil slope deformation & Soil creep",
                "Snow avalanches",
                "Snow drift",
                "Snow creep & slide",
            ]
            new_hazards = st.multiselect(
                "Select Possible Hazards",
                options=all_hazards_list,
                key="manual_haz_sel",
            )
            if st.button("Confirm and Add to Table", type="primary", use_container_width=True):
                if new_impact.strip() and new_asset.strip():
                    new_dict_key = [
                        k for k, v in climate_indicators.items() if v == new_indicator_name
                    ][0]

                    new_row = {
                        infrastructure_col: new_infra,
                        climate_driver_col: new_driver,
                        impact_model_col: new_impact,
                        "Asset": new_asset,
                        dictionary_key_col: new_dict_key,
                        "Type of impact": "Custom",
                        "Consequences": "Custom",
                        "Proposed climate Indicator": new_indicator_name,
                        "Possible Hazards": new_hazards,
                    }

                    st.session_state.saved_data = pd.concat(
                        [st.session_state.saved_data, pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    st.toast(
                        f"Added {new_asset} to the analysis table!", icon="✅")
                    st.rerun()
                else:
                    st.error(
                        "Please provide both an Impact Model and an Asset name.")

    if not st.session_state.saved_data.empty:
        cols_to_display = [impact_model_col,
                           infrastructure_col, dictionary_key_col]
        st.session_state.saved_data = st.session_state.saved_data.reset_index(
            drop=True)

        selection_event = st.dataframe(
            st.session_state.saved_data[cols_to_display],
            on_select="rerun",
            selection_mode="multi-row",
            use_container_width=True,
            key="impact_table_selection",
        )

        with btn_col2:
            if st.button("❌ Remove Selected", type="secondary", use_container_width=True):
                selected_indices = selection_event.selection.rows
                if selected_indices:
                    st.session_state.saved_data = st.session_state.saved_data.drop(
                        selected_indices
                    ).reset_index(drop=True)
                    st.rerun()
                else:
                    st.warning("Select rows to remove.")
    else:
        st.info(
            "Table is empty. Use filters above or add a custom impact model to populate items.")

    st.divider()
    st.subheader("3. Hazard Variation Analysis")

    URL = "https://naturedemo-clima-ind.dic-cloudmate.eu/api/calculate"

    LEVEL_TO_INDEX = {
        "No variation": 0,
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Very High": 4,
        "Extreme": 5,
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
        help="If checked, uses the center of the polygon drawn in the Information Extraction and Mapping tab.",
    )

    if use_poly_center and has_extracted_coords:
        default_lat = st.session_state["extracted_data"]["center_lat"]
        default_lon = st.session_state["extracted_data"]["center_lon"]
        input_disabled = True
    else:
        default_lat = (
            st.session_state["map_center"][0] if st.session_state["map_center"] else 50.7764
        )
        default_lon = (
            st.session_state["map_center"][1] if st.session_state["map_center"] else 6.0839
        )
        input_disabled = False

    row1_c1, row1_c2 = st.columns(2)

    with row1_c1:
        lat = st.number_input(
            "Latitude:",
            value=float(default_lat),
            format="%.4f",
            disabled=input_disabled,
        )

    with row1_c2:
        selected_scenario_label = st.radio(
            "Select Scenario:", ("RCP4.5", "RCP8.5"), horizontal=True
        )

    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        lon = st.number_input(
            "Longitude:",
            value=float(default_lon),
            format="%.4f",
            disabled=input_disabled,
        )

    with row2_c2:
        selected_term_label = st.radio(
            "Select Time Horizon:",
            ("Short Term", "Medium Term", "Long Term"),
            horizontal=True,
        )

    st.markdown(" ")
    if st.button("Calculate Hazard Variation & Level", type="primary", use_container_width=True):
        if st.session_state.saved_data.empty:
            st.error("Please add items to the table first.")
        else:
            scenario_map = {"RCP4.5": "rcp45", "RCP8.5": "rcp85"}
            term_map = {
                "Short Term": "short",
                "Medium Term": "medium",
                "Long Term": "long",
            }

            api_scenario = scenario_map[selected_scenario_label]
            api_term = term_map[selected_term_label]

            index_list = []
            level_list = []
            unique_keys = [
                k
                for k in st.session_state.saved_data[dictionary_key_col].unique()
                if k and str(k).strip() not in ("", "Not found")
            ]
            total_fetches = len(unique_keys)
            progress_bar = st.progress(0)
            status_text = st.empty()

            key_cache = {}
            for fetch_count, dict_key in enumerate(unique_keys, 1):
                status_text.caption(
                    f"Fetching climate data: **{dict_key}** ({fetch_count}/{total_fetches})"
                )
                val_selected = None
                val_historical = None
                try:
                    payload_sel = {
                        "index_type": dict_key,
                        "scenario": api_scenario,
                        "lat": lat,
                        "lon": lon,
                    }
                    resp_sel = requests.post(URL, json=payload_sel, timeout=10)
                    if resp_sel.status_code == 200 and resp_sel.json().get("status") == "success":
                        val_selected = (
                            resp_sel.json().get("results", {}).get(api_term, {}).get("value")
                        )

                    payload_hist = {
                        "index_type": dict_key,
                        "scenario": "historical",
                        "lat": lat,
                        "lon": lon,
                    }
                    resp_hist = requests.post(
                        URL, json=payload_hist, timeout=10)
                    if resp_hist.status_code == 200 and resp_hist.json().get("status") == "success":
                        val_historical = (
                            resp_hist.json().get("results", {}).get("historical", {}).get("value")
                        )
                except:
                    pass

                cached_idx, cached_lvl = 0, "No variation"
                if val_selected is not None and val_historical is not None:
                    try:
                        if val_historical == 0:
                            variation_val = 0.0 if val_selected == 0 else float(
                                "inf")
                        else:
                            variation_val = (
                                abs((val_selected - val_historical) /
                                    val_historical) * 100
                            )
                        if variation_val == 0:
                            cached_idx, cached_lvl = 0, "No variation"
                        elif variation_val == float("inf") or variation_val > 75:
                            cached_idx, cached_lvl = 5, "Extreme"
                        elif variation_val <= 10:
                            cached_idx, cached_lvl = 1, "Low"
                        elif variation_val <= 25:
                            cached_idx, cached_lvl = 2, "Medium"
                        elif variation_val <= 50:
                            cached_idx, cached_lvl = 3, "High"
                        elif variation_val <= 75:
                            cached_idx, cached_lvl = 4, "Very High"
                    except:
                        pass
                key_cache[dict_key] = (cached_idx, cached_lvl)
                progress_bar.progress(fetch_count / total_fetches)

            status_text.empty()
            for _, row in st.session_state.saved_data.iterrows():
                dict_key = row.get(dictionary_key_col)
                if (
                    dict_key
                    and str(dict_key).strip() not in ("", "Not found")
                    and dict_key in key_cache
                ):
                    final_idx, final_lvl = key_cache[dict_key]
                else:
                    final_idx, final_lvl = 0, "No variation"
                index_list.append(final_idx)
                level_list.append(final_lvl)

            result_df = st.session_state.saved_data[
                [infrastructure_col, climate_driver_col, impact_model_col]
            ].copy()

            result_df["Hazard Index"] = index_list
            result_df["Hazard Level"] = level_list
            st.session_state.calculated_results = result_df
            st.success("Calculation complete!")
            st.rerun()

    if not st.session_state.calculated_results.empty:
        st.subheader("Natural Hazards Table")
        if st.button(
            "Delete rows without climate information",
            type="primary",
            help="Permanently remove rows where Hazard Index is 0 or N/A from the dataset.",
        ):
            before_count = len(st.session_state.calculated_results)
            st.session_state.calculated_results = st.session_state.calculated_results[
                (st.session_state.calculated_results["Hazard Index"] != 0)
                & (st.session_state.calculated_results["Hazard Index"].notna())
            ].reset_index(drop=True)

            after_count = len(st.session_state.calculated_results)
            st.toast(f"Deleted {before_count - after_count} rows.", icon="🗑️")
            st.rerun()

        display_df = st.session_state.calculated_results.copy()

        old_to_new_map = {
            "⚪ No variation": "No variation",
            "🟢 Low": "Low",
            "🟡 Medium": "Medium",
            "🟠 High": "High",
            "🔴 Very High": "Very High",
            "🚨 Extreme": "Extreme",
        }
        if "Hazard Level" in display_df.columns:
            display_df["Hazard Level"] = display_df["Hazard Level"].replace(
                old_to_new_map)

        display_df["Hazard Index"] = pd.to_numeric(
            display_df["Hazard Index"], errors="coerce"
        ).fillna(0)

        column_config = {
            "Hazard Index": st.column_config.ProgressColumn(
                "Hazard Index", min_value=0, max_value=5, format="%d"
            ),
            "Hazard Level": st.column_config.SelectboxColumn(
                "Hazard Level",
                options=[
                    "No variation",
                    "Low",
                    "Medium",
                    "High",
                    "Very High",
                    "Extreme",
                ],
                required=True,
            ),
            infrastructure_col: st.column_config.TextColumn(disabled=True),
            climate_driver_col: st.column_config.TextColumn(disabled=True),
            impact_model_col: st.column_config.TextColumn(disabled=True),
            "Sensitivity Index": None,
            "Exposure Index": None,
            "Vulnerability Index": None,
            "Asset": None,
            "PRI scores": None,
            "PRI values": None,
            "Supportive Solutions": None,
            "Primary Solutions": None,
            "Possible Hazards": None,
        }

        temp_hazard_df = st.data_editor(
            display_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="hazard_editor_v3",
        )

        if st.button("Save Hazard Changes", type="primary"):
            updated = False

            for i in temp_hazard_df.index:
                old_level = display_df.loc[i, "Hazard Level"]
                new_level = temp_hazard_df.loc[i, "Hazard Level"]
                old_index = display_df.loc[i, "Hazard Index"]
                new_index = temp_hazard_df.loc[i, "Hazard Index"]

                if new_level != old_level:
                    temp_hazard_df.at[i, "Hazard Index"] = LEVEL_TO_INDEX.get(
                        new_level, 0)
                    updated = True
                elif new_index != old_index:
                    temp_hazard_df.at[i, "Hazard Level"] = INDEX_TO_LEVEL.get(
                        new_index, "Low")
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
                💡Tips: To manually adjust a hazard rating, change the 'Hazard Level' text dropdown and click 'Save Hazard Changes'. 
                The bar chart will update automatically.
            </span>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Generate Climate Hazard Report",
            type="secondary",
            use_container_width=True,
            help="Analyze the generated hazard table using Gemini.",
        ):
            with st.spinner("Generating Report from Hazard Table (Gemini)..."):
                report_text = generate_hazard_report_gemini(
                    st.session_state.calculated_results)
                st.session_state["hazard_report"] = report_text

        if st.session_state.get("hazard_report"):
            with st.expander("View Climate Hazard Report", expanded=True):
                render_ai_header("Climate Hazard Report")
                with st.expander("📊 View Raw Data Fed to AI (Hazard Table)", expanded=False):
                    tab_actual, tab_example = st.tabs(
                        ["📋 Actual Data", "📖 Example Used to Guide AI"]
                    )
                    with tab_actual:
                        st.caption(
                            "This is the hazard table that was provided to the AI model for analysis."
                        )
                        st.dataframe(
                            st.session_state.calculated_results,
                            use_container_width=True,
                        )
                    with tab_example:
                        st.caption(
                            "This is the example table and report text used as a reference to guide the AI's output style and structure."
                        )
                        st.markdown("**Example Input Table:**")
                        st.markdown(EXAMPLE_HAZARD_TABLE)
                        st.markdown("**Example Output Report:**")
                        st.markdown(EXAMPLE_HAZARD_REPORT)
                st.markdown(st.session_state["hazard_report"])
                render_ai_footer()

    st.divider()
    st.subheader("4. Exposure Index Analysis")
    st.info(
        "Determine the exposure of the assets based on their economic value (Revenue and CAPEX)."
    )

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        economic_available = st.toggle(
            "💰 Economic data for infrastructure assets are available", value=False
        )
    with col_exp2:
        use_default_thresholds = st.toggle(
            "⚙️ Use default threshold values",
            value=True,
            disabled=not economic_available,
            help="Toggle off to set custom Revenue and CAPEX thresholds.",
        )

    if "capex_df" not in st.session_state:
        st.session_state.capex_df = pd.DataFrame()

    def refresh_asset_list():
        if not st.session_state.calculated_results.empty:
            if "Asset" not in st.session_state.calculated_results.columns:
                try:
                    st.session_state.calculated_results["Asset"] = st.session_state.saved_data.loc[
                        st.session_state.calculated_results.index, "Asset"
                    ]
                except:
                    pass
            if "Asset" in st.session_state.calculated_results.columns:
                unique_assets = st.session_state.calculated_results["Asset"].unique(
                )
            else:
                unique_assets = st.session_state.saved_data["Asset"].unique()

            st.session_state.capex_df = pd.DataFrame(
                {"Exposed assets": unique_assets, "CAPEX (M€/year)": 0.0}
            )

    if st.session_state.capex_df.empty:
        refresh_asset_list()

    exposure_val = 3

    if economic_available:
        with st.container(border=True):
            col_rev, col_btn = st.columns([2, 1])
            with col_rev:
                revenue_input = st.number_input(
                    "Annual REVENUES (M€/year)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    help="Total annual revenue generated by the infrastructure.",
                )
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(
                    "🔄 Refresh Asset List",
                    use_container_width=True,
                    help="Fetch latest assets from the hazard table",
                ):
                    refresh_asset_list()

            st.markdown("##### Capital Expenditure (CAPEX) per Asset")
            if not st.session_state.capex_df.empty:
                edited_capex = st.data_editor(
                    st.session_state.capex_df,
                    column_config={
                        "Exposed assets": st.column_config.TextColumn(
                            "Exposed Asset", disabled=True
                        ),
                        "CAPEX (M€/year)": st.column_config.NumberColumn(
                            "CAPEX (M€/year)", min_value=0.0, format="%.2f M€"
                        ),
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="capex_editor",
                )
            else:
                st.warning("No assets found. Run hazards calculation first.")
                edited_capex = pd.DataFrame()

        if not use_default_thresholds:
            with st.container(border=True):
                st.markdown("##### 🎛️ Custom Threshold Boundaries")
                ct1, ct2, ct3, ct4 = st.columns(4)
                with ct1:
                    rev_low = st.number_input(
                        "Rev. Low (M€)", value=1.0, step=0.5)
                with ct2:
                    rev_high = st.number_input(
                        "Rev. High (M€)", value=2.5, step=0.5)
                with ct3:
                    cap_low = st.number_input(
                        "CAPEX Low (M€)", value=5.0, step=0.5)
                with ct4:
                    cap_high = st.number_input(
                        "CAPEX High (M€)", value=10.0, step=0.5)
        else:
            rev_low, rev_high, cap_low, cap_high = 1.0, 2.5, 5.0, 10.0

        with st.expander("📊 View Exposure Matrix Calculation Logic"):
            colors = {
                1: "#6dbf7a",
                2: "#a6d17b",
                3: "#ffeb84",
                4: "#f9a674",
                5: "#f76d6d",
            }
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

    if st.button("Calculate Exposure Indexes", type="primary", use_container_width=True):
        if economic_available and not edited_capex.empty:
            total_capex = edited_capex["CAPEX (M€/year)"].sum()
            exposure_val = calculate_exposure(
                revenue_input, total_capex, rev_low, rev_high, cap_low, cap_high
            )
            st.session_state.capex_df = edited_capex
        else:
            exposure_val = 3

        if not st.session_state.calculated_results.empty:
            st.session_state.calculated_results["Exposure Index"] = exposure_val
            st.success(f"✅ Exposure Index calculated: **{exposure_val}**")
        else:
            st.error("No impact models available to update.")

    if (
        not st.session_state.calculated_results.empty
        and "Exposure Index" in st.session_state.calculated_results.columns
    ):
        st.markdown("##### 📈 Exposure Results")

        exp_col_config = {
            "Exposure Index": st.column_config.ProgressColumn(
                "Exposure Index",
                help="Calculated Exposure score (1-5)",
                format="%d",
                min_value=0,
                max_value=5,
            ),
            "Sensitivity Index": None,
            "Vulnerability Index": None,
            "Asset": None,
            "PRI scores": None,
            "PRI values": None,
            "Hazard Index": None,
            "Hazard Level": None,
            "Possible Hazards": None,
            "Specific Hazard": None,
            "Supportive Solutions": None,
            "Primary Solutions": None,
            "Possible Hazards": None,
        }
        st.dataframe(
            st.session_state.calculated_results,
            column_config=exp_col_config,
            use_container_width=True,
        )
    st.divider()
    st.subheader("5. Vulnerability Index Analysis")

    st.info(
        "Assess vulnerability by defining the Sensitivity Index and configuring the Adaptive Capacity of each asset."
    )

    if not st.session_state.calculated_results.empty:
        if "Asset" not in st.session_state.calculated_results.columns:
            try:
                st.session_state.calculated_results["Asset"] = st.session_state.saved_data.loc[
                    st.session_state.calculated_results.index, "Asset"
                ]
            except Exception as e:
                st.error(
                    f"Error aligning asset data: {e}. Please try resetting the table.")

        if "Sensitivity Index" not in st.session_state.calculated_results.columns:
            st.session_state.calculated_results["Sensitivity Index"] = 3

        with st.container(border=True):
            st.markdown("#### Step 5.1: Define Sensitivity Index")
            st.caption(
                "Set the Sensitivity Index for each impact model. Use the dropdown in the table (1 = Low Sensitivity, 5 = High Sensitivity)."
            )

            vuln_input_df = st.session_state.calculated_results.copy()

            vuln_col_config = {
                "Sensitivity Index": st.column_config.SelectboxColumn(
                    "Sensitivity Index (1-5)",
                    options=[1, 2, 3, 4, 5],
                    required=True,
                    help="Select a value between 1 (best) and 5 (worst)",
                ),
                "Exposure Index": None,
                "Vulnerability Index": None,
                "PRI scores": None,
                "PRI values": None,
                "Hazard Index": None,
                "Hazard Level": None,
                "Supportive Solutions": None,
                "Primary Solutions": None,
                "Possible Hazards": None,
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
                key="sensitivity_editor_v2",
            )

        with st.container(border=True):
            st.markdown("#### 🛡️ Step 5.2: Adaptive Capacity Configuration")
            ac_available = st.toggle(
                "⚙️ Configure Adaptive Capacity for Assets", value=False)

            asset_ac_params = {}
            unique_assets_list = st.session_state.calculated_results["Asset"].unique(
            )

            if ac_available:
                st.caption(
                    "Configure all asset parameters in one compact table. Changes take effect when you click **Calculate Vulnerability Index**."
                )
                if "ac_editor_df" not in st.session_state or set(
                    st.session_state.ac_editor_df["Asset"].tolist()
                ) != set(unique_assets_list.tolist()):
                    st.session_state.ac_editor_df = pd.DataFrame(
                        {
                            "Asset": list(unique_assets_list),
                            "Initial AC (0-0.4)": [0.0] * len(unique_assets_list),
                            "Lifetime": ["Intermediate"] * len(unique_assets_list),
                            "Maintenance": ["Medium"] * len(unique_assets_list),
                            "Topology": ["Acceptable"] * len(unique_assets_list),
                        }
                    )

                ac_col_config = {
                    "Asset": st.column_config.TextColumn("Asset", disabled=True),
                    "Initial AC (0-0.4)": st.column_config.NumberColumn(
                        "Initial AC (0-0.4)",
                        min_value=0.0,
                        max_value=0.4,
                        step=0.01,
                        format="%.2f",
                        help="Baseline adaptive capacity. Maximum value is 0.4.",
                    ),
                    "Lifetime": st.column_config.SelectboxColumn(
                        "Lifetime",
                        options=["Greenfield", "Intermediate",
                                 "High (> 25 years)"],
                        required=True,
                    ),
                    "Maintenance": st.column_config.SelectboxColumn(
                        "Maintenance Level",
                        options=["High", "Medium", "Low"],
                        required=True,
                    ),
                    "Topology": st.column_config.SelectboxColumn(
                        "Design Topology",
                        options=["Resilient", "Acceptable", "Not acceptable"],
                        required=True,
                    ),
                }

                edited_ac_df = st.data_editor(
                    st.session_state.ac_editor_df,
                    column_config=ac_col_config,
                    hide_index=True,
                    use_container_width=True,
                    key="ac_data_editor",
                )

                for _, row in edited_ac_df.iterrows():
                    a = row["Asset"]
                    s_ac0 = row["Initial AC (0-0.4)"]
                    s_lf = row["Lifetime"]
                    s_lm = row["Maintenance"]
                    s_dt = row["Topology"]
                    v_lf = (
                        10 if s_lf == "Greenfield" else (
                            -10 if s_lf == "High (> 25 years)" else 0)
                    )
                    v_lm = 10 if s_lm == "High" else (
                        -10 if s_lm == "Low" else 0)
                    v_dt = 10 if s_dt == "Resilient" else (
                        -10 if s_dt == "Not acceptable" else 0)
                    asset_ac_params[a] = {
                        "AC0": s_ac0,
                        "lf": v_lf,
                        "lm": v_lm,
                        "dt": v_dt,
                    }

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Calculate Vulnerability Index", type="primary", use_container_width=True):
            st.session_state.calculated_results["Sensitivity Index"] = temp_edited_df[
                "Sensitivity Index"
            ]
            vulnerability_results = []

            for index, row in st.session_state.calculated_results.iterrows():
                asset_name = row["Asset"]
                sensitivity_val = row["Sensitivity Index"]

                final_ac = 0.0

                if ac_available and asset_name in asset_ac_params:
                    params = asset_ac_params[asset_name]
                    calculated_ac = params["AC0"] + (
                        (params["lf"] + params["lm"] + params["dt"]) / 100.0
                    )
                    final_ac = min(calculated_ac, 0.4)
                    final_ac = max(final_ac, 0.0)

                vuln_index = sensitivity_val * (1 - final_ac)
                vulnerability_results.append(vuln_index)

            st.session_state.calculated_results["Vulnerability Index"] = vulnerability_results
            st.success("✅ Vulnerability Index calculated successfully!")

        if "Vulnerability Index" in st.session_state.calculated_results.columns:
            st.markdown("##### 📊 Vulnerability Results")

            final_col_config = {
                "Sensitivity Index": st.column_config.NumberColumn("Sensitivity", format="%d"),
                "Vulnerability Index": st.column_config.ProgressColumn(
                    "Vulnerability Index",
                    help="Calculated Vulnerability score based on Sensitivity and AC.",
                    format="%.2f",
                    min_value=0,
                    max_value=5,
                ),
                "Exposure Index": None,
                "PRI scores": None,
                "PRI values": None,
                "Asset": None,
                "Hazard Index": None,
                "Possible Hazards": None,
                "Specific Hazard": None,
                "Hazard Level": None,
                "Supportive Solutions": None,
                "Primary Solutions": None,
                "Possible Hazards": None,
            }

            st.dataframe(
                st.session_state.calculated_results,
                column_config=final_col_config,
                use_container_width=True,
            )

    else:
        st.warning(
            "Please complete the previous sections (Filters -> Hazards -> Exposure) to generate the data for analysis."
        )
    st.divider()
    st.subheader("6. Potential Risk Index")

    if st.button(
        "Calculate the Potential Risk Index (PRI)",
        type="primary",
        use_container_width=True,
    ):
        if (
            "calculated_results" in st.session_state
            and not st.session_state.calculated_results.empty
        ):
            df_base = st.session_state.calculated_results.copy()

            if "Possible Hazards" not in df_base.columns and "saved_data" in st.session_state:
                try:
                    df_base["Possible Hazards"] = st.session_state.saved_data.loc[
                        df_base.index, "Possible Hazards"
                    ]
                except Exception:
                    pass

            hazard_col = "Hazard Index"
            exposure_col = "Exposure Index"
            vulnerability_col = "Vulnerability Index"

            required_cols = [hazard_col, exposure_col, vulnerability_col]

            if all(col in df_base.columns for col in required_cols):
                pri_scores = []
                pri_values = []

                pri_table = {
                    0: {"score": 0, "value": "NO RISK"},
                    25: {"score": 1, "value": "VERY LOW"},
                    50: {"score": 2, "value": "LOW"},
                    75: {"score": 3, "value": "MEDIUM"},
                    100: {"score": 4, "value": "HIGH"},
                    125: {"score": 5, "value": "EXTREME"},
                }
                allowed_levels = list(pri_table.keys())

                for index, row in df_base.iterrows():
                    try:
                        h = float(row[hazard_col]) if pd.notnull(
                            row[hazard_col]) else 0.0
                        v = (
                            float(row[vulnerability_col])
                            if pd.notnull(row[vulnerability_col])
                            else 0.0
                        )
                        e = float(row[exposure_col]) if pd.notnull(
                            row[exposure_col]) else 0.0
                    except ValueError:
                        h, v, e = 0.0, 0.0, 0.0

                    raw_product = h * v * e
                    lookup_key = min(
                        allowed_levels, key=lambda x: abs(x - raw_product))

                    pri_scores.append(pri_table[lookup_key]["score"])
                    pri_values.append(pri_table[lookup_key]["value"])

                df_base["PRI scores"] = pri_scores
                df_base["PRI values"] = pri_values

                st.session_state.calculated_results = df_base

                df_pri_display = df_base.copy()

                all_hazards_list = [
                    "Extreme high temperatures (Heatwave)",
                    "Extreme cold temperatures (Coldwave, cold snap)",
                    "Drought",
                    "Wildfire (Forest fire or Bush fire)",
                    "Desertification",
                    "Storms & strong winds",
                    "Hail",
                    "Aeolian erosion",
                    "Pluvial flood, heavy rainfall and surface runoff",
                    "Fluvial flood",
                    "Coastal flood (e.g. storm surge)",
                    "Impact floods and Tsunami",
                    "Fluvial sediment transport",
                    "Stream bank & bed erosion",
                    "Sheet erosion & rill erosion",
                    "Gully erosion",
                    "Coastal and shoreline erosion (includes freshwater environments)",
                    "Debris flood (Volumetric Sediment Concentration 20-40%)",
                    "Debris flow (Volumetric Sediment Concentration >40%)",
                    "Small Rockfall (Diameter <25cm)",
                    "Large Rockfall (Diameter >25-100 cm)",
                    "Landslides < 2 m depth",
                    "Landslides 2-10 m depth",
                    "Landslides > 10 m depths",
                    "Mud or Earth flow",
                    "Soil slope deformation & Soil creep",
                    "Snow avalanches",
                    "Snow drift",
                    "Snow creep & slide",
                ]

                def parse_and_match_hazards(val):
                    if isinstance(val, list):
                        valid = [h for h in val if h in all_hazards_list]
                        return valid if valid else ["None Identified"]
                    elif isinstance(val, str):
                        found = [h for h in all_hazards_list if h in val]
                        return found if found else ["None Identified"]
                    return ["None Identified"]

                if "Possible Hazards" in df_pri_display.columns:
                    df_pri_display["Possible Hazards"] = df_pri_display["Possible Hazards"].apply(
                        lambda x: ", ".join(parse_and_match_hazards(x))
                    )
                else:
                    df_pri_display["Possible Hazards"] = "None Identified"

                cols = list(df_pri_display.columns)
                core_cols = [
                    c
                    for c in cols
                    if c
                    not in [
                        hazard_col,
                        "Hazard Level",
                        exposure_col,
                        "Sensitivity Index",
                        vulnerability_col,
                        "PRI scores",
                        "PRI values",
                        "Specific Hazard",
                        "Possible Hazards",
                    ]
                ]
                index_cols = [
                    hazard_col,
                    "Hazard Level",
                    exposure_col,
                    "Sensitivity Index",
                    vulnerability_col,
                ]
                final_pri_cols = ["PRI scores",
                                  "PRI values", "Possible Hazards"]

                new_order = core_cols + index_cols + final_pri_cols
                df_pri_display = df_pri_display[new_order]

                st.session_state.pri_display_df = df_pri_display

                st.success(
                    "Potential Risk Index (PRI) calculated successfully!")
                st.rerun()
            else:
                missing = [
                    c for c in required_cols if c not in df_base.columns]
                st.error(
                    f"Missing columns: {', '.join(missing)}. Please run previous steps (Hazards, Exposure, Vulnerability)."
                )
        else:
            st.warning("Please complete previous sections to generate data.")

    if "pri_display_df" in st.session_state and not st.session_state.pri_display_df.empty:
        final_config = {
            "Sensitivity Index": None,
            "Possible Hazards": None,
            "Hazard Level": None,
            "Specific Hazard": None,
            "Supportive Solutions": None,
            "Primary Solutions": None,
            "Possible Hazards": None,
            "PRI scores": st.column_config.ProgressColumn(
                "PRI Score",
                help="Final Potential Risk Index Score (0-5)",
                format="%d",
                min_value=0,
                max_value=5,
            ),
            "PRI values": st.column_config.TextColumn("PRI Level"),
            "Hazard Index": st.column_config.ProgressColumn(
                "Hazard Index",
                help="Final Hazard Index",
                format="%d",
                min_value=0,
                max_value=5,
            ),
            "Exposure Index": st.column_config.ProgressColumn(
                "Exposure Index",
                help="Final Exposure Index",
                format="%d",
                min_value=0,
                max_value=5,
            ),
            "Vulnerability Index": st.column_config.ProgressColumn(
                "Vuln. Index",
                help="Final Vulnerability Index",
                format="%.2f",
                min_value=0,
                max_value=5,
            ),
        }

        st.dataframe(
            st.session_state.pri_display_df,
            column_config=final_config,
            use_container_width=True,
        )

        if st.button("Generate PRI Assessment Report", type="primary", use_container_width=True):
            if not st.session_state.get("gemini_client"):
                st.error("Please provide a valid API Key to generate the report.")
            else:
                with st.spinner("Analyzing Risk Indices and writing report (Gemini)..."):
                    pri_report_text = generate_pri_report_gemini(
                        st.session_state.pri_display_df)
                    st.session_state["pri_report"] = pri_report_text

        if "pri_report" in st.session_state and st.session_state["pri_report"]:
            with st.expander("View PRI Assessment Report", expanded=True):
                render_ai_header(
                    "Potential Risk Index (PRI) Assessment Report")
                with st.expander("📊 View Raw Data Fed to AI (PRI Table)", expanded=False):
                    tab_actual, tab_example = st.tabs(
                        ["📋 Actual Data", "📖 Example Used to Guide AI"]
                    )
                    with tab_actual:
                        st.caption(
                            "This is the PRI data table that was provided to the AI model for analysis."
                        )
                        st.dataframe(st.session_state.pri_display_df,
                                     use_container_width=True)
                    with tab_example:
                        st.caption(
                            "This is the example table and report text used as a reference to guide the AI's output style and structure."
                        )
                        st.markdown("**Example Input Table:**")
                        st.markdown(EXAMPLE_PRI_TABLE)
                        st.markdown("**Example Output Report:**")
                        st.markdown(EXAMPLE_PRI_REPORT)
                st.markdown(st.session_state["pri_report"])
                render_ai_footer()

            st.download_button(
                label="Download Report as Text",
                data=st.session_state["pri_report"],
                file_name="PRI_Assessment_Report.txt",
                mime="text/plain",
            )
    st.divider()
    st.subheader("7. Nature-based Solutions (NbS) Recommendations")
    st.markdown("#### Step 7.1: Potential Hazards Selection")
    approved_nbs = st.session_state.get("approved_nbs_methods", [])
    approved_supportive = st.session_state.get(
        "approved_supportive_methods", [])
    show_supportive = False
    all_hazards_for_selector = [
        "Extreme high temperatures (Heatwave)",
        "Extreme cold temperatures (Coldwave, cold snap)",
        "Drought",
        "Wildfire (Forest fire or Bush fire)",
        "Desertification",
        "Storms & strong winds",
        "Hail",
        "Aeolian erosion",
        "Pluvial flood, heavy rainfall and surface runoff",
        "Fluvial flood",
        "Coastal flood (e.g. storm surge)",
        "Impact floods and Tsunami",
        "Fluvial sediment transport",
        "Stream bank & bed erosion",
        "Sheet erosion & rill erosion",
        "Gully erosion",
        "Coastal and shoreline erosion (includes freshwater environments)",
        "Debris flood (Volumetric Sediment Concentration 20-40%)",
        "Debris flow (Volumetric Sediment Concentration >40%)",
        "Small Rockfall (Diameter <25cm)",
        "Large Rockfall (Diameter >25-100 cm)",
        "Landslides < 2 m depth",
        "Landslides 2-10 m depth",
        "Landslides > 10 m depths",
        "Mud or Earth flow",
        "Soil slope deformation & Soil creep",
        "Snow avalanches",
        "Snow drift",
        "Snow creep & slide",
    ]

    if "selected_nbs_hazards" not in st.session_state:
        st.session_state.selected_nbs_hazards = []

    if st.button("Automatic Extraction from PRI Table", type="primary"):
        approved_nbs = st.session_state.get("approved_nbs_methods", [])
        approved_supportive = st.session_state.get(
            "approved_supportive_methods", [])
        show_supportive = False
        if (
            "calculated_results" in st.session_state
            and not st.session_state.calculated_results.empty
        ):
            extracted_hazards = set()
            df_nbs = st.session_state.calculated_results.copy()

            if "Possible Hazards" not in df_nbs.columns and "saved_data" in st.session_state:
                df_nbs["Possible Hazards"] = st.session_state.saved_data.loc[
                    df_nbs.index, "Possible Hazards"
                ]

            if "Possible Hazards" in df_nbs.columns:
                for _, row in df_nbs.iterrows():
                    hazards_item = row.get("Possible Hazards", [])
                    if isinstance(hazards_item, str):
                        current_hazards = [
                            h for h in all_hazards_for_selector if h in hazards_item]
                    else:
                        current_hazards = [
                            h
                            for h in (hazards_item if isinstance(hazards_item, list) else [])
                            if h in all_hazards_for_selector
                        ]

                    extracted_hazards.update(current_hazards)

                st.session_state.selected_nbs_hazards = sorted(
                    list(extracted_hazards))
                st.session_state.hazard_transfer_key = (
                    st.session_state.get("hazard_transfer_key", 0) + 1
                )

                st.success(
                    f"Extracted {len(st.session_state.selected_nbs_hazards)} hazards.")
                st.rerun()
            else:
                st.error("Could not find hazard data in the PRI table.")
        else:
            st.error("No PRI calculation results available to extract from.")
    if not isinstance(st.session_state.selected_nbs_hazards, list):
        st.session_state.selected_nbs_hazards = []

    current_indices = [
        all_hazards_for_selector.index(h)
        for h in st.session_state.selected_nbs_hazards
        if h in all_hazards_for_selector
    ]
    safe_indices = current_indices if len(current_indices) > 0 else None
    if "hazard_transfer_key" not in st.session_state:
        st.session_state.hazard_transfer_key = 0

    col_left, col_center, col_right = st.columns([2, 8, 1])

    with col_center:
        selected_hazards = sac.transfer(
            items=all_hazards_for_selector,
            label="Select Hazards from Project Scope",
            index=safe_indices,
            titles=["Available Hazards", "Active Hazards"],
            search=True,
            height=400,
            width="100%",
            key=f"hazard_transfer_logic_{st.session_state.hazard_transfer_key}",
        )
    if selected_hazards is not None:
        valid_hazards = [
            h for h in selected_hazards if isinstance(h, str) and h in all_hazards_for_selector
        ]
        if sorted(valid_hazards) != sorted(st.session_state.selected_nbs_hazards):
            st.session_state.selected_nbs_hazards = sorted(valid_hazards)
    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button(
            "🗑️ Clear Hazard Selection",
            key="clear_hazard_sel",
            help="Remove all active hazards and reset the NbS panels.",
        ):
            st.session_state.selected_nbs_hazards = []
            st.session_state.hazard_transfer_key = (
                st.session_state.get("hazard_transfer_key", 0) + 1
            )
            st.rerun()

    dynamic_nbs_list = set()
    nbs_db = (
        NbS_list
        if isinstance(NbS_list, dict)
        else (NbS_list[0] if isinstance(NbS_list, list) and len(NbS_list) > 0 else {})
    )

    if st.session_state.selected_nbs_hazards:
        for h in st.session_state.selected_nbs_hazards:
            if h in nbs_db:
                dynamic_nbs_list.update(nbs_db[h].get("Yes", []))

    dynamic_nbs_list = sorted(list(dynamic_nbs_list))

    if (
        "prev_dynamic_nbs" not in st.session_state
        or st.session_state.prev_dynamic_nbs != dynamic_nbs_list
    ):
        st.session_state.prev_dynamic_nbs = dynamic_nbs_list
        st.session_state.approved_nbs_methods = dynamic_nbs_list

    _HAZARD_ICONS = {
        "Heatwave": "🌡️",
        "Coldwave": "🧊",
        "Drought": "🏜️",
        "Wildfire": "🔥",
        "Desertification": "🌵",
        "Storms": "🌪️",
        "Hail": "🌨️",
        "erosion": "⛰️",
        "flood": "🌊",
        "Flood": "🌊",
        "sediment": "🪨",
        "Rockfall": "🪨",
        "Landslide": "⛰️",
        "avalanche": "❄️",
        "Snow": "❄️",
        "Mud": "🌧️",
    }

    def _hazard_icon(name):
        for kw, icon in _HAZARD_ICONS.items():
            if kw.lower() in name.lower():
                return icon
        return "⚠️"

    def _resolve_chip(chip_result, sols):
        """Normalise sac.chip return to a list of label strings.
        None means first render — treat as all items selected (default state).
        sac.chip also returns [] after a rerun; same rule applies: keep all selected."""
        if chip_result is None or chip_result == []:
            return list(sols)
        elif isinstance(chip_result, str):
            return [chip_result]
        elif isinstance(chip_result, int):
            return [sols[chip_result]] if chip_result < len(sols) else []
        elif isinstance(chip_result, list):
            out = []
            for item in chip_result:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, int) and item < len(sols):
                    out.append(sols[item])
            return out if out else list(sols)
        return list(sols)

    def _build_solution_table(sol_key, all_sols_list):
        sol_to_hazards = {}
        for h in st.session_state.selected_nbs_hazards:
            for s in nbs_db.get(h, {}).get(sol_key, []):
                if s in all_sols_list:
                    sol_to_hazards.setdefault(s, [])
                    if h not in sol_to_hazards[s]:
                        sol_to_hazards[s].append(h)
        return [
            {
                "Include": True,
                "NbS Solution": sol,
                "Addressed Hazards": ", ".join(_hazard_icon(h) + " " + h for h in hazards),
            }
            for sol, hazards in sorted(sol_to_hazards.items())
        ]

    if st.session_state.selected_nbs_hazards and dynamic_nbs_list:
        st.markdown("##### ✅ Primary NbS Solutions")
        st.caption(
            "All solutions recommended for your active hazards, deduplicated. Uncheck **Include** to remove a solution from the NbS summary."
        )

        primary_rows = _build_solution_table("Yes", dynamic_nbs_list)

        if "nbs_table_excluded" not in st.session_state:
            st.session_state.nbs_table_excluded = set()
        current_primary_sols = {r["NbS Solution"] for r in primary_rows}
        st.session_state.nbs_table_excluded &= current_primary_sols
        for row in primary_rows:
            row["Include"] = row["NbS Solution"] not in st.session_state.nbs_table_excluded
        edited_primary = st.data_editor(
            pd.DataFrame(primary_rows),
            column_config={
                "Include": st.column_config.CheckboxColumn("Include", width="small"),
                "NbS Solution": st.column_config.TextColumn(
                    "NbS Solution", width="medium", disabled=True
                ),
                "Addressed Hazards": st.column_config.TextColumn(
                    "Addressed Hazards", width="large", disabled=True
                ),
            },
            hide_index=True,
            use_container_width=True,
            key="primary_nbs_table",
        )

        if st.button("Save Primary NbS Selections", type="primary"):
            st.session_state.nbs_table_excluded = {
                row["NbS Solution"] for _, row in edited_primary.iterrows() if not row["Include"]
            }
            approved_nbs = sorted(
                edited_primary.loc[edited_primary["Include"],
                                   "NbS Solution"].tolist()
            )
            st.session_state.approved_nbs_methods = approved_nbs
            st.toast("Primary selections saved!", icon="✅")
            st.rerun()
        current_inc = len(edited_primary[edited_primary["Include"]])
        st.markdown(
            f"<div style='background:#f1f8e9;border-left:4px solid #43a047;padding:8px 14px;border-radius:6px;margin-top:4px;color:#1b5e20;'><strong>Selection: {current_inc} / {len(primary_rows)} (Unsaved changes will not appear in summary)</strong></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
    dynamic_supportive_list = set()
    if st.session_state.selected_nbs_hazards:
        for h in st.session_state.selected_nbs_hazards:
            if h in nbs_db:
                dynamic_supportive_list.update(nbs_db[h].get("Supportive", []))
    dynamic_supportive_list = sorted(list(dynamic_supportive_list))

    if "approved_supportive_methods" not in st.session_state:
        st.session_state.approved_supportive_methods = dynamic_supportive_list
    if (
        "prev_dynamic_supportive" not in st.session_state
        or st.session_state.prev_dynamic_supportive != dynamic_supportive_list
    ):
        st.session_state.prev_dynamic_supportive = dynamic_supportive_list
        st.session_state.approved_supportive_methods = dynamic_supportive_list
    if st.session_state.selected_nbs_hazards and dynamic_supportive_list:
        show_supportive = st.toggle(
            "🔄 Configure Supportive NbS Solutions",
            value=False,
            help="Toggle to view and edit supportive Nature-based Solutions.",
        )

        supportive_rows = _build_solution_table(
            "Supportive", dynamic_supportive_list)

        if "nbs_supp_table_excluded" not in st.session_state:
            st.session_state.nbs_supp_table_excluded = set()

        current_supp_sols = {r["NbS Solution"] for r in supportive_rows}
        st.session_state.nbs_supp_table_excluded &= current_supp_sols

        for row in supportive_rows:
            row["Include"] = row["NbS Solution"] not in st.session_state.nbs_supp_table_excluded
        if show_supportive:
            st.markdown("##### 🔄 Supportive NbS Solutions")
            st.caption(
                "Supportive solutions complement primary NbS measures, deduplicated across all active hazards. Uncheck **Include** to exclude a solution from the mapping summary."
            )

            edited_supportive = st.data_editor(
                pd.DataFrame(supportive_rows),
                column_config={
                    "Include": st.column_config.CheckboxColumn("Include", width="small"),
                    "NbS Solution": st.column_config.TextColumn(
                        "NbS Solution", width="medium", disabled=True
                    ),
                    "Addressed Hazards": st.column_config.TextColumn(
                        "Addressed Hazards", width="large", disabled=True
                    ),
                },
                hide_index=True,
                use_container_width=True,
                key="supportive_nbs_table",
            )
            if st.button("Save Supportive NbS Selections", type="primary"):
                st.session_state.nbs_supp_table_excluded = {
                    row["NbS Solution"]
                    for _, row in edited_supportive.iterrows()
                    if not row["Include"]
                }
                approved_supportive = sorted(
                    edited_supportive.loc[edited_supportive["Include"], "NbS Solution"].tolist(
                    )
                )
                st.session_state.approved_supportive_methods = approved_supportive
                st.toast("Supportive selections saved!", icon="✅")
                st.rerun()

            current_inc_s = len(
                edited_supportive[edited_supportive["Include"]])
            st.markdown(
                f"<div style='background:#e3f2fd;border-left:4px solid #1e88e5;padding:8px 14px;border-radius:6px;margin-top:4px;color:#0d47a1;'><strong>Selection: {current_inc_s} / {len(supportive_rows)} (Unsaved changes will not appear in summary)</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

    _sei_dropdown_options = []

    if "calculated_results" in st.session_state and not st.session_state.calculated_results.empty:
        st.markdown("#### NbS Implementation Mapping Summary")
        approved_nbs_set = set(
            st.session_state.get("approved_nbs_methods", []))
        approved_supportive_set = (
            set(st.session_state.get("approved_supportive_methods", []))
            if show_supportive
            else set()
        )
        summary_display_df = st.session_state.calculated_results.copy()

        if (
            "Possible Hazards" not in summary_display_df.columns
            and "saved_data" in st.session_state
        ):
            summary_display_df["Possible Hazards"] = st.session_state.saved_data.loc[
                summary_display_df.index, "Possible Hazards"
            ]

        primary_sol_col = []
        supportive_sol_col = []

        for _, row in summary_display_df.iterrows():
            hazards_item = row.get("Possible Hazards", [])
            if isinstance(hazards_item, str):
                current_hazards = [
                    h for h in all_hazards_for_selector if h in hazards_item]
            else:
                current_hazards = [
                    h
                    for h in (hazards_item if isinstance(hazards_item, list) else [])
                    if h in all_hazards_for_selector
                ]

            p_sols, s_sols = set(), set()
            for h in current_hazards:
                h_strip = h.strip()
                if h_strip in nbs_db:
                    db_yes = nbs_db[h_strip].get("Yes", [])
                    db_supp = nbs_db[h_strip].get("Supportive", [])
                    if h_strip in st.session_state.selected_nbs_hazards:
                        valid_primary = [
                            sol for sol in db_yes if sol in approved_nbs_set]
                        valid_supportive = [
                            sol for sol in db_supp if sol in approved_supportive_set
                        ]
                    else:
                        valid_primary = []
                        valid_supportive = []

                    p_sols.update(valid_primary)
                    s_sols.update(valid_supportive)

            primary_sol_col.append(", ".join(sorted(list(p_sols))))
            supportive_sol_col.append(", ".join(sorted(list(s_sols))))

        summary_display_df["Primary Solutions"] = primary_sol_col
        summary_display_df["Supportive Solutions"] = supportive_sol_col

        st.session_state.calculated_results["Primary Solutions"] = primary_sol_col
        st.session_state.calculated_results["Supportive Solutions"] = supportive_sol_col
        _sei_dropdown_options = sorted(
            set(
                sol.strip()
                for cols in (primary_sol_col, supportive_sol_col)
                for row_val in cols
                for sol in str(row_val).split(",")
                if sol.strip()
            )
        )

        available_cols = summary_display_df.columns.tolist()
        required_cols = [
            "Infrastructure",
            "Asset",
            "Impact model",
            "Possible Hazards",
            "Primary Solutions",
            "Supportive Solutions",
        ]
        cols_to_show = [c for c in required_cols if c in available_cols]

        st.dataframe(summary_display_df[cols_to_show],
                     use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### Step 7.2: Filtration of the Recommended NbS Solutions")
    st.info(
        "Filter and refine NbS selection by integrating Site-Specific Feasibility (SSF), Socio-Economic acceptance (SEI), and Hazard Impact Attenuation (HIA)."
    )
    _sei_dropdown_options = []
    if "calculated_results" in st.session_state:
        df = st.session_state.calculated_results
        extracted_sols = set()
        extracted_sols.update(st.session_state.get("approved_nbs_methods", []))
        if show_supportive:
            extracted_sols.update(st.session_state.get(
                "approved_supportive_methods", []))
        _sei_dropdown_options = sorted(list(extracted_sols))

    if "sei_lookup" not in st.session_state:
        st.session_state.sei_lookup = {}
    if "global_site_conditions" not in st.session_state:
        st.session_state.global_site_conditions = {
            "Slope instability": False,
            "Limited vegetation and low quality of soil": False,
            "Limited access for implementation": False,
            "Cold temperatures": False,
            "Limited water availability": False,
            "Lack of connection to major services": False,
            "Space Constraints": False,
            "Exposure to soil, water and/or air pollution": False,
            "Limitations due to high population density": False
        }

    sei_factors_list = [
        "Community Engagement",
        "Cultural Preferences",
        "Workforce Availability",
        "Economic Viability",
        "Long term O&M costs",
        "Land Ownership",
        "Regulatory Constraints",
    ]

    ssf_labels = {
        "Slope instability": "Unstable/Steep Slopes",
        "Limited vegetation and low quality of soil": "Poor Soil/Low Vegetation",
        "Limited access for implementation": "Difficult Site Access",
        "Cold temperatures": "Cold Temperatures / Frost Risk",
        "Limited water availability": "Water Scarcity",
        "Lack of connection to major services": "No Infrastructure/Services Access",
        "Space Constraints": "Very Limited Space",
        "Exposure to soil, water and/or air pollution": "Polluted Soil/Water/Air",
        "Limitations due to high population density": "Urban/Densely Populated Area",
    }
    if _sei_dropdown_options:
        relevant_methods = _sei_dropdown_options
        selected_nbs_for_sei = st.selectbox(
            "Select an NbS Solution to configure SEI factors:", relevant_methods
        )
        if selected_nbs_for_sei not in st.session_state.sei_lookup:
            st.session_state.sei_lookup[selected_nbs_for_sei] = {
                f: 1 for f in sei_factors_list}
    else:
        selected_nbs_for_sei = None
        relevant_methods = []

    if "ssf_lookup" not in st.session_state:
        st.session_state.ssf_lookup = {
            "Terracing (slope shaping - reduction of slope inclination)": {
                "Slope instability": {
                    "Explanation": "Terracing improves slope stability.",
                    "Value": 100,
                },
                "Limited vegetation and low quality of soil": {
                    "Explanation": "Harder to shape in shallow/poor soils.",
                    "Value": 50,
                },
                "Limited access for implementation": {
                    "Explanation": "Requires machinery and work space, the personnel to reach the area and be able to carry the material up to there. All hinders the implementation and maintenance.",
                    "Value": 0,
                },
                "Cold temperatures": {
                    "Explanation": "Requires periodic upkeep, there should be monitoring to double check the condition over the cold period.",
                    "Value": 0,
                },
                "Limited water availability": {
                    "Explanation": "Soil compaction more difficult when dry.",
                    "Value": 50,
                },
                "Lack of connection to major services": {
                    "Explanation": "Machinery delivery required.",
                    "Value": 50,
                },
                "Space Constraints": {
                    "Explanation": "Needs substantial bench width.",
                    "Value": 0,
                },
                "Exposure to soil, water and/or air pollution": {
                    "Explanation": "Sediment transported by runoff is a factor that may weaken terrace edges.",
                    "Value": 50,
                },
                "Limitations due to high population density": {
                    "Explanation": "Remote area.",
                    "Value": 100,
                },
            },
            "Earth dams and barriers (vegetated)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Avalanche mounds": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "3-D steel grids (vegetated)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Reinforced soil and earth packs (vegetated)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Afforestation and reforestation": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 0},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 0},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Protection forest management": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Retention forest": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Wildfire-forest management": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Buffer vegetation strips and coppice management": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Firebreaks and firestrips": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 50},
            },
            "Fire-resistant tree species & plants": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Prescribed burning": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 0},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 0},
                "Limitations due to high population density": {"Value": 0},
            },
            "Riparian buffer zones": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Floodplain restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Meandering channel planform": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Channel widening": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 50},
            },
            "Sills": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Groynes (vegetated)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated flood protection dams, dikes & levees": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Water retention basins and ponds (storage ponds)": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Wetland conservation and restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Constructed rural wetlands": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Salt marsh restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Shoreline reforestation & living shorelines (mangroves)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 0},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 50},
            },
            "Dune restoration and coastal vegetation": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 50},
            },
            "Sand dune stabilization": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Seagrass bed restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 0},
                "Limitations due to high population density": {"Value": 50},
            },
            "Coral reef conservation and restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 0},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 0},
                "Limitations due to high population density": {"Value": 50},
            },
            "Agroforestry": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Horticulture": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Water retention, harvesting & cisterns": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Managed aquifer recharge (MAR)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 0},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 0},
                "Limitations due to high population density": {"Value": 100},
            },
            "Green corridors & tree rows": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Biodiverse hedgerows": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Meadow & grassland restoration": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Vegetated buffer zones": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Controlled grazing": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Fire-smart agriculture": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Contour trenching": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 50},
            },
            "Conservation tillage": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Mulching": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Cover cropping": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Soil amendments (previosly organic amendments)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Hydro and mulch seeding": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated biodegradeable erosion control meshes": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated biodegradeable erosion control mats and blankets (renamed from NTNU)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Sod (turves)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live staking": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live fencing (for slope engineering)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live slope grids or contour logs": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live layered techniques": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated cribwall (layer-based design)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated drainage systems": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Wattle fence (for water enginering)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Tree revetment (tree spurs)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated riprap": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Root wad": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated crib wall (fascine-based design)": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 0},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live fascines": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Brush mattress": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Live palisades and live weirs": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vegetated log/stone barriers and live/rock check dams": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Wooden log fences": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 50},
                "Limitations due to high population density": {"Value": 100},
            },
            "Open green spaces": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Green pavers": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Green roofs": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Vertical greenery": {
                "Slope instability": {"Value": 50},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 50},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 0},
                "Lack of connection to major services": {"Value": 0},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Urban forests": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 100},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 0},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 50},
            },
            "Rain gardens": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Bio-retention cells, basins and ponds": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Constructed urban wetlands": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 100},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 50},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 50},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Infiltration trenches": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 100},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
            "Bioswales": {
                "Slope instability": {"Value": 100},
                "Limited vegetation and low quality of soil": {"Value": 50},
                "Limited access for implementation": {"Value": 100},
                "Cold temperatures": {"Value": 50},
                "Limited water availability": {"Value": 100},
                "Lack of connection to major services": {"Value": 50},
                "Space Constraints": {"Value": 100},
                "Exposure to soil, water and/or air pollution": {"Value": 100},
                "Limitations due to high population density": {"Value": 100},
            },
        }

    relevant_methods = set(_sei_dropdown_options)

    edit_ssf_toggle = st.toggle(
        "🛠️ Customize Site-Specific Feasibility (SSF) Rules",
        help="Modify the baseline assumptions for how site constraints affect each NbS method.",
    )

    if edit_ssf_toggle:
        st.markdown("##### Edit SSF Rulebook")
        val_to_str = {
            100: "Highly Feasible",
            50: "Moderately Feasible",
            0: "Not Feasible",
        }
        str_to_val = {v: k for k, v in val_to_str.items()}
        ssf_criteria_list = [
            "Slope instability",
            "Limited vegetation and low quality of soil",
            "Limited access for implementation",
            "Cold temperatures",
            "Limited water availability",
            "Lack of connection to major services",
            "Space Constraints",
            "Exposure to soil, water and/or air pollution",
            "Limitations due to high population density",
        ]
        edit_data = []
        for method in sorted(list(relevant_methods)):
            if method in st.session_state.ssf_lookup:
                row_dict = {"NbS Method": method}
                for crit in ssf_criteria_list:
                    crit_data = st.session_state.ssf_lookup[method].get(
                        crit, {})
                    val = crit_data.get("Value", 100) if isinstance(
                        crit_data, dict) else 100
                    row_dict[crit] = val_to_str.get(val, "Highly Feasible")
                edit_data.append(row_dict)
        if edit_data:
            col_config = {
                "NbS Method": st.column_config.TextColumn(disabled=True)}
            for crit in ssf_criteria_list:
                col_config[crit] = st.column_config.SelectboxColumn(
                    options=["Highly Feasible",
                             "Moderately Feasible", "Not Feasible"],
                    required=True,
                )
            edited_df = st.data_editor(
                pd.DataFrame(edit_data),
                column_config=col_config,
                hide_index=True,
                use_container_width=True,
                key="ssf_rule_editor",
            )
            for _, row in edited_df.iterrows():
                method = row["NbS Method"]
                for crit in ssf_criteria_list:
                    new_val = str_to_val[row[crit]]
                    if method in st.session_state.ssf_lookup:
                        if crit not in st.session_state.ssf_lookup[method]:
                            st.session_state.ssf_lookup[method][crit] = {}
                        st.session_state.ssf_lookup[method][crit]["Value"] = new_val
        else:
            st.info(
                "No identified solutions found to edit. Please run Step 7.1 first.")
        st.divider()
    with st.expander("⚙️ Configure Site Conditions & Socio-Economic Factors", expanded=True):
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            with st.container(border=True):
                st.markdown("##### 🌍 Site-Specific Conditions (SSF)")
                st.caption(
                    "These physical conditions apply globally to your specific site.")
                for crit, label in ssf_labels.items():
                    current_val = st.session_state.global_site_conditions.get(
                        crit, False)
                    val = st.toggle(
                        label,
                        value=current_val,
                        key=f"ssf_global_cond_{crit}",
                    )
                    st.session_state.global_site_conditions[crit] = val
        with col_input2:
            with st.container(border=True):
                st.markdown("##### 👥 Socio-Economic & Institutional (SEI)")
                if selected_nbs_for_sei:
                    st.caption(
                        f"Configuring SEI factors for: **{selected_nbs_for_sei}**")
                    for f in sei_factors_list:
                        current_val = st.session_state.sei_lookup[selected_nbs_for_sei].get(
                            f, 1)
                        val = st.select_slider(
                            f"{f}",
                            options=[1, 2, 3],
                            value=current_val,
                            key=f"sei_{selected_nbs_for_sei}_{f}",
                            help="1: Favorable, 2: Neutral, 3: Unfavorable",
                        )
                        st.session_state.sei_lookup[selected_nbs_for_sei][f] = val
                else:
                    st.info(
                        "Select an NbS solution from the dropdown above to configure SEI factors."
                    )

    st.session_state.filtered_nbs_pool = []
    low_perf_pool = []
    if (
        "calculated_results" in st.session_state
        and "Primary Solutions" in st.session_state.calculated_results.columns
    ):
        unique_pairs = {}
        method_to_hazards = {}
        for row_idx, row in st.session_state.calculated_results.iterrows():
            raw_pri = row.get("PRI scores", 0)
            try:
                pri_score = (
                    float(raw_pri) if raw_pri is not None and str(
                        raw_pri).strip() != "" else 0.0
                )
            except (ValueError, TypeError):
                pri_score = 0.0
            asset_val = str(row.get("Asset", "")).strip() or "—"
            impact_val = str(row.get("Impact model", "")).strip() or "—"
            infra_val = str(row.get("Infrastructure", "")).strip() or ""
            row_label = f"{asset_val} — {impact_val}"

            raw_hazards = row.get("Possible Hazards", [])
            if isinstance(raw_hazards, str):
                val_clean = (
                    raw_hazards.replace("[", "").replace("]", "").replace(
                        "'", "").replace('"', "")
                )
                hazards = [h.strip()
                           for h in val_clean.split(",") if h.strip()]
            elif isinstance(raw_hazards, list):
                hazards = raw_hazards
            else:
                hazards = []
            hazards = [h for h in hazards if h in all_hazards_for_selector]
            all_hazards_raw = []
            p_raw = str(row.get("Primary Solutions", ""))
            row_p_sols = [
                s.strip()
                for s in p_raw.split(",")
                if s.strip() and s.strip() in st.session_state.get("approved_nbs_methods", [])
            ]
            s_raw = str(row.get("Supportive Solutions", ""))
            row_s_sols = [
                s.strip()
                for s in s_raw.split(",")
                if s.strip()
                and show_supportive
                and s.strip() in st.session_state.get("approved_supportive_methods", [])
            ]
            all_sols = list(dict.fromkeys(row_p_sols + row_s_sols))

            for h in hazards:
                for sol in all_sols:
                    pair_name = f"{sol} method for {h}"
                    up_key = (row_idx, pair_name)
                    is_prim = sol in row_p_sols

                    if up_key not in unique_pairs:
                        unique_pairs[up_key] = {
                            "original_pri": pri_score,
                            "status": "scored",
                            "pair_name": pair_name,
                            "method_only": sol,
                            "row_label": row_label,
                            "asset": asset_val,
                            "impact_model": impact_val,
                            "infrastructure": infra_val,
                            "is_primary": is_prim,
                        }
                    elif unique_pairs[up_key]["original_pri"] < pri_score:
                        unique_pairs[up_key]["original_pri"] = pri_score
                        if is_prim:
                            unique_pairs[up_key]["is_primary"] = True

                    if sol not in method_to_hazards:
                        method_to_hazards[sol] = set()
                    method_to_hazards[sol].add(h)

        nbs_db = (
            NbS_list
            if isinstance(NbS_list, dict)
            else (NbS_list[0] if isinstance(NbS_list, list) and len(NbS_list) > 0 else {})
        )
        for _, data in unique_pairs.items():
            name = data["pair_name"]
            method_base = data["method_only"]

            m_ssf_data = st.session_state.ssf_lookup.get(method_base, {})
            method_site_conditions = st.session_state.global_site_conditions
            ssf_scores = []

            for crit in ssf_labels.keys():
                active = method_site_conditions.get(crit, False)
                if active:
                    c_info = m_ssf_data.get(crit, {})
                    val = c_info.get("Value", 100) if isinstance(
                        c_info, dict) else 100
                    ssf_scores.append(val)
                else:
                    ssf_scores.append(100)

            avg_ssf = sum(ssf_scores) / len(ssf_scores) if ssf_scores else 100
            method_sei_vals = st.session_state.sei_lookup.get(
                method_base, {f: 1 for f in sei_factors_list}
            )
            sei_scores = [
                100 if v == 1 else (50 if v == 2 else 0) for v in method_sei_vals.values()
            ]
            avg_sei = sum(sei_scores) / len(sei_scores) if sei_scores else 100
            relevant_hazards = st.session_state.get("selected_nbs_hazards", [])

            hia_scores = []
            for haz_key in relevant_hazards:
                haz_data = nbs_db.get(haz_key, {})
                yes_list = haz_data.get("Yes", [])
                supp_list = haz_data.get("Supportive", [])

                if method_base in yes_list:
                    hia_scores.append(100)
                elif method_base in supp_list:
                    hia_scores.append(50)
                else:
                    hia_scores.append(0)
            avg_hia = sum(hia_scores) / len(hia_scores) if hia_scores else 0

            total_score = (avg_ssf + avg_sei + avg_hia) / 3
            if total_score < 10:
                tech_eff = 1
            elif total_score < 30:
                tech_eff = 2
            elif total_score < 60:
                tech_eff = 3
            elif total_score < 80:
                tech_eff = 4
            else:
                tech_eff = 5

            af = 1.0 - tech_eff / 5.0
            pri_score = data.get("original_pri", 0)
            rpri = pri_score * af
            eff_percent = total_score
            data.update(
                {
                    "name": name,
                    "method_only": method_base,
                    "ssf": avg_ssf,
                    "sei": avg_sei,
                    "hia": avg_hia,
                    "total": total_score,
                    "tech_eff": tech_eff,
                    "eff_percent": eff_percent,
                    "rpri": rpri,
                }
            )
            if total_score >= 30:
                st.session_state.filtered_nbs_pool.append(data)
            else:
                low_perf_pool.append(data)

        if not st.session_state.filtered_nbs_pool:
            if not unique_pairs:
                st.info(
                    "💡 **Strategy Setup:** Please click the **'Save'** buttons in the Step 7.1 tables above to generate the ranking and residual risk analysis."
                )
            else:
                st.warning(
                    "⚠️ No solutions strictly passed the 30% feasibility threshold. Showing all potential methods for your review."
                )
                st.session_state.filtered_nbs_pool = list(
                    unique_pairs.values())
        else:
            st.success(
                f"Filtration complete: {len(st.session_state.filtered_nbs_pool)} solutions passed the feasibility threshold."
            )

        if st.session_state.filtered_nbs_pool:
            st.markdown("---")
            st.subheader("NbS Feasibility Spider Diagram")
            df_final = pd.DataFrame(st.session_state.filtered_nbs_pool).sort_values(
                by="total", ascending=False
            )
            top_m = df_final.head(5)
            fig = go.Figure()
            for _, r in top_m.iterrows():
                fig.add_trace(
                    go.Scatterpolar(
                        r=[r["ssf"], r["sei"], r["hia"], r["ssf"]],
                        theta=[
                            "Site Feasibility (SSF)",
                            "Socio-Economic (SEI)",
                            "Hazard Attenuation (HIA)",
                            "Site Feasibility (SSF)",
                        ],
                        fill="toself",
                        name=r["name"],
                    )
                )
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📊 View Full Site-Specific Filtration Summary", expanded=False):
                filt_config = {
                    "name": st.column_config.TextColumn("NbS Method"),
                    "ssf": st.column_config.ProgressColumn(
                        "SSF (%)", format="%.0f%%", min_value=0, max_value=100
                    ),
                    "sei": st.column_config.ProgressColumn(
                        "SEI (%)", format="%.0f%%", min_value=0, max_value=100
                    ),
                    "hia": st.column_config.ProgressColumn(
                        "HIA (%)", format="%.0f%%", min_value=0, max_value=100
                    ),
                    "total": st.column_config.ProgressColumn(
                        "Final Index (%)", format="%.0f%%", min_value=0, max_value=100
                    ),
                }
                st.dataframe(
                    df_final[["name", "ssf", "sei", "hia", "total"]],
                    column_config=filt_config,
                    use_container_width=True,
                    hide_index=True,
                )

            if low_perf_pool:
                st.markdown("##### ⚠️ Threshold Analysis")
                with st.expander(
                    f"View {len(low_perf_pool)} methods below 30% threshold",
                    expanded=False,
                ):
                    for item in low_perf_pool:
                        st.warning(
                            f"**{item['name']}** is not recommended (Score: {item['total']:.1f}%)."
                        )

            st.divider()
            st.markdown("#### Final NbS Recommendation Strategy")
            st.info("Ranking Based on Residual Potential Risk Index (RPRI)")

            if st.button("🔢 Calculate RPRI Ranking", type="primary", key="calc_rpri_btn"):
                st.session_state.rpri_results_ready = True

            if st.session_state.get("rpri_results_ready", False):

                def get_dynamic_color(rpri_val, eff_percent, min_val, max_val):
                    if eff_percent == 0.0:
                        return "#d32f2f"
                    if max_val == min_val:
                        return "#1b5e20"
                    norm = (rpri_val - min_val) / (max_val - min_val)
                    if norm <= 0.14:
                        return "#1b5e20"
                    elif norm <= 0.28:
                        return "#2e7d32"
                    elif norm <= 0.42:
                        return "#aed581"
                    elif norm <= 0.57:
                        return "#fff176"
                    elif norm <= 0.71:
                        return "#ffb74d"
                    elif norm <= 0.85:
                        return "#f57c00"
                    else:
                        return "#d32f2f"

                def render_rpri_ranking(pool, show_row_badge=False):
                    """
                    Consolidate pool by method_only (keep highest RPRI per method),
                    then render the ranked cards.
                    show_row_badge=True adds a small row label badge on each card
                    (used in the All-Rows-Combined view so the user can see which
                    row drove the displayed PRI value).
                    """
                    cons = {}
                    for item in pool:
                        if not item.get("is_primary", False):
                            continue
                        m = item["method_only"]
                        if m not in cons or item.get("rpri", 0) > cons[m].get("rpri", 0):
                            cons[m] = item

                    scored = sorted(
                        [i for i in cons.values() if i["status"] == "scored"],
                        key=lambda x: (x["eff_percent"] == 0, x["rpri"]),
                    )
                    unscored = [i for i in cons.values() if i["status"]
                                == "unscored"]

                    if not scored and not unscored:
                        st.info("No primary solutions found for this selection.")
                        return

                    valid_vals = [i["rpri"]
                                  for i in scored if i["eff_percent"] > 0]
                    mn, mx = (min(valid_vals), max(valid_vals)
                              ) if valid_vals else (0, 0)

                    for rank, item in enumerate(scored, 1):
                        bg = get_dynamic_color(
                            item["rpri"], item["eff_percent"], mn, mx)
                        tc = "black" if bg in [
                            "#fff176", "#ffb74d", "#aed581"] else "white"
                        af_val = 1.0 - item["tech_eff"] / 5.0
                        pri_val = item.get("original_pri", 0.0)
                        rpri_val = item.get("rpri", 0.0)
                        delta_val = pri_val - rpri_val
                        row_badge_html = ""
                        if show_row_badge:
                            lbl = item.get("row_label", "")
                            if lbl:
                                row_badge_html = f'<span style="background:#e3f2fd;color:#1565c0;border-radius:4px;padding:1px 6px;font-size:0.78em;font-weight:normal;margin-left:6px;">{lbl}</span>'
                        st.markdown(
                            f"""
                            <div style="
                                background:#ffffff;
                                border:1.5px solid #dee2e6;
                                border-left:5px solid {bg};
                                border-radius:8px;
                                padding:12px 16px;
                                margin-bottom:10px;
                                display:flex;
                                align-items:center;
                                gap:16px;
                                box-shadow:0 1px 4px rgba(0,0,0,0.07);
                            ">
                              <div style="
                                background:{bg};color:{tc};
                                border-radius:50%;min-width:40px;height:40px;
                                display:flex;align-items:center;justify-content:center;
                                font-weight:bold;font-size:18px;flex-shrink:0;">
                                {rank}
                              </div>
                              <div style="flex:1;color:#212529;">
                                <div style="font-weight:600;font-size:1em;margin-bottom:3px;">
                                  {item["method_only"]}{row_badge_html}
                                </div>
                                <div style="font-size:0.9em;margin-bottom:2px;">
                                  🔹 <b>PRI:</b> {pri_val:.1f} &nbsp;|&nbsp;
                                  <b>RPRI:</b> {rpri_val:.2f} &nbsp;|&nbsp;
                                  <b>Δ RPRI:</b> {delta_val:.2f}
                                </div>
                                <div style="font-size:0.82em;color:#555;">
                                  Technical Efficiency: {item["tech_eff"]} / 5
                                  (Total Feasibility: {item["eff_percent"]:.1f}%) &nbsp;|&nbsp;
                                  AF: {af_val:.2f}
                                </div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if unscored:
                        with st.expander(
                            "Solutions with unavailable technical efficiency values",
                            expanded=False,
                        ):
                            for item in unscored:
                                st.markdown(
                                    f'<div style="background-color:#f0f2f6;padding:10px;'
                                    f'border-radius:6px;margin-bottom:8px;border:1px solid #ddd;color:black;">'
                                    f'<h6 style="margin:0;">- {item["name"]}</h6>'
                                    f'<p style="margin:0;font-size:0.9em;color:#555;"><i>'
                                    f"Technical efficiency values are not available for this method."
                                    f"</i></p></div>",
                                    unsafe_allow_html=True,
                                )

                st.markdown(
                    "##### 🏆 Ranked NbS Solutions by Residual Risk (RPRI)")
                seen_labels = []
                for item in st.session_state.filtered_nbs_pool:
                    lbl = item.get("row_label", "")
                    if lbl and item.get("is_primary", False) and lbl not in seen_labels:
                        seen_labels.append(lbl)

                ALL_LABEL = "🌐 All Rows Combined"
                view_options = [ALL_LABEL] + seen_labels

                st.info(
                    "Use the selector below to view the RPRI ranking for a specific Impact Model / Asset row from the Implementation Mapping Summary, or select **All Rows Combined** to see the overall ranking (each method shown once at its highest RPRI across all rows).",
                    icon="ℹ️",
                )

                selected_view = st.selectbox(
                    "📋 View ranking for:", view_options, key="rpri_view_selector"
                )

                if selected_view == ALL_LABEL:
                    render_rpri_ranking(
                        st.session_state.filtered_nbs_pool, show_row_badge=True)
                else:
                    row_pool = [
                        item
                        for item in st.session_state.filtered_nbs_pool
                        if item.get("row_label") == selected_view
                    ]
                    if row_pool:
                        infra = row_pool[0].get("infrastructure", "")
                        asset = row_pool[0].get("asset", "")
                        imp = row_pool[0].get("impact_model", "")
                        parts = [p for p in [infra, asset, imp]
                                 if p and p != "—"]
                        st.markdown(
                            f'<div style="background:#f3e5f5;border-left:4px solid #7b1fa2;padding:8px 14px;border-radius:6px;margin-bottom:12px;color:#4a148c;"><strong>Row:</strong> {" &nbsp;›&nbsp; ".join(parts)}</div>',
                            unsafe_allow_html=True,
                        )
                    render_rpri_ranking(row_pool, show_row_badge=False)
                st.divider()
                st.markdown("##### 🗺️ Cross-Row RPRI Heatmap")
                st.caption(
                    "Each cell shows the RPRI value for a given NbS method (row) across every Impact Model / Asset row (column). Blank cells mean the method does not apply to that row. Green = low residual risk · Red = high residual risk."
                )
                hm_data = {}
                hm_all_labels = []
                for _, _cr_row in st.session_state.calculated_results.iterrows():
                    _a = str(_cr_row.get("Asset", "")).strip() or "—"
                    _im = str(_cr_row.get("Impact model", "")).strip() or "—"
                    _lbl = f"{_a} — {_im}"
                    if _lbl and _lbl not in hm_all_labels:
                        hm_all_labels.append(_lbl)

                for item in st.session_state.filtered_nbs_pool:
                    m = item.get("method_only", "")
                    lbl = item.get("row_label", "")
                    rv = item.get("rpri", None)
                    st_val = item.get("status", "")
                    if not m or not lbl or st_val != "scored" or rv is None:
                        continue
                    if not item.get("is_primary", False):
                        continue
                    if m not in hm_data:
                        hm_data[m] = {}
                    if lbl not in hm_data[m] or rv > hm_data[m][lbl]:
                        hm_data[m][lbl] = rv

                if len(hm_data) == 0 and st.session_state.filtered_nbs_pool:
                    fallback_label = "All Assets"
                    for item in st.session_state.filtered_nbs_pool:
                        m = item.get(
                            "method_only",
                            item.get("name", "").split(" method for ")[0],
                        )
                        rv = item.get("rpri", None)
                        st_val = item.get("status", "scored")
                        if not m or st_val != "scored" or rv is None:
                            continue
                        if not item.get("is_primary", False):
                            continue
                        if m not in hm_data:
                            hm_data[m] = {}
                        if fallback_label not in hm_data[m] or rv > hm_data[m][fallback_label]:
                            hm_data[m][fallback_label] = rv
                    if hm_data and not hm_all_labels:
                        hm_all_labels = [fallback_label]
                hm_col_base = hm_all_labels if hm_all_labels else seen_labels

                if len(hm_data) >= 1 and len(hm_col_base) >= 1:

                    def _mean_rpri(method):
                        vals = list(hm_data[method].values())
                        return sum(vals) / len(vals) if vals else 0

                    sorted_methods = sorted(hm_data.keys(), key=_mean_rpri)
                    ALL_COL_LABEL = "🌐 All Rows Combined"
                    col_labels = hm_col_base + [ALL_COL_LABEL]
                    row_labels = sorted_methods
                    z_matrix = []
                    text_matrix = []

                    for method in row_labels:
                        z_row = []
                        t_row = []
                        row_vals = []
                        for lbl in hm_col_base:
                            val = hm_data[method].get(lbl, None)
                            z_row.append(val if val is not None else np.nan)
                            t_row.append(
                                f"{val:.2f}" if val is not None else "—")
                            if val is not None:
                                row_vals.append(val)
                        if row_vals:
                            agg_val = sum(row_vals) / len(row_vals)
                            z_row.append(agg_val)
                            t_row.append(f"{agg_val:.2f}")
                        else:
                            z_row.append(np.nan)
                            t_row.append("—")
                        z_matrix.append(z_row)
                        text_matrix.append(t_row)

                    z_min = 0
                    z_max = 5

                    def _short(label, max_len=28):
                        return label if len(label) <= max_len else label[: max_len - 1] + "…"

                    short_col_labels = [_short(l) for l in col_labels]
                    fig_height = max(300, 36 + 30 * len(row_labels))

                    def _rpri_cell_color(val):
                        """Return fill colour for a cell given its RPRI value (0–5)."""
                        if val is None or (isinstance(val, float) and np.isnan(val)):
                            return "#f0f0f0"
                        stops = [
                            (0.00, (27, 94, 32)),
                            (0.14, (46, 125, 50)),
                            (0.28, (174, 213, 129)),
                            (0.50, (255, 241, 118)),
                            (0.72, (255, 183, 77)),
                            (0.86, (245, 124, 0)),
                            (1.00, (211, 47, 47)),
                        ]
                        t = max(0.0, min(1.0, val / 5.0))
                        for i in range(len(stops) - 1):
                            t0, c0 = stops[i]
                            t1, c1 = stops[i + 1]
                            if t0 <= t <= t1:
                                r = (t - t0) / (t1 - t0)
                                rgb = tuple(
                                    int(c0[j] + r * (c1[j] - c0[j])) for j in range(3))
                                return f"rgb{rgb}"
                        return f"rgb{stops[-1][1]}"

                    def _font_color(val):
                        """White text on dark cells, black on light ones."""
                        if val is None or (isinstance(val, float) and np.isnan(val)):
                            return "#888888"
                        return "white" if val >= 3.5 or val <= 0.7 else "black"

                    tbl_cell_values = [row_labels]
                    tbl_fill_colors = [["#1565c0"] * len(row_labels)]
                    tbl_font_colors = [["white"] * len(row_labels)]

                    for ci, col_lbl in enumerate(short_col_labels):
                        col_vals = [z_matrix[ri][ci]
                                    for ri in range(len(row_labels))]
                        col_texts = [text_matrix[ri][ci]
                                     for ri in range(len(row_labels))]
                        tbl_cell_values.append(col_texts)
                        tbl_fill_colors.append(
                            [_rpri_cell_color(v) for v in col_vals])
                        tbl_font_colors.append(
                            [_font_color(v) for v in col_vals])

                    hm_fig = go.Figure(
                        go.Table(
                            columnwidth=[220] + [90] * len(short_col_labels),
                            header=dict(
                                values=["<b>NbS Method</b>"]
                                + [f"<b>{l}</b>" for l in short_col_labels],
                                fill_color="#1565c0",
                                font=dict(color="white", size=11),
                                align=["left"] + ["center"] *
                                len(short_col_labels),
                                height=36,
                                line=dict(color="white", width=1),
                            ),
                            cells=dict(
                                values=tbl_cell_values,
                                fill_color=tbl_fill_colors,
                                font=dict(color=tbl_font_colors, size=11),
                                align=["left"] + ["center"] *
                                len(short_col_labels),
                                height=28,
                                line=dict(color="white", width=1),
                            ),
                        )
                    )

                    hm_fig.update_layout(
                        height=fig_height,
                        margin=dict(l=0, r=0, t=10, b=10),
                        paper_bgcolor="white",
                    )

                    st.plotly_chart(hm_fig, use_container_width=True)
                    st.markdown(
                        """
                        <div style="display:flex;gap:10px;flex-wrap:wrap;
                                    margin-top:4px;font-size:0.82em;align-items:center;">
                          <span style="background:#1b5e20;color:white;padding:2px 8px;
                                       border-radius:4px;">Very low RPRI</span>
                          <span style="background:#aed581;color:black;padding:2px 8px;
                                       border-radius:4px;">Low–medium</span>
                          <span style="background:#fff176;color:black;padding:2px 8px;
                                       border-radius:4px;">Medium</span>
                          <span style="background:#ffb74d;color:black;padding:2px 8px;
                                       border-radius:4px;">Medium–high</span>
                          <span style="background:#d32f2f;color:white;padding:2px 8px;
                                       border-radius:4px;">High RPRI</span>
                          <span style="background:#f0f0f0;color:#888;padding:2px 8px;
                                       border-radius:4px;">— Not applicable</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:
                    st.warning(
                        "⚠️ Heatmap could not render. Open the diagnostics expander above to see what data is available. Ensure the RPRI ranking has been calculated and that primary solutions are assigned.",
                    )
    else:
        st.warning("Please run Step 7.1 first.")
