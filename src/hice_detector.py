"""
Backward-compatible re-export layer.

All detection logic has moved to the ``hice_framework`` package (v1.0.0).
This module re-exports everything for existing code that imports from
``src.hice_detector``.
"""
from hice_framework import (  # noqa: F401
    ACLEDAdapter,
    UCDPGEDAdapter,
    SourceAdapter,
    detect_hice,
    detect_hice_from_source,
    classify_hice_type,
    calculate_hice_intensity,
    extract_health_keyword_counts,
    # signal functions (used internally by detect_hice)
    compute_health_mask,
    compute_targeting_mask,
    compute_phrase_mask,
    compute_soft_health_mask,
    compute_proximity_mask,
    compute_bystander_mask,
)
from hice_framework._signals import (  # noqa: F401
    HEALTH_TERMS,
    TARGETING_PATTERN,
    ACTION_PHRASES,
    SOFT_HEALTH_PATTERN,
    HEALTH_INFRA,
    ATTACK_TERMS,
    PROXIMITY_WINDOW,
    ENUMERATION_FP_PATTERN,
    ENUMERATION_FP_NEGATIVE,
    HOSPITAL_BYSTANDER_PATTERN,
    HOSPITAL_BYSTANDER_NEGATIVE,
)
