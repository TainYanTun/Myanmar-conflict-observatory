"""
Signal computation functions for the HICE detection pipeline.

Each function operates on a pd.Series of narrative text (lowercased)
and returns a boolean mask indicating whether the signal is present.
All functions are source-agnostic.
"""

import re
import pandas as pd

PROXIMITY_WINDOW = 45

HEALTH_TERMS = [
    r'\bhospital(s)?\b', r'\bclinic(s)?\b', r'\bhealth center(s)?\b',
    r'\brural health center(s)?\b', r'\brhc\b', r'\bmedical facility\b',
    r'\bhealth facility\b', r'\btreatment center\b', r'\bdoctor(s)?\b',
    r'\bnurse(s)?\b', r'\bhealth worker(s)?\b', r'\bmedic(s)?\b',
    r'\bmedical staff\b', r'\bambulance(s)?\b', r'\bmedical supplies\b',
    r'\bworld health organization\b', r'\bunicef\b', r'\bmsf\b', r'\bicrc\b',
    r'\bmedicine\b.{0,20}\b(shortage|destroyed|looted|burned|seized)\b',
    r'\bpatient(s)?\b.{0,15}\b(injured|treated|killed|arrested|wounded)\b',
]

TARGETING_PATTERN = (
    r'\b(target(ed|ing)?|fired upon|opened fire on|hit by|raided|occupied)\b'
)

ACTION_PHRASES = [
    r'\b(set fire to)\b',
    r'\b(was|were|had been) (destroyed|burned|attacked|looted)\b',
    r'\b(reportedly|allegedly) (attacked|targeted)\b',
    r'\bwas shot\b', r'\bwas arrested\b',
    r'\b(was forced to close|suspended operations|came under fire|'
    r'sustained damage|was struck by|had to evacuate|was displaced|'
    r'forced to flee)\b',
]

ATTACK_TERMS = r'(?:attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit)'
HEALTH_INFRA = (
    r'(?:hospital|clinic|health center|doctor|nurse|medic|'
    r'medical(?: facility| team| staff))'
)

SOFT_HEALTH_PATTERN = (
    r'\b(injured|wounded|killed|dead)\b.{0,20}\b'
    r'(patient|doctor|nurse|medic|staff)\b'
)

ENUMERATION_FP_PATTERN = (
    r'(civilians?|villagers?|residents?).{0,50}(doctor|nurse|medic|patient)'
)
ENUMERATION_FP_NEGATIVE = (
    r'(doctor|nurse|medic|health worker).{0,40}'
    r'(killed|shot|arrested|abducted)'
)

HOSPITAL_BYSTANDER_PATTERN = (
    r'\b(taken|sent|rushed|brought|admitted|transfer|transport|'
    r'arrive|flee|arrive)\b.{0,20}\b(to|at|in|near).{0,15}\b'
    r'(hospital|clinic|facility|dispensary)\b'
)
HOSPITAL_BYSTANDER_NEGATIVE = (
    r'(hospital|clinic|facility).{0,40}'
    r'(attack|bomb|shell|destroy|burn|raid|strike)'
)


def compute_health_mask(notes: pd.Series) -> pd.Series:
    """Flag rows mentioning health infrastructure, personnel, or organisations."""
    return notes.str.contains('|'.join(HEALTH_TERMS), regex=True, na=False)


def compute_targeting_mask(notes: pd.Series) -> pd.Series:
    """Flag rows with explicit targeting language."""
    return notes.str.contains(TARGETING_PATTERN, regex=True, na=False)


def compute_phrase_mask(notes: pd.Series) -> pd.Series:
    """Flag rows with passive-voice action phrases indicating a hostile act."""
    return notes.str.contains('|'.join(ACTION_PHRASES), regex=True, na=False)


def compute_soft_health_mask(notes: pd.Series) -> pd.Series:
    """Flag rows where casualty language appears near health personnel."""
    return notes.str.contains(SOFT_HEALTH_PATTERN, regex=True, na=False)


def compute_proximity_mask(
    notes: pd.Series,
    window: int = PROXIMITY_WINDOW,
) -> pd.Series:
    """
    Bidirectional proximity linking.

    A health-infrastructure term and an attack verb must co-occur within
    *window* characters, evaluated in either order in the narrative text.
    """
    pattern = (
        rf'({HEALTH_INFRA}.{{0,{window}}}{ATTACK_TERMS})'
        rf'|({ATTACK_TERMS}.{{0,{window}}}{HEALTH_INFRA})'
    )
    return notes.str.contains(pattern, regex=True, na=False)


def compute_bystander_mask(notes: pd.Series) -> pd.Series:
    """
    Identify false-positive patterns where health terms appear as background.

    Returns True for rows that should be **excluded** (i.e. they match
    bystander patterns without a genuine attack signal).

    Corresponds to F1-F3 in the paper:
      F1: incidental enumeration (civilian casualty lists and background subjects)
      F2: humanitarian aid language (no hostile act) -- covered indirectly
      F3: spatial-only proximity ("near a hospital" as location)
    """
    enumeration_fp = (
        notes.str.contains(ENUMERATION_FP_PATTERN, regex=True, na=False)
        & ~notes.str.contains(ENUMERATION_FP_NEGATIVE, regex=True, na=False)
    )
    hospital_bystander = (
        notes.str.contains(HOSPITAL_BYSTANDER_PATTERN, regex=True, na=False)
        & ~notes.str.contains(HOSPITAL_BYSTANDER_NEGATIVE, regex=True, na=False)
    )
    return enumeration_fp | hospital_bystander


def compute_event_coupling(
    proximity_mask: pd.Series,
    phrase_mask: pd.Series,
    soft_health_mask: pd.Series,
    targeting_mask: pd.Series,
    bystander_mask: pd.Series,
) -> pd.Series:
    """Events with a genuine health-action link, excluding bystander FPs."""
    return (
        proximity_mask | phrase_mask | soft_health_mask | targeting_mask
    ) & ~bystander_mask
