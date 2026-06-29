# HICE Classification System

Classifies detected HICE events into five thematic impact categories with a priority-ordered rule hierarchy.

**File:** `hice_framework/_detector.py`, function `classify_hice_type(notes)`

## Category Priority

Categories are evaluated in priority order using `np.select()`. The first matching condition wins:

| Priority | Category | Weight | Condition |
|----------|----------|--------|-----------|
| 1 | **personnel_targeting** | 1.0 | Staff harm keywords within 15 characters of staff terms |
| 2 | **systemic_attack** | 0.9 | Infrastructure damage + staff present in text |
| 3 | **infrastructure_damage** | 0.6 | Infrastructure damage without staff reference |
| 4 | **access_disruption** | 0.5 | Closure/blockade markers OR proximity violence without direct action |
| 5 | **humanitarian_disruption** | 0.3 | Default catch-all for staff present without facility |

## Detection Logic

### Infrastructure markers
```
\b(hospital|clinic|pharmacy|dispensary|health center|medical center|medical facility|health facility|treatment center)\b
```

### Staff markers
```
\b(doctor|nurse|midwife|surgeon|medic|medical staff|health worker)\b
```

### Access markers
```
\b(closed|abandoned|no access|denied access|blocked)\b
```

### Damage verbs
```
\b(bomb(ed|s)?|shell(ed|s)?|airstrike|burn(ed|t|ing)?|destroy(ed|ing)?|loot(ed|ing)?|raided|damaged|struck|hit by|set fire|explosion)\b
```

### Proximity violence detection

Events where a health term and attack verb co-occur within 45 characters, but WITHOUT explicit direct action verbs:

```python
proximity_mask = bidirectional 45-char coupling
direct_action = explicit verbs (targeted, fired upon, raided, occupied, destroyed, etc.)
pv_hice = proximity_mask & ~direct_action
```

This captures events where fighting near a health facility caused disruption, even if the facility wasn't the explicit target.

### Personnel harm detection

```
\b(killed|arrested|shot|abducted|beaten)\b.{0,15}\b(doctor|nurse|medic|midwife|staff)\b
```

## Classification Conditions

```python
conditions = [
    pers_harm,                              # 1. personnel_targeting
    infra_damage & staff_present,           # 2. systemic_attack
    infra_damage & ~staff_present,          # 3. infrastructure_damage
    is_access,                              # 4. access_disruption
    staff_present & ~facility_present,      # 5. humanitarian_disruption
]
choices = [
    "personnel_targeting",
    "systemic_attack",
    "infrastructure_damage",
    "access_disruption",
    "humanitarian_disruption",
]
```

## Category Descriptions

| Category | Description | Example narrative |
|----------|-------------|-------------------|
| **Personnel Targeting** | Medical personnel directly harmed | "Military arrested the doctor and two nurses" |
| **Systemic Attack** | Facility damaged while staff present | "Clinic was bombed while health workers were treating patients" |
| **Infrastructure Damage** | Physical damage to health facility | "Airstrike destroyed the rural health center" |
| **Access Disruption** | Facilities closed or blocked | "Military blocked access to the hospital" |
| **Humanitarian Disruption** | Catch-all; supply chain or logistics disruption | "MSF suspended operations due to security concerns" |

## Validation Results (current)

| Category | Count | Precision |
|----------|-------|-----------|
| Humanitarian Disruption | 157 | 100.0% |
| Access Disruption | 137 | 80.3% |
| Infrastructure Damage | 124 | 93.5% |
| Personnel Targeting | 38 | 100.0% |
| Systemic Attack | 7 | 100.0% |
| **Total** | **463** | **96.0%** |
