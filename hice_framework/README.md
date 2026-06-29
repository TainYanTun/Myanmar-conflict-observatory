# HICE Framework -- Healthcare Interference Conflict Event Detection

A deterministic, rule-based NLP pipeline for detecting healthcare interference
in conflict zones from unstructured event narrative text. Designed to be
**source-agnostic** -- works with ACLED, UCDP GED, ICEWS, or any conflict
event dataset with free-text narratives.

## Quick Start

Full walkthrough with step-by-step explanations: [`docs/Usage_Guide.md`](../docs/Usage_Guide.md)

This example uses ACLED data. The framework also supports UCDP GED, ICEWS, and custom sources via plug-in adapters (see [Source Adapters](#source-adapters)).

```python
import pandas as pd
from hice_framework import (
    ACLEDAdapter,
    detect_hice_from_source,
    classify_hice_type,
    VulnerabilityScorer,
)

# 1. Load your data (any source)
df = pd.read_csv("myanmar_conflict_clean.csv")

# 2. Detect HICE events
hice_mask = detect_hice_from_source(df, ACLEDAdapter())
hice_df = df[hice_mask].copy()

# 3. Classify into impact categories
hice_df["hice_type"] = classify_hice_type(
    hice_df["notes"].fillna("").str.lower()
)

# 4. Score regional vulnerability
scorer = VulnerabilityScorer()
ranking = scorer.score(hice_df, admin_col="admin1")
print(ranking[["admin1", "Score", "Rank", "HICE_count"]].head(10))

# 5. Check rank stability
sensitivity = scorer.sensitivity_analysis(hice_df, admin_col="admin1")
min_rho = sensitivity["rho"].min()
print(f"Minimum Spearman's rho: {min_rho:.4f}")
```

## Installation

**Option 1 — pip install from GitHub (recommended):**

```bash
pip install git+https://github.com/TainYanTun/Myanmar-conflict-observatory.git#subdirectory=hice_framework
```

**Option 2 — pip install from the local directory:**

```bash
pip install hice_framework/
```

**Option 3 — Copy the directory:**

Copy `hice_framework/` into your project and import:

```python
import sys
sys.path.insert(0, "path/to/hice_framework")
from hice_framework import ACLEDAdapter, detect_hice_from_source
```

Dependencies: `pandas`, `numpy`, `scipy`.

## Architecture

The HICE detection pipeline uses three layers:

```
Layer 1: Structural Filtering
    Source adapter identifies kinetic events (battles, explosions, attacks).
    This gates which rows enter the NLP pipeline.

Layer 2: Action-Keyword Coupling
    Four parallel signals are evaluated:
      - Health term mention (hospital, clinic, doctor, ...)
      - Explicit targeting language (targeted, fired upon, raided, ...)
      - Action phrases (was destroyed, was forced to close, ...)
      - Soft health coupling (casualties near medical personnel)
      - Bidirectional proximity (45-char window: attack-near-hospital)

Layer 3: Bystander Disambiguation
    Negative gate that excludes false positives:
      - F1: health terms in civilian casualty enumeration
      - F3: spatial-only proximity (hospital as location, not target)
```

## Source Adapters

The framework uses a plug-in adapter pattern. Built-in adapters:

| Adapter        | Expected Columns                    | Notes                                       |
|----------------|--------------------------------------|---------------------------------------------|
| ACLEDAdapter   | `notes`, `event_type`, `sub_event_type`, `actor1` | Standard ACLED dataset |
| UCDPGEDAdapter | `source_article`, `type_of_violence`, `side_a`   | All events are kinetic |

### Custom Adapter Example

```python
from hice_framework import SourceAdapter, detect_hice_from_source

class ICEWSAdapter(SourceAdapter):
    def get_notes(self, df):
        return df["story"].fillna("").str.lower()

    def get_structure_mask(self, df):
        return df["event_root"].isin([
            "Attack", "Fight", "Use conventional military force"
        ])

    def get_actor_presence(self, df):
        return df["actor1"].notna().astype(int)

hice_mask = detect_hice_from_source(my_icews_df, ICEWSAdapter())
```

## HICE Impact Classification

Events are classified into five mutually exclusive categories, evaluated
in priority order:

| Category                | Weight | Description                                     |
|-------------------------|--------|-------------------------------------------------|
| personnel_targeting     | 1.0    | Medical personnel directly harmed or targeted   |
| systemic_attack         | 0.9    | Combined infrastructure damage + staff impact   |
| infrastructure_damage   | 0.6    | Physical damage to clinics, hospitals, supplies |
| access_disruption       | 0.5    | Facilities closed, denied access, blocked       |
| humanitarian_disruption | 0.3    | Catch-all for other healthcare interference     |

## Vulnerability Scoring

The regional vulnerability score combines HICE type weights with logarithmic
fatality scaling:

    Score_r = sum_{i in events_r} w_i * (1 + ln(F_i + 1))

This ensures:
- Personnel targeting contributes most (highest weight)
- Outlier fatalities do not dominate (log scaling)
- Regions with many HICE events are ranked appropriately

## API Reference

### Detection

```python
detect_hice(notes, structure_mask, actor_presence) -> pd.Series
detect_hice_from_source(df, adapter) -> pd.Series
classify_hice_type(notes) -> pd.Series
calculate_hice_intensity(event_type_series) -> pd.Series
extract_health_keyword_counts(text_series) -> pd.DataFrame
```

### Signal Computation (for custom pipelines)

```python
compute_health_mask(notes)           # Health term mention
compute_targeting_mask(notes)        # Targeting language
compute_phrase_mask(notes)           # Action phrases
compute_soft_health_mask(notes)      # Casualty + staff coupling
compute_proximity_mask(notes)        # Bidirectional proximity
compute_bystander_mask(notes)        # False-positive detection
compute_event_coupling(...)          # Combine signals, exclude bystanders
```

### Vulnerability Analysis

```python
VulnerabilityScorer(weights=None, fatality_col="fatalities")
    .score(df, hice_type_col="hice_type", admin_col="admin1") -> DataFrame
    .sensitivity_analysis(df, hice_type_col, admin_col) -> DataFrame
```

## Data Requirements

Minimum columns your dataset must contain:
- **Narrative text**: free-text description of the event
- **Event type**: categorical classification (battle, explosion, etc.)
- **Actor**: name or identifier of at least one involved party

Optional but recommended:
- **Fatalities**: numeric fatality count for vulnerability scoring
- **Admin region**: administrative region name for regional ranking

## Citing

If you use this framework in academic work, please cite the associated paper:

```
@article{hice2025,
  title={Healthcare Interference Conflict Events: A Framework for
         Detection and Vulnerability Assessment},
  author={...},
  journal={...},
  year={2025}
}
```

## License

See the LICENSE file in the project root.
