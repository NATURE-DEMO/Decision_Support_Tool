# Integrated DST

The **Integrated DST** (`pages/integrated_dst.py`) is the primary application delivered as Deliverable D2.3. It consolidates the Specific Site DST and Custom Site Analysis into a single authentication-gated Streamlit application:

**Production URL**: [https://nature-demo-dst.dic-cloudmate.eu](https://nature-demo-dst.dic-cloudmate.eu)

Access requires a user account — see [Authentication](authentication.md) for login, sign-up, and role management.

---

## Application layout

After login, the application presents two persistent panels.

**Sidebar (left)** — visible on every view, structured top to bottom:

- NATURE-DEMO project logo (links to the project website)
- Logged-in user's display name and role
- 🔐 Change Password expander
- Logout button
- 🛡️ Admin Panel expander (admin users only)
- **🔬 Custom Site Analysis & NbS Recommendation** button — activates the custom site mode
- **Select Site** section — six clickable demo site cards, each with a background photograph and site label; the active card is highlighted with a green border

**Main content area (right)** — switches between two view types depending on sidebar selection:

- **Specific Site view** — activated when a demo site card is clicked; four-tab interface: Site Info & Maps, Level 1, Level 2, Level 3
- **Custom Site Analysis view** — activated by the 🔬 button; three-tab interface: Extraction · Mapping & Data, Level 1 · Perceived Risks, Level 2 · Technical Analysis

---

## Mode 1 — Specific Site DST

### Demo sites

Six pre-configured site configurations are available, covering five NATURE-DEMO demonstration sites. The Austrian demonstrator is split into two sub-sites reflecting distinct locations within the same catchment:

| Site | Location | Primary CI / hazard focus |
|------|---------|--------------------------|
| Demo 1-A | Lattenbach Valley, Austria | Torrent control / railway — debris flows, extreme rainfall, slope instability |
| Demo 1-B | Brunntal, Austria | Alpine roads and paths — slope stability, snowmelt floods |
| Demo 2 | Brasov City, Romania | Urban green infrastructure — heat island, drought, air pollution |
| Demo 3 | Slovenia | River / flood protection — fluvial flooding, river erosion |
| Demo 4 | Zvolen, Slovakia | Road and railway crossroads — wildfire, flooding, extreme weather |
| Demo 5 | Globocica, North Macedonia | Hydropower dams — drought, sedimentation, water resource stress |

Clicking a site card loads all content from the GitHub `texts/{site_key}/` directory and opens the four-tab interface. Content is fetched dynamically at runtime via the GitHub Contents API — no data files are bundled in the deployment.

### Tab 1 — Site Info & Maps

The tab is divided into two columns.

**Left column — site description**  
Text files in `texts/{site_key}/` are fetched, sorted by numeric filename prefix, and rendered as justified paragraphs under section headings derived from the filename. New description sections can be added by uploading a correctly named `.txt` file to GitHub without any code changes.

**Right column — interactive map and climate data**  
- A Leafmap satellite-imagery map centred on the site at zoom level 15 with a location marker.
- A Köppen-Geiger Climate Classification map (1991–2020 baseline, 0.1° resolution) sampled at the site coordinates and rendered over an OpenTopoMap basemap. The identified climate class is highlighted in the 30-class colour bar.
- A pre-written climate report file fetched from GitHub.

### Tab 2 — Level 1: Perceived Risk

**Consensus data system**  
When this tab opens, two Excel files are downloaded from GitHub for the active site: the KPI condition table (5 KPIs × 5 scenarios) and the Extent of Loss table (5 KPIs × 4 scenarios). If expert or admin users have previously submitted their own assessments, all submissions — including the GitHub baseline — are averaged into a live consensus displayed to all users. Administrator submissions override the consensus for their site.

**KPIs and scenarios** — see [Level 1 methodology](../methodology/level1_qualitative.md) for full definitions. The five KPIs (SRS, AM, EC, EV, HP) are scored 1 (best) – 5 (worst) across five scenarios (CI, CI_H, CI_HG, CI_HN, CI_HNG).

Expert and admin users see an editable form below each consensus table, pre-populated with their own previously saved values. After editing any cell, click **Save** to commit values to Supabase via UPSERT; the displayed consensus updates immediately.

**Visualisations**

- **KPI Radar Chart** — Plotly radar with five axes (one per KPI); per-scenario toggle checkboxes control which scenario polygons are displayed.
- **Consequence matrices** — up to four Plotly scatter heat maps, one per hazard scenario, plotting CI condition (y-axis) against Extent of Loss (x-axis) for the five KPIs on a red-green severity background.

**Interpretation expander**  
A pre-written narrative fetched from GitHub explains the KPI values for non-specialist readers.

### Tab 3 — Level 2: Screening Tool

Level 2 content is loaded from `texts/{site_key}/level2/` in a fixed rendering order:

1. `Introduction.txt` — context and scope narrative
2. `Methods.txt` — methodology notes specific to the site
3. Numbered `.xlsx` files (e.g., `01_PRI_results.xlsx`) — rendered as interactive sortable data tables
4. `Interpretations.txt` — narrative interpretation of the results
5. `NbS.txt` — NbS recommendations for the site

Absent files are silently skipped. Adding content to a site requires only uploading a correctly named file to GitHub.

### Tab 4 — Level 3: High-Resolution Assessment

Level 3 files are loaded from `texts/{site_key}/level3/`. Files are grouped by numeric prefix — within each group, `.txt` files render first as section headings with justified text, followed by `.xlsx` files as interactive sortable tables. If no Level 3 files are present the message "No Level 3 data found." is displayed.

---

## Mode 2 — Custom Site Analysis

Activated by the **🔬 Custom Site Analysis & NbS Recommendation** button. Three tabs are presented.

!!! note "Tab order matters"
    Complete the **Extraction** tab first — it defines the polygon geometry and coordinates referenced by the Level 1 and Level 2 save functions. Saved snapshots are geo-referenced to the polygon centroid bounding box.

### Extraction tab

**Infrastructure type selection**  
Twelve chip-style toggle buttons in a 4-column grid represent infrastructure categories. Multiple categories can be selected simultaneously; selection persists when switching between tabs.

| | | | |
|-|-|-|-|
| 🚗 Roads & Highways | 🚆 Railways | 🌉 Bridges | 🔩 Tunnels |
| 💧 Dams & Water Storage | 🌳 Urban Green Spaces | 〰️ Embankments & Levees | 🛡️ Slope Stabilization |
| 🏢 Buildings | ⚡ Power & Utilities | 🌊 Water Bodies & Rivers | 🗺️ Catchment Surface Cover |

**Map and polygon drawing**  
- Enter a place name and click **Go** to pan the Folium map to the location (geocoded via Nominatim/OSM).
- Use the polygon or rectangle drawing tool (top-left toolbar) to define the area of interest.
- Click **Extract Information** to query the OpenStreetMap Overpass API for all selected CI types within the polygon.

**Extraction outputs**  
Three result blocks appear:

- **C1 — Geographical & Infrastructure Context Report** — the polygon attributes and OSM data are passed to Google Gemini, which generates a contextual infrastructure report using a retrieval-augmented approach with embedded examples (no external internet search). Displayed with AI disclosure header/footer.
- **C2 — Köppen-Geiger Climate Classification Map** — the raster is sampled at the polygon centroid; the climate code and a surrounding tile are rendered over OpenTopoMap. Gemini generates a climate interpretation report, wrapped with the same AI disclosure. A **View Raw Data Fed to AI** expander shows the inputs passed to the model.
- **C3 — Raw OSM Data Tables** — an expander shows up to 20 OSM features per selected CI type with all available tag attributes for verification.

Expert and admin users also see a **📂 My Saved Analyses (Last Saved per Level)** expander listing previously saved Level 1 and Level 2 snapshots with load and delete controls (see [Saving and loading snapshots](#saving-and-loading-analysis-snapshots)).

### Level 1 tab — Perceived Risks

The Level 1 workflow is divided into three sequential sections.

**Section 1 — Scope table definition**  
Five cascaded selectors define each row to add to the scope table:

1. Infrastructure Type (from the twelve chip categories)
2. Climate Driver (overarching climate forcing, e.g., "Change in precipitation")
3. Impact Model (filtered by infrastructure type from `modules/impact_models/`)
4. Asset (specific sub-component, filtered by infrastructure type)
5. Possible Hazards (multi-select from the canonical 29-item hazard list)

After hazards are selected, two additional multi-selects appear, populated automatically from the NbS–Hazard matrix:

- **Primary NbS Solutions** — solutions that directly address the selected hazards
- **Supportive NbS Solutions** — solutions providing indirect risk reduction or co-benefits

Click **➕ Add to Scope Table** to append the row. Each selected NbS solution creates a separate row. Rows can be removed individually (checkbox + ❌ Remove Selected) or entirely (🗑️ Clear Scope Table).

**Section 2 — Risk rating and Extent of Loss**  
For each scope item selected from a dropdown, two editable tables are presented:

- **CI Condition table** — 5 KPI rows × 5 scenario columns (CI, CI_H, CI_HG, CI_HN, CI_HNG), rated 1–5 or "Not Available". The Risk Score is auto-computed as the maximum CI_HN value across the five KPIs. Click **Save Risk Ratings** to commit.
- **Extent of Loss table** — 5 KPI rows × 4 scenario columns (CI excluded), rated 1–5. Click **Save Loss Ratings** to commit.

After saving, a KPI radar chart and consequence heat maps update automatically. A summary table at the bottom lists all scope items with their calculated Risk Scores. A **Generate Interpretation Report** button sends the current matrices to Gemini for a narrative analysis.

**Section 3 — NbS solution rating**  
For each primary NbS solution in the scope table, five criteria are rated 1–5 (or "Not Acceptable"):

| Criterion | Description |
|-----------|-------------|
| Technical Efficiency | Expected effectiveness in reducing the hazard impact |
| Implementation Cost | Capital cost relative to alternatives |
| Implementation Time | Time to deploy and achieve risk reduction |
| Environmental Impact | Net environmental effect |
| Social Acceptance | Anticipated community acceptance |

Activate **View Supportive Solutions** to reveal a separate rating table for supportive NbS.

**NbS filtration — SSF, SEI, and HIA**  
Three layers refine the NbS ranking:

- **Site-Specific Feasibility (SSF)** — nine toggle buttons for physical site constraints: Unstable/Steep Slopes, Poor Soil/Low Vegetation, Difficult Site Access, Cold Temperatures / Frost Risk, Water Scarcity, No Infrastructure/Services Access, Very Limited Space, Polluted Soil/Water/Air, Urban/Densely Populated Area. Enabling a constraint reduces the feasibility score of sensitive solutions.
- **Socio-Economic & Institutional (SEI)** — seven sliders per solution: Community Engagement, Cultural Preferences, Workforce Availability, Economic Viability, Long-term O&M Costs, Land Ownership, Regulatory Constraints (1 = Favourable, 2 = Neutral, 3 = Unfavourable).
- **Hazard Impact Assessment (HIA)** — confirmation of hazard-to-solution mapping.

A feasibility spider diagram is auto-generated from the SSF/SEI configuration for each solution. The **Final NbS Recommendation Strategy** table shows Risk Score, Suitability Index, and Suitability Score for every solution, ranked in descending order.

**Saving a Level 1 snapshot** (expert/admin only): enter a descriptive location name and click **💾 Save Level 1**. The complete state — scope table, risk and loss ratings, NbS ratings, SSF/SEI configuration — is saved as JSON to Supabase.

### Level 2 tab — Technical Analysis

Level 2 is a sequential seven-step quantitative workflow. Steps must be completed in order; each builds on the previous.

**Step 1 — Build impact model scope table**  
Three cascaded multi-select dropdowns (Infrastructure → Climate Driver → Type of Impact) progressively filter the impact model database from `modules/impact_models/`. Click **Add filtered items to Table** to append matched rows. Repeat with different filter combinations to build a full scope.

Table controls:

- **🗑️ Reset Table** — clears all rows and resets all downstream calculations
- **➕ Add Custom Impact Model** — popover for manually defining a custom entry: infrastructure type, climate driver, impact description, asset name, climate indicator code, and hazard types

**Step 2 — Review and customise**  
Inspect the accumulated rows; remove individual rows via checkbox + delete control. Custom entries are flagged in the table.

**Step 3 — Climate hazard retrieval (Hazard Index)**  
For each row, the assigned climate indicator is fetched from the clima-ind-viz API. Inputs required before calculation:

- **Location coordinates** — entered manually or transferred from the Extraction tab via **Use Polygon Centre Coordinates**
- **Climate scenario** — RCP4.5 (moderate) or RCP8.5 (high emissions)
- **Time horizon** — Short-term (2011–2040), Medium-term (2041–2070), or Long-term (2071–2100)

Click **Calculate Hazard Variation & Level** to retrieve data. The **Hazard Index (HI)** is scored 0–5 from the % change vs. the historical baseline per D2.1 Table 19 — see [Level 2 methodology](../methodology/level2_prescreening.md) for scoring thresholds. Rows without returned data can be removed with **Delete rows without climate information**. To manually override a retrieved value, double-click the Hazard Level cell and select from the dropdown, then click **Save Hazard Changes** to commit.

**Step 4 — Exposure Index (EI)**  
EI (1–5) quantifies financial exposure. Two options:

- Click **Calculate Exposure Index** without entering data to assign the default EI = 3 to all rows (conservative neutral baseline).
- Enable **Economic data for infrastructure assets are available** to enter annual revenue and CAPEX per asset. The **View Exposure Matrix Calculation Logic** expander shows how configured thresholds translate to EI scores. Custom threshold boundaries can be set by disabling **Use default threshold values**.

**Step 5.1 — Sensitivity Index**  
A data editor table allows setting the Sensitivity Index (1–5) per row:
1 = low sensitivity (asset withstands the hazard well) → 5 = high sensitivity (highly susceptible to damage).

**Step 5.2 — Adaptive Capacity (optional)**  
Enable **Configure Adaptive Capacity for Assets** to reveal the AC configuration table. For each unique asset:

| Parameter | Options | Effect on AC |
|-----------|---------|-------------|
| Initial AC₀ | 0.0 – 0.4 | Baseline value |
| Remaining service life | Greenfield / Intermediate / End-of-life | +0.10 / 0 / −0.10 |
| Maintenance level | High / Medium / Low | +0.10 / 0 / −0.10 |
| Design topology | Resilient / Acceptable / Not acceptable | +0.10 / 0 / −0.10 |

Final AC = AC₀ + sum of adjustments, capped at 0.4. The Vulnerability Index is:

$$\text{VI} = \text{Sensitivity} \times (1 - \text{AC})$$

Click **Calculate Vulnerability Index** to run the computation.

**Step 6 — Potential Risk Index (PRI)**  
Click **Calculate the Potential Risk Index (PRI)**:

$$\text{PRI} = \text{HI} \times \text{EI} \times \text{VI}$$

Results are mapped to a labelled risk tier and added to the results table. A **Generate PRI Assessment Report** button sends the results to Gemini for a structured narrative risk profile.

**Step 7.1 — NbS identification**  
Two methods for hazard identification:

- **Automatic extraction** — a built-in dictionary maps impact model entries to their most likely specific hazard types (convenient but may miss ambiguous cases; review before proceeding)
- **Manual selection** — explicit multi-select from the 29-item hazard list

The primary NbS solutions for the identified hazards are displayed; deselect irrelevant entries and click **Save Primary NbS Selection**. Supportive solutions can be added via **Configure Supportive Solutions**. An **NbS Implementation Mapping Summary** at the end shows the confirmed NbS assignment per impact model row.

**Step 7.2 — NbS filtration and ranking**  
The same SSF and SEI filtration mechanism as Level 1 (see above) refines the NbS candidate pool. Click **Calculate RPRI Ranking** to compute the **Residual Potential Risk Index (RPRI)** — the remaining risk level after the solution has been implemented. RPRI = 0 indicates complete risk elimination; higher values indicate residual risk. Solutions are ranked in ascending order of RPRI and displayed as colour-coded cards. A cross-row RPRI heat map table shows the effectiveness of all shortlisted solutions across every impact model row simultaneously, using a green-to-red colour scale to identify which solutions provide the broadest risk reduction.

**Saving a Level 2 snapshot** (expert/admin only): enter a location name and click **💾 Save Level 2**.

---

## Saving and loading analysis snapshots

Expert and admin users can persist Level 1 or Level 2 analyses as named snapshots to Supabase. Snapshots capture the complete session state — scope table, risk and loss ratings, NbS data, map coordinates — as JSON.

Saved snapshots appear in the **📂 My Saved Analyses (Last Saved per Level)** expander in the Extraction tab. For each snapshot:

- **⬆️ Load into Analysis** — restores the complete snapshot to session state; switch to the corresponding Level tab to continue working
- **🗑️ Delete Snapshot** — permanently removes the snapshot from the database after a confirmation step

A preview panel shows snapshot metadata and a data summary before loading.

---

## AI-generated content

Google Gemini (`gemini-2.5-flash-lite`) is used in four places within the Custom Site Analysis:

| Location | Content generated |
|----------|------------------|
| Extraction — C1 | Geographical & Infrastructure Context Report |
| Extraction — C2 | Köppen-Geiger climate classification interpretation |
| Level 1 — Section 2 | Risk and loss matrix interpretation narrative |
| Level 2 — Step 6 | PRI assessment report |

All AI outputs are wrapped with disclosure header and footer banners. A **View Raw Data Fed to AI** expander is available for each report so users can inspect what was passed to the model. AI-generated content is provided as contextual background and should not substitute expert judgement. No external internet searches are performed; all model calls use embedded reference examples consistent with the project's AI-ethics requirements.
