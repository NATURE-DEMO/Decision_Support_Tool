# Application overview

The application provides a public **Decision Support Tool** with the Custom Site Analysis workflow, and a sign-up **High Resolution DST** that adds the pre-evaluated demonstrator-site configurations alongside the same Custom Site Analysis.

**Production URL**: [https://nature-demo-dst.dic-cloudmate.eu](https://nature-demo-dst.dic-cloudmate.eu)

Access to the High Resolution DST requires a user account — see [Authentication](authentication.md) for login, sign-up, role assignment, and password management.

---

## Two analysis modes

The application provides two distinct analysis modes from a single unified interface:

| Mode | Scope | Levels covered | Where to start |
|------|-------|----------------|----------------|
| **[Demonstrator sites](specific_site.md)** | Six pre-configured site configurations covering the five NATURE-DEMO demonstration sites | Level 1 · Level 2 · Level 3 | Click any demo site card in the sidebar |
| **Custom Site Analysis** | Any user-defined location in Europe via polygon drawing | Level 1 · Level 2 (with NbS scoring and ranking) | Click the 🔬 button in the sidebar, then complete the [Extraction tab](custom_extraction.md) |

Demonstrator-site content is loaded from the project GitHub repository at runtime — no static data is bundled in the deployed app. Custom Site analyses extract OpenStreetMap data via the Overpass API and call the IBM clima-ind-viz API for climate indicator values.

---

## User-guide pages

| Page | What it covers |
|------|----------------|
| [Authentication](authentication.md) | Login, sign-up, user roles, password management, admin panel |
| [Layout](layout.md) | Sidebar contents, main content area, application startup flow |
| [Demonstrator sites](specific_site.md) | Demo sites, Site Info tab, Level 1, Level 2, Level 3 |
| [Custom site — Extraction](custom_extraction.md) | Infrastructure selection, polygon drawing, OSM extraction, AI context report |
| [Custom site — Level 1](custom_level1.md) | Scope table, perceived risk rating, NbS solution scoring with SSF/SEI |
| [Custom site — Level 2](custom_level2.md) | 7-step PRI = HI × EI × VI workflow, NbS ranking, RPRI residual risk |
| [Exporting results](exporting.md) | Charts, tables, AI reports, snapshots, audit CSV |
| [Quick reference](quick_reference.md) | Mode comparison, Level 2 step checklist, GitHub content reference |
| [Troubleshooting](troubleshooting.md) | Common warnings and recovery steps |

For the methodological background see the [Methodology](../methodology/framework.md) section. For the platform architecture and API integration see [Architecture](../architecture/overview.md).

---

## Companion tool — European Climate Data Visualisation

A companion application is hosted at [naturedemo-clima-ind.dic-cloudmate.eu](https://naturedemo-clima-ind.dic-cloudmate.eu), developed and maintained by IBM Research. This is the interactive front-end of the IBM clima-ind-viz API that also drives the Level 2 Hazard Index calculation in the Custom Site Analysis. It provides:

- City- and coordinate-based location search across Europe.
- Interactive time-series charts for the EURO-CORDEX climate indices, with historical data and RCP4.5/RCP8.5 projections to 2100.
- Scenario comparison with ensemble uncertainty bands across GCM–RCM combinations.

The companion tool can be used independently to explore climate indicator data for any European location before or alongside a full Level 2 analysis.

!!! note "AI-generated content"
    Several application views call Google Gemini for narrative interpretation of risk results, climate classification, and infrastructure context. Every AI output is preceded by a yellow-bordered disclosure banner. See [AI-generated content & responsible use](../acknowledgments.md#ai-generated-content-and-responsible-use) for the project's AI-ethics policy.
