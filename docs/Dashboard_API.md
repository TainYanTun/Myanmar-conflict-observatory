# Dashboard & API

FastAPI web application with an interactive dashboard for exploring HICE detection results, plus a pipeline simulator for testing individual narratives.

**File:** `server.py`

## Architecture

```
precompute.py ──► dashboard_data.json ──► server.py ──► browser
                                                    │
                                                    └──► /simulate (POST)
```

Data flow:
1. `scripts/precompute.py` reads the ACLED CSV, runs HICE detection, generates all Plotly figures, and serializes everything to `dashboard_data.json`
2. `server.py` loads this JSON at startup and serves it via a Jinja2 HTML template
3. Optional: `POST /simulate` runs a single narrative through the full pipeline in real-time

## Routes

### `GET /`

Renders the main dashboard with 6 tabs:

| Tab | Content |
|-----|---------|
| **Overview** | HICE category pie chart, keyword frequency bar, actor categories, event type breakdown |
| **Geospatial** | Interactive map (Plotly scattermapbox) with incident points colored by HICE type |
| **Temporal** | Monthly trend line, category breakdown, cumulative incident curve |
| **Risk Assessment** | Severity index, frequency vs lethality risk matrix, vulnerability ranking bar chart, regional table |
| **Records** | Paginated data table with detail card popup (date, location, actor, notes) |
| **Simulator** | Interactive pipeline step-through: paste a narrative and see which layer catches it |

### `GET /health`

Health check endpoint. Returns `{"status": "ok"}`.

### `POST /simulate`

Runs a single narrative through the HICE detection pipeline step by step.

**Request:**
```json
{
  "text": "Military forces attacked the hospital in Sagaing, destroying the clinic and arresting medical staff."
}
```

**Response:** Returns each pipeline step (structural gate, health mask, targeting mask, action phrases, soft coupling, proximity, bystander, coupling decision) with matched text spans, timestamps, and the final HICE classification.

## Data Precomputation

**File:** `scripts/precompute.py`

Reads the most recent CSV from `data/`, runs the full HICE pipeline, generates all Plotly figures, and saves to `dashboard_data.json`.

```bash
python3 scripts/precompute.py
```

The JSON file contains:
- **meta:** Total event count, HICE count, date range
- **overview:** Serialized Plotly figure JSONs (pie, keyword, actor, event type)
- **geo:** Geospatial records with lat/lon, type, region, actor, fatalities
- **temporal:** Trend line, category breakdown, cumulative (Plotly JSON)
- **risk:** Severity index, risk matrix, vulnerability ranking (Plotly JSON + table data)
- **records:** Full event list sorted by date (descending)
- **categories:** Per-category count, label, color, percentage

## Running the Dashboard

```bash
# Development
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Production (via startup.sh)
gunicorn server:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The live dashboard is available at: https://myanmar-conflict-observatory.onrender.com/

## Pipeline Simulator

The `simulate_pipeline()` function in `server.py` runs a single text through:
1. **Structural Gate:** Checks for kinetic event language + armed actor
2. **Health Keyword Detection:** Scans for 23 health term patterns
3. **Targeting Language:** Explicit targeting verbs
4. **Action Phrases:** Passive-voice hostile actions
5. **Soft Health-Casualty Coupling:** Casualty language near health personnel
6. **Bidirectional Proximity:** 45-character window coupling
7. **Bystander Disambiguation:** F1 (enumeration) and F3 (spatial-only) checks
8. **Event Coupling Decision:** Combines all signals
9. **HICE Type Classification:** If detected, assigns one of 5 categories

Each step returns the matched text spans with character offsets, enabling highlighted rendering in the UI.

## Color Scheme

```python
HICE_COLORS = {
    "infrastructure_damage":   "#2563eb",  # Blue
    "access_disruption":       "#7c3aed",  # Purple
    "personnel_targeting":     "#dc2626",  # Red
    "humanitarian_disruption": "#64748b",  # Slate
    "systemic_attack":         "#0891b2",  # Cyan
}
```
