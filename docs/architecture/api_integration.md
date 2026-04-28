# API Integration — clima-ind-viz

The DST retrieves all climate data from the **clima-ind-viz JSON API**. The production endpoint is:

```
https://naturedemo-clima-ind.dic-cloudmate.eu
```

---

## Available endpoints

### `GET /api/indices`

Returns metadata for all 23 available climate indices.

```bash
curl -X GET "https://naturedemo-clima-ind.dic-cloudmate.eu/api/indices"
```

**Response example (truncated):**

```json
{
  "tg_year": {
    "description": "Annual mean temperature",
    "unit": "°C",
    "group": "temperature"
  },
  "rx1day_rp100": {
    "description": "100-year return level of maximum 1-day precipitation",
    "unit": "mm",
    "group": "precipitation"
  },
  "sfcwind20": {
    "description": "Annual days with wind speed ≥ 20 m/s",
    "unit": "days/year",
    "group": "wind"
  }
}
```

---

### `POST /api/search`

Geocodes a city name using OpenStreetMap Nominatim.

```bash
curl -X POST "https://naturedemo-clima-ind.dic-cloudmate.eu/api/search" \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Linz"}'
```

**Response:**

```json
{
  "status": "success",
  "query": "Linz",
  "count": 2,
  "results": [
    {
      "name": "Linz, Austria",
      "lat": 48.3069,
      "lon": 14.2858,
      "boundingbox": ["48.1869", "48.3569", "14.2058", "14.3658"],
      "type": "city"
    }
  ]
}
```

---

### `POST /api/calculate`

Calculates climate index values for a given location and scenario. This is the **primary endpoint** used by the DST.

```bash
curl -X POST "https://naturedemo-clima-ind.dic-cloudmate.eu/api/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "index_type": "rx1day_rp100",
    "scenario": "rcp85",
    "lat": 48.3069,
    "lon": 14.2858,
    "area_name": "Linz"
  }'
```

**Parameters:**

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `index_type` | ✅ | Any key from `/api/indices` | Climate index to calculate |
| `scenario` | ✅ | `historical`, `rcp45`, `rcp85` | Emissions scenario |
| `lat` | ✅ | −90 to 90 | Latitude of the asset location |
| `lon` | ✅ | −180 to 180 | Longitude of the asset location |
| `area_name` | ❌ | string | Label for the location (default: `"Query Point"`) |

**Response:**

```json
{
  "status": "success",
  "query": {
    "index_type": "rx1day_rp100",
    "scenario": "rcp85",
    "lat": 48.3069,
    "lon": 14.2858
  },
  "results": {
    "short": {
      "value": 68.4,
      "unit": "mm",
      "description": "100-year return level of maximum 1-day precipitation",
      "lower_bound": 61.2,
      "upper_bound": 77.9,
      "time_frame": "short"
    },
    "medium": { "value": 74.1, "lower_bound": 65.8, "upper_bound": 84.3, "time_frame": "medium" },
    "long":   { "value": 82.7, "lower_bound": 71.4, "upper_bound": 96.1, "time_frame": "long" }
  }
}
```

The `lower_bound` and `upper_bound` correspond to the p10 and p90 ensemble percentiles respectively.

---

## How the DST consumes the API

The DST calls `/api/calculate` once per climate index required by each active impact model. The call is wrapped in a `try/except` block with a `st.error()` fallback so that a single failed index does not abort the entire assessment.

```python
response = requests.post(
    "https://naturedemo-clima-ind.dic-cloudmate.eu/api/calculate",
    json={
        "index_type": impact["dictionary_key"],
        "scenario": selected_scenario,
        "lat": asset_lat,
        "lon": asset_lon,
        "area_name": asset_name,
    },
    timeout=30,
)
response.raise_for_status()
climate_data = response.json()
```

The returned `value` feeds directly into the HCI computation. The `lower_bound` / `upper_bound` are used to propagate uncertainty to the PRI output.

---

## Index reference

The full list of supported `index_type` values and their descriptions is available at:
[nature-demo.github.io/clima-data/indicators](https://nature-demo.github.io/clima-data/indicators/)

| Group | Key indices used by DST |
|-------|------------------------|
| Temperature | `tg_year`, `tx40`, `tn20` |
| Precipitation | `prcptot_year`, `rx1day_rp100`, `rx5day_rp100` |
| Snow & humidity | `solidprcptot_winter`, `hurs_year`, `hurs40_days` |
| Wind | `sfcwind_year`, `sfcwind10`, `sfcwind20` |
| Green infrastructure | `par_plant_level`, `spei3_severe_prob` |
