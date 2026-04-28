# Troubleshooting

## Application shows a loading spinner for more than 60 seconds

The Streamlit Community Cloud server enters sleep mode after approximately 30 minutes of inactivity. Wait up to 90 seconds for the server to restart — the page will load automatically once it wakes. If it does not load after two minutes, refresh the browser. Persistent failures may also indicate a temporary Supabase outage or a network issue; verify that `https://nature-demo-dst.dic-cloudmate.eu` is reachable.

---

## "Database initialisation failed" warning at startup

The application could not connect to Supabase. For locally deployed instances, verify that `SUPABASE_URL` and `SUPABASE_KEY` are correctly set in `.streamlit/secrets.toml`. For Streamlit Community Cloud, check the Secrets settings panel in the Streamlit dashboard. See [Deployment](../deployment.md) for the full secrets configuration.

---

## "GEMINI_API_KEY not found" warning banner

The `GOOGLE_API_KEY` secret is missing or invalid. AI-generated reports (climate context, PRI assessment narratives, interpretation reports) will be unavailable, but the rest of the application functions normally. Set the key in `.streamlit/secrets.toml` for local deployments or in the Streamlit Cloud Secrets panel.

---

## Overpass API returns no data or the extraction times out

The OpenStreetMap Overpass API has rate limits and may be temporarily overloaded. If the drawn polygon is very large (more than a few square kilometres), reduce its size. Wait 30–60 seconds and click **Extract Information** again without redrawing the polygon.

---

## Level 2 "Calculate Hazard Variation & Level" returns no values

This occurs when the polygon centroid or manually entered coordinates fall outside the EURO-CORDEX EUR-11 domain (~25°W–45°E, 27°N–72°N), or when the clima-ind-viz API is temporarily unavailable. Verify that the coordinates are within Europe and that `https://naturedemo-clima-ind.dic-cloudmate.eu` is reachable. Use **Delete rows without climate information** to remove any rows that returned no data before proceeding. If the API is unavailable, use the [companion climate data tool](quick_reference.md#companion-tool--european-climate-data-visualisation) to look up indicator values manually and enter them directly into the Hazard Level cells via the double-click override, then commit with **Save Hazard Changes**.

---

## A loaded analysis snapshot appears incomplete or causes errors

Snapshots save the complete session state as JSON. If the application was updated after a snapshot was saved, some session-state keys may no longer match the current schema. Delete the affected snapshot and recreate the analysis from the current step.

---

## The Köppen-Geiger map renders blank or with missing tiles

The OpenTopoMap basemap used for the Köppen overlay requires an internet connection. A blank background indicates a network issue with the tile server. The climate class code and interpretation are still extracted and reported correctly; only the visual basemap is affected.
