# HICE Framework Usage Guide

End-to-end walkthrough from installation to regional vulnerability ranking.

The framework works with **any conflict event dataset** (ACLED, UCDP GED, ICEWS, or custom sources) via source adapters. See [Using Different Data Sources](#using-different-data-sources) below.

## Installation

```bash
pip install hice_framework/
```

Requires Python 3.10+. Dependencies (`pandas`, `numpy`, `scipy`) install automatically.

## Minimal Example

```python
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type, VulnerabilityScorer
import pandas as pd

# 1. Load your ACLED data
df = pd.read_csv("myanmar_conflict_clean.csv")

# 2. Detect HICE events (returns boolean mask)
mask = detect_hice_from_source(df, ACLEDAdapter())
hice_events = df[mask].copy()
print(f"Detected {len(hice_events)} HICE events")

# 3. Classify into 5 impact categories
hice_events["hice_type"] = classify_hice_type(hice_events["notes"].fillna("").str.lower())
print(hice_events["hice_type"].value_counts())

# 4. Score regional vulnerability
scorer = VulnerabilityScorer()
ranking = scorer.score(hice_events, admin_col="admin1")
print(ranking.head(10))
```

## Step-by-Step Breakdown

### Step 1: Load your data

The framework works with any conflict event dataset that has a free-text narrative column. For ACLED data:

```python
df = pd.read_csv("myanmar_conflict_clean.csv", low_memory=False)
```

### Step 2: Detect HICE events

The `ACLEDAdapter` maps ACLED columns to the pipeline's expected format:

```python
from hice_framework import ACLEDAdapter, detect_hice_from_source

mask = detect_hice_from_source(df, ACLEDAdapter())
hice_events = df[mask].copy()
```

For other data sources (UCDP GED, ICEWS), use the appropriate adapter or create a custom one:

```python
from hice_framework import UCDPGEDAdapter

mask = detect_hice_from_source(df, UCDPGEDAdapter())
```

### Step 3: Classify each event

Five categories evaluated in priority order: personnel_targeting > systemic_attack > infrastructure_damage > access_disruption > humanitarian_disruption.

```python
from hice_framework import classify_hice_type

hice_events["hice_type"] = classify_hice_type(hice_events["notes"].fillna("").str.lower())
```

### Step 4: Score regions

The `VulnerabilityScorer` computes:

```
Score_r = sum(w_i * (1 + ln(F_i + 1)))
```

```python
from hice_framework import VulnerabilityScorer

scorer = VulnerabilityScorer()
ranking = scorer.score(hice_events, admin_col="admin1")
```

### Step 5: Check rank stability

Test whether the regional ranking is sensitive to weight choices:

```python
sensitivity = scorer.sensitivity_analysis(hice_events, admin_col="admin1")
print(f"Minimum Spearman's rho: {sensitivity['rho'].min():.4f}")
```

## Using Different Data Sources

### ACLED (default)

Your CSV must have columns: `notes`, `event_type`, `sub_event_type`.

```python
mask = detect_hice_from_source(df, ACLEDAdapter())
```

### UCDP GED

Your CSV must have columns: `source_article`, `type_of_violence`.

```python
mask = detect_hice_from_source(df, UCDPGEDAdapter())
```

### Custom source

Implement the `SourceAdapter` interface:

```python
from hice_framework import SourceAdapter, detect_hice_from_source

class MyAdapter(SourceAdapter):
    def get_notes(self, df):
        return df["narrative"].fillna("").str.lower()

    def get_structure_mask(self, df):
        return df["event_type"].isin(["Battle", "Explosion", "Attack"])

mask = detect_hice_from_source(df, MyAdapter())
```

## Running the Validation Suite

Reproduce the published validation results:

```bash
python3 scripts/validation/run_all.py
```

This runs:

- **AI precision audit** (3 passes of n=150, ~96.0%)
- **Category validation** (per-category precision)
- **Sensitivity analysis** (rank stability)

Output written to `validation/validation_summary.json`.

## Running the Research Dashboard

```bash
# Pre-compute dashboard data
python3 scripts/precompute.py

# Start the web server
uvicorn server:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 to explore the interactive dashboard.