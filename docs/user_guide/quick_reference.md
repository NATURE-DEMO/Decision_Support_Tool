# Quick Reference

## Analysis mode comparison

| | Specific Site DST | Custom Site Analysis |
|--|------------------|---------------------|
| **Entry point** | Click a demo site card in the sidebar | Click 🔬 in the sidebar |
| **Location** | Pre-configured (6 demo site configurations) | User-drawn polygon, any location in Europe |
| **Level 1** | Pre-loaded expert consensus from GitHub; editable by expert/admin users | User-defined scope table; interactive KPI rating |
| **Level 2** | GitHub-hosted tables and reports | 7-step interactive calculator |
| **Level 3** | GitHub-hosted data per site | Not available |
| **Saving** | Expert inputs persist to Supabase automatically on save | Manual snapshot (expert/admin only); load/delete from Extraction tab |
| **Best for** | NATURE-DEMO partners; WP4 validation workshops | Any user assessing a new European location |

---

## Level 2 step checklist (Custom Site Analysis)

| Step | Action | Required |
|------|--------|:--------:|
| 1 | Build scope table using cascaded infrastructure / climate driver / impact type filters | ✅ |
| 2 | Review table; optionally add custom impact models | — |
| 3 | Set coordinates; select RCP scenario and time horizon; click **Calculate Hazard Variation & Level** | ✅ |
| 4 | Enter CAPEX / revenues per asset, or accept default EI = 3 | ✅ |
| 5.1 | Set Sensitivity Index (1–5) for each row | ✅ |
| 5.2 | Configure Adaptive Capacity per asset (AC₀, service life, maintenance, topology) | — |
| 6 | Click **Calculate the Potential Risk Index (PRI)** | ✅ |
| 7.1 | Identify NbS solutions (automatic extraction or manual selection) | ✅ |
| 7.2 | Configure SSF / SEI / HIA factors; review ranked NbS list | — |

---

## Hazard Index (HI) scoring thresholds

| % change vs. historical baseline | HI score |
|----------------------------------|:--------:|
| No change | 0 |
| ≤ 10 % | 1 |
| ≤ 25 % | 2 |
| ≤ 50 % | 3 |
| ≤ 75 % | 4 |
| ≤ 100 % | 5 |

---

## Exposure Index (EI) matrix

|  | Revenues < 1 M€ | Revenues 1–10 M€ | Revenues > 10 M€ |
|--|:-:|:-:|:-:|
| **CAPEX < 10 M€** | 1 | 2 | 3 |
| **CAPEX 10–100 M€** | 2 | 3 | 4 |
| **CAPEX > 100 M€** | 3 | 4 | 5 |

If economic data are not available, a default EI = 3 (neutral conservative baseline) is applied to all rows.

---

## GitHub content update reference (Specific Site DST)

| Tab | GitHub path | File naming convention | Rendered as |
|-----|-------------|------------------------|-------------|
| Site Info | `texts/{site_key}/` | `NN_Title.txt` | Justified paragraph under heading |
| Level 1 interpretation | `texts/{site_key}/` | `interpretation.txt` | Narrative text |
| Level 2 | `texts/{site_key}/level2/` | `Introduction.txt`, `Methods.txt`, `NN_*.xlsx`, `Interpretations.txt`, `NbS.txt` | Text + interactive sortable table |
| Level 3 | `texts/{site_key}/level3/` | `NN_*.txt`, `NN_*.xlsx` | Grouped by numeric prefix — text then table |

**Site keys**: `demo1a`, `demo1b`, `demo2`, `demo3`, `demo4`, `demo5`

Files not present for a site are silently skipped. Content can be updated at any time by committing correctly named files to the repository — no code deployment is required.

---

## AI-generated content — responsible use

Google Gemini (`gemini-2.5-flash-lite`) is used in four places within the Custom Site Analysis:

| Report | Triggered by |
|--------|-------------|
| Geographical & Infrastructure Context (C1) | Completing polygon extraction |
| Köppen-Geiger Climate Interpretation (C2) | Completing polygon extraction |
| Level 1 Interpretation | "Generate Interpretation Report" button |
| PRI Assessment Report | "Generate PRI Assessment Report" button in Step 6 |

All AI outputs are:
- Clearly labelled with disclosure header and footer banners
- Accompanied by a **View Raw Data Fed to AI** expander showing the model inputs
- Generated using embedded reference examples only — no external internet search

AI content is provided as contextual background to support expert judgement, not to replace it. Results should be reviewed critically before inclusion in any formal risk assessment or planning document.

---

## Exporting results

| Output | How to export |
|--------|--------------|
| **Charts** (radar, consequence matrices, PRI plots, RPRI heat maps) | Hover over chart → click 📷 camera icon in the top-right toolbar → downloads as PNG |
| **Data tables** (`st.dataframe`) | Click any cell, select a range, then copy with Ctrl+C / Cmd+C and paste into Excel |
| **AI reports** | Select the report text in the browser and copy |
| **PRI assessment report** | Click **Download Report as Text** → downloads `PRI_Assessment_Report.txt` |
| **Expert audit trail** (admin only) | Admin Panel → 📋 Audit → **📥 Download Audit CSV** → downloads `expert_inputs_audit.csv` |
| **Saved snapshots** | Reload via 📂 My Saved Analyses panel; raw JSON accessible via Supabase dashboard |

!!! warning "No auto-save"
    The DST does not auto-save session state. Closing or refreshing the browser discards all unsaved inputs and results. Expert and admin users should use **💾 Save Level 1** and **💾 Save Level 2** before ending a session.

---

## Companion tool — European Climate Data Visualisation

An interactive climate data explorer is available at **[naturedemo-clima-ind.dic-cloudmate.eu](https://naturedemo-clima-ind.dic-cloudmate.eu)**. It provides city- and coordinate-based location search, time-series charts for all EURO-CORDEX climate indices, and scenario comparison with ensemble uncertainty bands. It can be used independently to explore climate indicator values for any European location before or alongside a Level 2 analysis, and serves as a manual lookup when the Level 2 API call returns no data.
