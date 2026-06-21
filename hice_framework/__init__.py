"""
HICE Framework -- Healthcare Interference Conflict Event Detection

A deterministic, rule-based NLP pipeline for detecting healthcare interference
in conflict zones from unstructured event narrative text.

Key features:
  - Source-agnostic design via adapter pattern (ACLED, UCDP GED, ICEWS, ...)
  - Three-layer detection: L1 kinetic gate, L2 keyword coupling, L3 disambiguation
  - Five-category HICE impact classification
  - HICE-type-weighted regional vulnerability scoring
  - Sensitivity analysis for rank stability validation

Quick start::

    import pandas as pd
    from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

    df = pd.read_csv("myanmar_conflict_clean.csv")
    hice_mask = detect_hice_from_source(df, ACLEDAdapter())
    df["hice_type"] = classify_hice_type(df["notes"].fillna("").str.lower())
    hice_df = df[hice_mask].copy()

    from hice_framework import VulnerabilityScorer
    scorer = VulnerabilityScorer()
    ranking = scorer.score(hice_df)
    print(ranking)
"""

from ._adapter import SourceAdapter, ACLEDAdapter, UCDPGEDAdapter
from ._detector import (
    detect_hice,
    detect_hice_from_source,
    classify_hice_type,
    calculate_hice_intensity,
    extract_health_keyword_counts,
)
from ._signals import (
    compute_health_mask,
    compute_targeting_mask,
    compute_phrase_mask,
    compute_soft_health_mask,
    compute_proximity_mask,
    compute_bystander_mask,
)
from ._vulnerability import VulnerabilityScorer, DEFAULT_WEIGHTS

__all__ = [
    # Adapters
    "SourceAdapter",
    "ACLEDAdapter",
    "UCDPGEDAdapter",
    # Detection pipeline
    "detect_hice",
    "detect_hice_from_source",
    "classify_hice_type",
    "calculate_hice_intensity",
    "extract_health_keyword_counts",
    # Signal computation
    "compute_health_mask",
    "compute_targeting_mask",
    "compute_phrase_mask",
    "compute_soft_health_mask",
    "compute_proximity_mask",
    "compute_bystander_mask",
    # Vulnerability analysis
    "VulnerabilityScorer",
    "DEFAULT_WEIGHTS",
]
