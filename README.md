<div align="center">
  <img src="assets/icon.png" alt="HICE Framework" width="40%">


# HICE Framework

Rule-based NLP toolkit for detecting attacks on healthcare in conflict zones from free-text event data.
Source-agnostic adapter pattern, interactive dashboard, MIT license.<br>
[About](#about) · [Install](#install) · [Quick Start](#quick-start) · [Documentation](#documentation) · [Contributing](#contributing)

</div>

## About

HICE (Healthcare Interference Conflict Event) is a deterministic rule-based NLP pipeline that detects healthcare targeting in conflict zones from unstructured narrative text — without requiring labeled training data or machine learning models. It uses a three-layer architecture: a structural gate that filters for violent events, bidirectional keyword coupling within a 45-character proximity window, and bystander disambiguation to filter false positives. Results are classified into five impact categories and scored regionally for vulnerability triage.

The framework is source-agnostic via plug-in adapters. Currently supports ACLED (used in the Myanmar case study) and UCDP GED, with a public adapter interface for any conflict event dataset.

**Performance:** 96.0% validated precision (3-pass AI audit, n=450). Regional rankings stable at Spearman's ρ ≥ 0.9926 under weight perturbations.

## Install

```bash
pip install git+https://github.com/TainYanTun/HICE-Framework.git
```

Or clone and install locally:

```bash
git clone https://github.com/TainYanTun/HICE-Framework.git
pip install HICE-Framework/hice_framework/
```

Requires Python 3.10+. Dependencies (pandas, numpy, scipy) install automatically.

## Quick Start

```python
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type, VulnerabilityScorer

df = pd.read_csv("myanmar_conflict_clean.csv")
mask = detect_hice_from_source(df, ACLEDAdapter())
hice_events = df[mask].copy()
hice_events["hice_type"] = classify_hice_type(hice_events["notes"].fillna("").str.lower())

scorer = VulnerabilityScorer()
ranking = scorer.score(hice_events, admin_col="admin1")
print(ranking.head(10))
```

Full walkthrough: [`docs/Usage_Guide.md`](docs/Usage_Guide.md)

### Launch Dashboard

```bash
python scripts/precompute.py
uvicorn server:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

### Run Validation Suite

```bash
python scripts/validation/run_all.py
```

Output written to `validation/validation_summary.json`.

## Documentation

| Guide                                                               | Description                                                                      |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [Usage Guide](docs/Usage_Guide.md)                                   | End-to-end walkthrough with data loading, detection, classification, scoring     |
| [Detection Pipeline](docs/HICE_Detection_Pipeline.md)                | Three-layer architecture: structural gate, keyword coupling, bystander filtering |
| [Signal System](docs/Signal_System.md)                               | All keyword patterns, proximity window, bystander regex rules                    |
| [Classification](docs/Classification_System.md)                      | Five-category priority system with validation results                            |
| [Source Adapters](docs/Source_Adapters.md)                           | Adapter pattern for ACLED, UCDP GED, custom datasets                             |
| [Vulnerability Scoring](docs/Vulnerability_Scoring.md)               | Score formula`Σ(w × (1+ln(F+1)))` and sensitivity analysis                   |
| [Vulnerability Score — Worked Example](docs/vulnerability_score.md) | Formula breakdown, category weights, full example case calculation               |
| [Validation Framework](docs/Validation_Framework.md)                 | AI audit, category validation, sensitivity methodology                           |
| [Dashboard API](docs/Dashboard_API.md)                               | FastAPI routes, precompute pipeline, simulator                                   |

## Architecture

| Layer | Step                                                                     | Status |
| ----- | ------------------------------------------------------------------------ | ------ |
| 1     | Structural gate — kinetic events only                                   | ✅     |
| 2a    | Health keyword detection (23 patterns)                                   | ✅     |
| 2b    | Bidirectional proximity coupling (45-char window)                        | ✅     |
| 2c    | Targeting verbs, action phrases, soft casualty coupling                  | ✅     |
| 3     | Bystander disambiguation (F1 civilian lists, F2 aid context, F3 spatial) | ✅     |
| —    | Five-category HICE classification                                        | ✅     |
| —    | Regional vulnerability scoring with sensitivity analysis                 | ✅     |
| —    | Interactive dashboard with pipeline simulator                            | ✅     |

### HICE Impact Categories

| Category                | Weight | Description                                       |
| ----------------------- | ------ | ------------------------------------------------- |
| Personnel Targeting     | 1.0    | Medical staff killed, arrested, shot, or abducted |
| Systemic Attack         | 0.9    | Infrastructure damage + staff present             |
| Infrastructure Damage   | 0.6    | Facilities bombed, burned, shelled, looted        |
| Access Disruption       | 0.5    | Closures, blockades, proximity violence           |
| Humanitarian Disruption | 0.3    | Supply chain or logistics interference            |

## Data Source

The Myanmar case study uses [ACLED](https://acleddata.com/) data (Feb 2021–Apr 2025, 80,000+ events). The adapter architecture also supports UCDP GED and any custom dataset with free-text narrative columns.

## Ethical Framework

- **Do No Harm**: Geospatial resolution limited to administrative region level to prevent tactical exploitation.
- **Verified Floor**: Detected counts are confirmed minimums; actual figures in communication-blackout regions are likely higher.
- **ICRC Alignment**: Data governance follows the *ICRC Handbook on Data Protection in Humanitarian Action*.

## Contributing

Contributions welcome. See [docs/](docs/) for system documentation and methodology details.

## License

MIT License. Conflict data sourced from ACLED.