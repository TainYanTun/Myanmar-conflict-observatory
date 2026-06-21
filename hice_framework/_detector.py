"""
Core HICE detection pipeline.

This module implements the three-layer detection architecture:
  Layer 1 -- Structural filtering: only kinetic events pass
  Layer 2 -- Bidirectional action-keyword coupling (4 parallel signals)
  Layer 3 -- Bystander disambiguation (F1/F3/F4)

Usage::

    from hice_framework import ACLEDAdapter, detect_hice_from_source

    mask = detect_hice_from_source(df, ACLEDAdapter())
    hice_events = df[mask]
"""

import warnings
import re
import numpy as np
import pandas as pd

from ._signals import (
    compute_health_mask,
    compute_targeting_mask,
    compute_phrase_mask,
    compute_soft_health_mask,
    compute_proximity_mask,
    compute_bystander_mask,
)
from ._adapter import SourceAdapter

warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression")


def detect_hice(
    notes: pd.Series,
    structure_mask: pd.Series,
) -> pd.Series:
    """
    Run the 3-layer detection pipeline.

    Parameters
    ----------
    notes : pd.Series
        Free-text narrative column (lowercased expected).
    structure_mask : pd.Series (bool)
        True for events that pass the structural (kinetic) gate.

    Returns
    -------
    pd.Series (bool)
        True for events classified as HICE.
    """
    # L1: Gate -- only kinetic events proceed
    passed = structure_mask.astype(bool)
    gated_idx = notes.index[passed]

    # L2: Compute signals on gated rows
    gated_notes = notes.loc[gated_idx]
    health = compute_health_mask(gated_notes)
    targeting = compute_targeting_mask(gated_notes)
    phrase = compute_phrase_mask(gated_notes)
    soft = compute_soft_health_mask(gated_notes)
    proximity = compute_proximity_mask(gated_notes)
    coupling = proximity | phrase | targeting | soft

    # L3: Exclude bystander false positives
    # HICE requires: health term + linguistic coupling + not a bystander
    bystander = compute_bystander_mask(gated_notes)
    result = health & coupling & ~bystander
    mask = pd.Series(False, index=notes.index)
    mask.loc[gated_idx] = result
    return mask


def detect_hice_from_source(
    df: pd.DataFrame,
    adapter: SourceAdapter,
) -> pd.Series:
    """
    Run the full HICE detection pipeline on a DataFrame via the given adapter.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataset.
    adapter : SourceAdapter
        Adapter implementation (e.g., ``ACLEDAdapter()``).

    Returns
    -------
    pd.Series (bool)
        True for HICE-classified rows.
    """
    notes = adapter.get_notes(df)
    structure_mask = adapter.get_structure_mask(df)
    return detect_hice(notes, structure_mask)


def classify_hice_type(notes: pd.Series) -> pd.Series:
    """
    Classify each HICE event into a thematic impact category.

    Categories (evaluated in priority order):
      1. personnel_targeting    Medical personnel directly harmed
      2. systemic_attack        Infrastructure damage + staff present
      3. infrastructure_damage  Physical damage to health infrastructure
      4. access_disruption      Facilities closed or blocked
      5. humanitarian_disruption  Catch-all

    Parameters
    ----------
    notes : pd.Series
        Lowercased narrative text.

    Returns
    -------
    pd.Series (str)
        Category label for each row.
    """
    infra_markers = (
        r"\b(hospital|clinic|pharmacy|dispensary|health center|medical center|"
        r"medical facility|health facility|treatment center)\b"
    )
    staff_markers = (
        r"\b(doctor|nurse|midwife|surgeon|medic|medical staff|health worker)\b"
    )
    access_markers = r"\b(closed|abandoned|no access|denied access|blocked)\b"
    damage_verbs = (
        r"\b(bomb(ed|s)?|shell(ed|s)?|airstrike|burn(ed|t|ing)?|destroy(ed|ing)?|"
        r"loot(ed|ing)?|raided|damaged|struck|hit by|set fire|explosion)\b"
    )

    attack_terms = r"(?:attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit)"
    health_infra = (
        r"(?:hospital|clinic|health center|doctor|nurse|medic|"
        r"medical(?: facility| team| staff))"
    )
    proximity_pattern = (
        rf"({health_infra}.{{0,45}}{attack_terms})"
        rf"|({attack_terms}.{{0,45}}{health_infra})"
    )
    proximity_mask = notes.str.contains(proximity_pattern, regex=True, na=False)
    direct_action = notes.str.contains(
        r"\b(target(ed|ing)?|fired upon|opened fire on|hit( by)?|"
        r"struck( by)?|raided|occupied|destroyed|burned|attacked|looted|"
        r"damaged|bomb(ed|s)?|shell(ed|s)?|airstrike|assaulted)\b",
        regex=True, na=False,
    )
    pv_hice = proximity_mask & ~direct_action
    infra_damage = notes.str.contains(
        rf"({infra_markers}.{{0,45}}{damage_verbs})"
        rf"|({damage_verbs}.{{0,45}}{infra_markers})",
        regex=True, na=False,
    )
    facility_present = notes.str.contains(infra_markers, regex=True, na=False)
    staff_present = notes.str.contains(staff_markers, regex=True, na=False)
    is_access = (
        notes.str.contains(access_markers, regex=True, na=False)
        | pv_hice
    )
    pers_harm = notes.str.contains(
        r"\b(killed|arrested|shot|abducted|beaten)\b.{0,15}\b"
        r"(doctor|nurse|medic|midwife|staff)\b",
        regex=True, na=False,
    )

    conditions = [
        pers_harm,
        infra_damage & staff_present,
        infra_damage & ~staff_present,
        is_access,
        staff_present & ~facility_present,
    ]
    choices = [
        "personnel_targeting",
        "systemic_attack",
        "infrastructure_damage",
        "access_disruption",
        "personnel_targeting",
    ]

    return np.select(conditions, choices, default="humanitarian_disruption")


def calculate_hice_intensity(
    event_type_series: pd.Series,
) -> pd.Series:
    """
    Rank HICE intensity based on event type labels (high/medium/low).
    """
    high_int = [
        "Air/drone strike", "Shelling/artillery/missile attack",
        "Remote explosive/landmine/IED",
    ]
    med_int = [
        "Attack", "Abduction/forced disappearance", "Arrests",
        "Looting/property destruction",
    ]
    conditions = [
        event_type_series.isin(high_int),
        event_type_series.isin(med_int),
    ]
    return np.select(conditions, ["high", "medium"], default="low")


def extract_health_keyword_counts(text_series: pd.Series) -> pd.DataFrame:
    """Count keyword frequency in a text series (typically HICE-flagged notes)."""
    keywords = [
        "hospital", "clinic", "health center", "medical facility",
        "doctor", "nurse", "medic", "ambulance", "medical supplies",
        "medicine", "patient", "world health organization",
        "unicef", "msf", "icrc",
    ]
    combined_text = " ".join(text_series.fillna("").str.lower())
    counts = []
    for kw in keywords:
        count = len(re.findall(r"\b" + re.escape(kw) + r"(s)?\b", combined_text))
        if count > 0:
            counts.append({"keyword": kw.upper(), "frequency": count})
    result = pd.DataFrame(counts)
    if not result.empty:
        result = result.sort_values("frequency", ascending=False)
    return result
