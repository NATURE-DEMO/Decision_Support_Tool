# Exporting results

The DST does not provide a single "export everything" command — different artefacts of an assessment have different best-fit export paths. This page summarises the options.

!!! warning "Session state is not auto-saved"
    The DST does not auto-save session state. Closing or refreshing the browser discards all unsaved analysis inputs and results. Expert and admin users should use the 💾 **Save Level 1** and 💾 **Save Level 2** buttons before ending a session.

---

## Charts

All Plotly charts (radar charts, consequence matrices, PRI scatter plots, RPRI heat maps) display a toolbar on hover. Click the 📷 camera icon in the top-right corner of the chart to download it as a PNG image.

## Data tables

All `st.dataframe` tables in the application support in-browser column sorting, filtering, and cell selection. Selected content can be copied with Ctrl+C / Cmd+C and pasted directly into Excel or another spreadsheet application.

## AI reports

Select the text of any AI-generated report in the browser and copy it using Ctrl+C (Windows/Linux) or Cmd+C (macOS).

## Audit CSV (admin only)

The Admin Panel includes a 📥 **Download Audit CSV** button that exports the complete `inputs_v3` database table, including all expert submissions with timestamps and user IDs.

---

## Analysis snapshots (expert and admin)

Expert and admin users can persist Level 1 or Level 2 analyses as named JSON snapshots to the Supabase database. Snapshots capture the complete session state — scope table, risk and loss ratings, NbS data, SSF/SEI configuration, and the polygon centroid bounding box (≈ 5 km²) — so an analysis can be reloaded and continued later or shared with another expert account.

### Saving

At the bottom of the [Level 1](custom_level1.md#saving-a-level-1-snapshot) or [Level 2](custom_level2.md#saving-a-level-2-snapshot) tab:

1. Enter a descriptive location name in the text field.
2. Click 💾 **Save Level 1** or 💾 **Save Level 2**.

The application computes a bounding box around the polygon centroid (Custom Site Analysis) and writes the complete state record to the database.

### Loading and deleting

Saved snapshots appear in the **📂 My Saved Analyses (Last Saved per Level)** expander on the [Extraction](custom_extraction.md) tab. For each snapshot a preview panel shows snapshot metadata and a data summary before loading. Two controls are available:

- ⬆️ **Load into Analysis** — restores the complete snapshot to session state. Switch to the corresponding Level tab to continue working.
- 🗑️ **Delete Snapshot** — permanently removes the snapshot from the database after a confirmation step.

### Raw JSON access

If a snapshot must be processed externally, the raw JSON record can be exported through the Supabase dashboard for the configured project. The schema mirrors the application's session-state structure for the corresponding level.
