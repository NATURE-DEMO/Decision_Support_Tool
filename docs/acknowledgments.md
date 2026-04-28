# Acknowledgments

## Funding

This work is part of the [**NATURE-DEMO** project](https://nature-demo.eu), funded by the European Union's Horizon Europe research and innovation programme under grant agreement No. **101157448**.

The views and opinions expressed are those of the authors only and do not necessarily reflect those of the European Union or the European Climate, Infrastructure and Environment Executive Agency (CINEA). Neither the European Union nor the granting authority can be held responsible for them.

---

## Climate data sources

We gratefully acknowledge the following data providers and climate modelling initiatives:

- **[Copernicus Climate Data Store (CDS)](https://cds.climate.copernicus.eu)** — the European Union's Earth observation programme, providing access to comprehensive climate data
- **[CORDEX](https://www.cordex.org)** — the World Climate Research Programme's Coordinated Regional Climate Downscaling Experiment
- **EURO-CORDEX** — the European domain of CORDEX, providing high-resolution regional climate projections
- **[Earth System Grid Federation (ESGF)](https://esgf-node.llnl.gov)** — international collaboration for climate model data distribution

---

## NbS data

The NbS–Hazard matrix implemented in this tool is based on the **D1.1 NbS Catalogue** compiled by the NATURE-DEMO consortium, with effectiveness data drawn from Kuschel et al. (2025).

---

## Scientific libraries and software

This work builds on outstanding contributions from the scientific Python community:

### Climate processing (clima-data)
- **[xclim](https://xclim.readthedocs.io/)** — climate indices calculation
- **[xarray](https://xarray.pydata.org/)** — multi-dimensional array processing
- **[netCDF4](https://unidata.github.io/netcdf4-python/)** — NetCDF file handling

### Visualisation and geospatial
- **[Streamlit](https://streamlit.io/)** — web application framework
- **[Plotly](https://plotly.com/python/)** — interactive charts
- **[Folium](https://python-visualization.github.io/folium/)** — interactive maps
- **[geopandas](https://geopandas.org/)** — geospatial data analysis
- **[FastHTML](https://fastht.ml/)** / **[HTMX](https://htmx.org/)** — clima-ind-viz web interface

### Data and geocoding
- **[OpenStreetMap](https://www.openstreetmap.org/)** / **[Overpass API](https://overpass-api.de/)** — infrastructure extraction
- **[Nominatim](https://nominatim.org/)** — OpenStreetMap geocoding service

### AI
- **[Google Gemini](https://ai.google.dev/)** (`gemini-2.5-flash-lite`) — AI-generated contextual risk reports

---

## Climate risk assessment framework

We acknowledge the **[CLIMAAX project](https://handbook.climaax.eu/)** (CLIMAte risk and vulnerability Assessment framework and toolboX), funded by the European Union's Horizon Europe research and innovation programme under grant agreement No. 101093864, for developing standardised climate risk assessment frameworks that informed the NATURE-DEMO methodology.

---

## AI-generated content and responsible use

All AI-generated reports in the DST use **Google Gemini** (model: `gemini-2.5-flash-lite`) with a retrieval-augmented generation (RAG) approach using embedded examples. The model operates without internet search capability, ensuring that outputs are grounded exclusively in the data provided by the application — in full accordance with the project Data Management Plan and applicable AI-ethics requirements.

Every AI output is preceded by a yellow-bordered **AI-Generated Content** header banner identifying the content type and displaying the model version. The following disclaimer is shown automatically with every report:

> *AI-generated summaries and interpretations provided by this tool are intended to support understanding and exploration of geospatial and infrastructure data. These outputs are automatically generated and should not be used as the sole basis for any decisions. Users are advised to consult the detailed, tabular data provided within the tool and seek expert advice before making any decisions.*

A collapsible ⚠️ **AI Limitations & Responsible Use** expander is appended to every report, noting that AI-generated content may contain inaccuracies or omissions, that the model does not possess domain expertise, and that the system is not designed for real-time operational decision-making or emergency response without expert validation. A feedback notice at the bottom of every AI output asks users to report any inaccuracies to the project team.

!!! warning "Important"
    Never use AI-generated reports as the sole basis for infrastructure protection, emergency management, or policy decisions. Always validate AI outputs against the tabular data in the tool and consult qualified domain experts.

### Where AI is used in the application

| Location | Content generated |
|----------|-------------------|
| Custom Site — [Extraction tab](user_guide/custom_extraction.md) (C1) | Geographical & Infrastructure Context Report |
| Custom Site — [Extraction tab](user_guide/custom_extraction.md) (C2) | Köppen-Geiger climate classification interpretation |
| Custom Site — [Level 1](user_guide/custom_level1.md), Section 2 | Risk and loss matrix interpretation narrative |
| Custom Site — [Level 2](user_guide/custom_level2.md), Step 6 | PRI assessment report |
| Specific Site DST — [Site Info / Level 1](user_guide/specific_site.md) | Site description and KPI interpretation narratives |

If the Gemini API key is not configured, all AI buttons are disabled and a warning banner is displayed; the rest of the application functions normally.

---

## Attribution

When using results derived from this tool in publications, please cite:

- The relevant EURO-CORDEX dataset(s) per data provider requirements
- D2.1 — *Risk Assessment Framework for NbS-enhanced Critical Infrastructure*, NATURE-DEMO (2024)
- D1.1 — *NbS Catalogue for Critical Infrastructure*, NATURE-DEMO (2024)

For full dataset citations see the [Bibliography](bibliography.md).

---

*The NATURE-DEMO Decision Support Tool integrates nature-based solutions evidence to support climate-resilient critical infrastructure across Europe.*
