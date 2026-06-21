"""
Source-agnostic HICE (Healthcare Interference Conflict Events) Detection Framework.

=============================================================================
ARCHITECTURE (3 layers, matches paper Section III.C)
=============================================================================
Layer 1 - Structural Gate (via adapter: only kinetic events proceed)
Layer 2 - Bidirectional Action-Keyword Coupling (4 parallel signals:
          proximity, targeting, action phrases, soft health coupling)
Layer 3 - Bystander Disambiguation (negative gate, F1/F3/F4 patterns)

=============================================================================
OUTPUT
=============================================================================
detect_hice_from_source() returns a boolean pd.Series mask where True
indicates a verified Healthcare Interference Conflict Event (HICE).

=============================================================================
HOW TO USE WITH A DIFFERENT DATA SOURCE
=============================================================================
1. Implement the SourceAdapter ABC with two methods:
   - get_notes(df)          -- return a Series of free-text narratives
   - get_structure_mask(df) -- return a boolean Series: True for kinetic
                               events (battles, explosions, attacks, etc.)
   - Optional: get_event_type_col(df) for calculate_hice_intensity()

2. Call detect_hice_from_source(df, adapter).

   Example::

       from hice_detector import ACLEDAdapter, detect_hice_from_source

       mask = detect_hice_from_source(df, ACLEDAdapter())
       df_hice = df[mask]

   Example with a custom source::

       from hice_detector import SourceAdapter, detect_hice_from_source

       class MyAdapter(SourceAdapter):
           def get_notes(self, df):
               return df["narrative"]
           def get_structure_mask(self, df):
               return df["event_type"].isin(["battle", "explosion", "attack"])

       hice_mask = detect_hice_from_source(my_df, MyAdapter())
"""

import re
import warnings
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from collections import Counter

warnings.filterwarnings('ignore', message='This pattern is interpreted as a regular expression')

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  HEALTH ONTOLOGY                                                      ║
# ╚═════════════════════════════════════════════════════════════════════════╝

