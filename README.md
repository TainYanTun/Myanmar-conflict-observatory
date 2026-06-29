# Healthcare Interference Conflict Event (HICE) Detection Framework

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/TainYanTun/HICE-Framework)

The **HICE Detection Framework** is a deterministic rule-based NLP framework for detecting healthcare interference from unstructured conflict narrative text. It includes a standalone Python package (`hice_framework/`), an interactive analytical dashboard, and a formal research manuscript validated through a Myanmar case study (2021–2025).

## Core Components

### 1. HICE Detection Framework (`hice_framework/`)
A standalone, importable Python package implementing a three-layer detection pipeline:

- **Layer 1 — Structural Gate**: Only kinetic events (battles, explosions, violence against civilians) proceed to NLP.
- **Layer 2a — Health Entity Gate**: Events must contain a health ontology term (hospital, clinic, doctor, nurse, etc.).
- **Layer 2b — Bidirectional Keyword Coupling**: Four parallel signals (proximity, targeting patterns, action phrases, soft casualty coupling) evaluated within a 45-character window.
- **Layer 3 — Bystander Disambiguation**: F1/F4 (civilian casualty lists), F2 (humanitarian aid), and F3 (spatial proximity) false-positive filters.

**Performance**: 96.0% precision validated via 3-pass AI-assisted audit (n=450). Spearman's ρ ≥ 0.995 under weight perturbations.

### 2. Interactive Dashboard (`server.py`)
A FastAPI-based web dashboard with six analytical tabs:
- Overview, Records, Geospatial, Temporal, Actor Network, Pipeline Simulator

### 3. Research Manuscript (`research/main.tex`)
Full paper documenting the HICE framework, Myanmar case study (463 HICE incidents from 80,000+ ACLED events, Feb 2021–Apr 2025), sensitivity analysis, and category-level validation.

## Quick Start

### Requirements
- Python 3.9+
- `pip install -r requirements.txt`

### Run HICE Detection
```python
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type
import pandas as pd

df = pd.read_csv('data/myanmar_conflict_clean.csv')
mask = detect_hice_from_source(df, ACLEDAdapter())
notes = df['notes'].fillna('').str.lower()
types = classify_hice_type(notes)
hice_events = df[mask].copy()
hice_events['hice_type'] = types[mask]
```

### Launch Dashboard
```bash
python server.py
```

### Run Validations
```bash
python scripts/validation/run_all.py
```

## HICE Categories (Priority Order)
| Category | Weight | Description |
|---|---|---|
| Personnel Targeting | 1.0 | Medical staff killed, arrested, shot, or abducted |
| Systemic Attack | 0.9 | Infrastructure damage + staff presence |
| Infrastructure Damage | 0.6 | Facility bombed, burned, shelled, or looted |
| Access Disruption | 0.5 | Closures, blockades, or proximity violence |
| Humanitarian Disruption | 0.3 | Supply chain or logistics interference |

## Project Structure
```
├── hice_framework/          # Standalone Python package
│   ├── __init__.py          # Public API
│   ├── _adapter.py          # SourceAdapter ABC, ACLEDAdapter, UCDPGEDAdapter
│   ├── _detector.py         # Detection pipeline + classification
│   ├── _signals.py          # 5 pure signal functions
│   └── _vulnerability.py    # VulnerabilityScorer, SensitivityAnalyzer
├── scripts/
│   ├── validation/          # Organized validation pipeline
│   │   ├── run_audit.py
│   │   ├── run_category_audit.py
│   │   ├── run_sensitivity.py
│   │   └── run_all.py
│   └── generate_*.py        # Figure generation scripts
├── server.py                # FastAPI dashboard
├── templates/dashboard.html # Jinja2 template
├── static/style.css         # Apple design tokens
├── research/                # Paper manuscript + figures
│   ├── main.tex
│   └── assets/
├── validation/              # Audit outputs
└── data/                    # ACLED data (gitignored)
```

## Data Source
All analysis is based on the [ACLED](https://acleddata.com/) dataset covering Feb 1, 2021 to Apr 2, 2025 (80,000+ events). The framework's adapter architecture also supports UCDP GED ingestion for cross-source validation.

## Ethical Framework
- **Do No Harm**: Geospatial resolution limited to prevent tactical exploitation.
- **Verified Floor**: ACLED data is treated as a confirmed minimum; actual figures in communication-blackout regions are likely higher.
- **ICRC Alignment**: Data governance follows the *ICRC Handbook on Data Protection in Humanitarian Action*.

## Collaborators
- **Tain Yan Tun** — Lead Engineer & Computational Data Scientist
- **Pimpa Cheewaprakobkit** — Faculty Advisor, Asia Pacific International University

## License
MIT License. Conflict data sourced from ACLED.