HEALTH_TERMS = [
    r'\bhospital(s)?\b', r'\bclinic(s)?\b', r'\bhealth center(s)?\b',
    r'\brural health center(s)?\b', r'\brhc\b', r'\bmedical facility\b',
    r'\bhealth facility\b', r'\btreatment center\b', r'\bdoctor(s)?\b',
    r'\bnurse(s)?\b', r'\bhealth worker(s)?\b', r'\bmedic(s)?\b',
    r'\bmedical staff\b', r'\bambulance(s)?\b', r'\bmedical supplies\b',
    r'\bworld health organization\b', r'\bunicef\b', r'\bmsf\b', r'\bicrc\b',
    r'\bmedicine\b.{0,20}\b(shortage|destroyed|looted|burned|seized)\b',
    r'\bpatient(s)?\b.{0,15}\b(injured|treated|killed|arrested|wounded)\b'
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
    r'forced to flee)\b'
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

PROXIMITY_WINDOW = 45

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  L2: SIGNAL COMPUTATION                                               ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def compute_health_mask(notes: pd.Series) -> pd.Series:
    return notes.str.contains('|'.join(HEALTH_TERMS), regex=True, na=False)

def compute_targeting_mask(notes: pd.Series) -> pd.Series:
    return notes.str.contains(TARGETING_PATTERN, regex=True, na=False)

def compute_phrase_mask(notes: pd.Series) -> pd.Series:
    return notes.str.contains('|'.join(ACTION_PHRASES), regex=True, na=False)

def compute_soft_health_mask(notes: pd.Series) -> pd.Series:
    return notes.str.contains(SOFT_HEALTH_PATTERN, regex=True, na=False)

def compute_proximity_mask(notes: pd.Series, window: int = PROXIMITY_WINDOW) -> pd.Series:
    pattern = (
        rf'({HEALTH_INFRA}.{{0,{window}}}{ATTACK_TERMS})'
        rf'|({ATTACK_TERMS}.{{0,{window}}}{HEALTH_INFRA})'
    )
    return notes.str.contains(pattern, regex=True, na=False)

def compute_bystander_mask(notes: pd.Series) -> pd.Series:
    enumeration_fp = (
        notes.str.contains(ENUMERATION_FP_PATTERN, regex=True, na=False)
        & ~notes.str.contains(ENUMERATION_FP_NEGATIVE, regex=True, na=False)
    )
    hospital_bystander = (
        notes.str.contains(HOSPITAL_BYSTANDER_PATTERN, regex=True, na=False)
        & ~notes.str.contains(HOSPITAL_BYSTANDER_NEGATIVE, regex=True, na=False)
    )
    return enumeration_fp | hospital_bystander

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  ADAPTER INTERFACE                                                    ║
# ╚═════════════════════════════════════════════════════════════════════════╝

class SourceAdapter(ABC):
    @abstractmethod
    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        """Return the free-text narrative column (lowercased)."""

    @abstractmethod
    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        """Return a boolean mask: True for kinetic events."""

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError("get_event_type_col() not implemented.")

class ACLEDAdapter(SourceAdapter):
    ATTACK_SUB_TYPES = [
        'Attack', 'Shelling/artillery/missile attack', 'Air/drone strike',
        'Abduction/forced disappearance', 'Arrests', 'Looting/property destruction'
    ]
    VIOLENT_EVENT_TYPES = [
        'Violence against civilians', 'Battles', 'Explosions/Remote violence'
    ]

    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        return df['notes'].fillna('').str.lower()

    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        return (
            df['sub_event_type'].isin(self.ATTACK_SUB_TYPES)
            | df['event_type'].isin(self.VIOLENT_EVENT_TYPES)
        )

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        return df['sub_event_type']

class UCDPGEDAdapter(SourceAdapter):
    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        return df['source_article'].fillna('').str.lower()

    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(True, index=df.index)

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        return df['type_of_violence'].map({1: 'state-based', 2: 'non-state', 3: 'one-sided'})

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  DETECTION PIPELINE                                                   ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def detect_hice(
    notes: pd.Series,
    structure_mask: pd.Series,
) -> pd.Series:
    """
    Run the 3-layer detection pipeline.

    L1: only kinetic events proceed (structure_mask gate)
    L2: 4 parallel NLP signals (proximity, targeting, phrase, soft health)
    L3: bystander disambiguation (F1/F3/F4 exclusion)
    """
    passed = structure_mask.astype(bool)
    gated_idx = notes.index[passed]

    gated_notes = notes.loc[gated_idx]
    health = compute_health_mask(gated_notes)
    targeting = compute_targeting_mask(gated_notes)
    phrase = compute_phrase_mask(gated_notes)
    soft = compute_soft_health_mask(gated_notes)
    proximity = compute_proximity_mask(gated_notes)
    coupling = proximity | phrase | targeting | soft

    bystander = compute_bystander_mask(gated_notes)
    result = health & coupling & ~bystander
    mask = pd.Series(False, index=notes.index)
    mask.loc[gated_idx] = result
    return mask

def detect_hice_from_source(
    df: pd.DataFrame,
    adapter: SourceAdapter,
) -> pd.Series:
    """Run the full HICE detection pipeline on a DataFrame via the given adapter."""
    notes = adapter.get_notes(df)
    structure_mask = adapter.get_structure_mask(df)
    return detect_hice(notes, structure_mask)

# ╔═════════════════════════════════════════════════════════════════════════╗
# ║  CLASSIFICATION & POST-PROCESSING                                     ║
# ╚═════════════════════════════════════════════════════════════════════════╝

def classify_hice_type(notes: pd.Series) -> pd.Series:
    """Classify HICE into thematic categories (priority order)."""
    infra_markers = (
        r'\b(hospital|clinic|pharmacy|dispensary|health center|medical center|'
        r'medical facility|health facility|treatment center)\b'
    )
    staff_markers = (
        r'\b(doctor|nurse|midwife|surgeon|medic|medical staff|health worker)\b'
    )
    access_markers = r'\b(closed|abandoned|no access|denied access|blocked)\b'

    attack_terms = r'(?:attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit)'
    health_infra = (
        r'(?:hospital|clinic|health center|doctor|nurse|medic|'
        r'medical(?: facility| team| staff))'
    )
    proximity_pattern = (
        rf'({health_infra}.{{0,45}}{attack_terms})'
        rf'|({attack_terms}.{{0,45}}{health_infra})'
    )
    proximity_mask = notes.str.contains(proximity_pattern, regex=True, na=False)
    direct_action = notes.str.contains(
        r'\b(target(ed|ing)?|fired upon|opened fire on|hit( by)?|'
        r'struck( by)?|raided|occupied|destroyed|burned|attacked|looted|'
        r'damaged|bomb(ed|s)?|shell(ed|s)?|airstrike|assaulted)\b',
        regex=True, na=False
    )
    pv_hice = proximity_mask & ~direct_action

    damage_verbs = (
        r'\b(bomb(ed|s)?|shell(ed|s)?|airstrike|burn(ed|t|ing)?|destroy(ed|ing)?|'
        r'loot(ed|ing)?|raided|damaged|struck|hit by|set fire|explosion)\b'
    )

    infra_damage = notes.str.contains(
        rf'({infra_markers}.{{0,45}}{damage_verbs})'
        rf'|({damage_verbs}.{{0,45}}{infra_markers})',
        regex=True, na=False,
    )
    facility_present = notes.str.contains(infra_markers, regex=True, na=False)
    staff_present = notes.str.contains(staff_markers, regex=True, na=False)
    is_access = (
        notes.str.contains(access_markers, regex=True, na=False) | pv_hice
    )
    pers_harm = notes.str.contains(
        r'\b(killed|arrested|shot|abducted|beaten)\b.{0,15}\b'
        r'(doctor|nurse|medic|midwife|staff)\b',
        regex=True, na=False
    )

    conditions = [
        pers_harm,
        infra_damage & staff_present,
        infra_damage & ~staff_present,
        is_access,
        staff_present & ~facility_present,
    ]
    choices = [
        'personnel_targeting', 'systemic_attack',
        'infrastructure_damage', 'access_disruption', 'personnel_targeting',
    ]
    return np.select(conditions, choices, default='humanitarian_disruption')

def calculate_hice_intensity(event_type_series: pd.Series) -> pd.Series:
    high_int = [
        'Air/drone strike', 'Shelling/artillery/missile attack',
        'Remote explosive/landmine/IED'
    ]
    med_int = [
        'Attack', 'Abduction/forced disappearance', 'Arrests',
        'Looting/property destruction'
    ]
    conditions = [event_type_series.isin(high_int), event_type_series.isin(med_int)]
    return np.select(conditions, ['high', 'medium'], default='low')

def extract_health_keyword_counts(text_series: pd.Series) -> pd.DataFrame:
    keywords = [
        'hospital', 'clinic', 'health center', 'medical facility',
        'doctor', 'nurse', 'medic', 'ambulance', 'medical supplies',
        'medicine', 'patient', 'world health organization',
        'unicef', 'msf', 'icrc'
    ]
    combined_text = ' '.join(text_series.fillna('').str.lower())
    counts = []
    for kw in keywords:
        count = len(re.findall(r'\b' + re.escape(kw) + r'(s)?\b', combined_text))
        if count > 0:
            counts.append({'Keyword': kw.upper(), 'Frequency': count})
    result = pd.DataFrame(counts)
    return result.sort_values('Frequency', ascending=False) if not result.empty else result
