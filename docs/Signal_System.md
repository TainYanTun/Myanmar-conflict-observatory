# Signal System

The signal computation functions that implement the HICE detection pipeline's keyword coupling and bystander disambiguation. All functions operate on `pd.Series` of lowercased narrative text and return boolean masks.

**File:** `hice_framework/_signals.py`

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `PROXIMITY_WINDOW` | `45` | Bidirectional character window for health-attack coupling |

## Health Keywords (`HEALTH_TERMS`)

23 regex patterns covering health infrastructure, personnel, and organisations:

| Category | Terms |
|----------|-------|
| Facilities | `hospital`, `clinic`, `health center`, `rural health center`, `RHC`, `medical facility`, `health facility`, `treatment center` |
| Personnel | `doctor`, `nurse`, `health worker`, `medic`, `medical staff` |
| Transport | `ambulance` |
| Supplies | `medical supplies` |
| Organisations | `World Health Organization`, `UNICEF`, `MSF`, `ICRC` |
| Compound | `medicine .{0,20} shortage/destroyed/looted/burned/seized` |
| Compound | `patient .{0,15} injured/treated/killed/arrested/wounded` |

## Targeting Pattern (`TARGETING_PATTERN`)

Single regex for explicit targeting verbs:

```
\b(target(ed|ing)?|fired upon|opened fire on|hit by|raided|occupied)\b
```

## Action Phrases (`ACTION_PHRASES`)

List of ~10 passive-voice patterns:

| Pattern | Example |
|---------|---------|
| `set fire to` | "set fire to the clinic" |
| `was/were destroyed/burned/attacked/looted` | "hospital was destroyed" |
| `reportedly/allegedly attacked/targeted` | "reportedly attacked" |
| `was shot` / `was arrested` | "doctor was shot" |
| `was forced to close` | "clinic was forced to close" |
| `suspended operations` | "health center suspended operations" |
| `came under fire` | "ambulance came under fire" |
| `sustained damage` | "facility sustained damage" |
| `was struck by` | "hospital was struck by" |
| `had to evacuate` / `was displaced` / `forced to flee` | "medical staff had to evacuate" |

## Attack Terms (`ATTACK_TERMS`)

For proximity coupling:

```
attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit
```

## Health Infrastructure (`HEALTH_INFRA`)

For proximity coupling:

```
hospital|clinic|health center|doctor|nurse|medic|medical(?: facility| team| staff)
```

## Soft Health Pattern (`SOFT_HEALTH_PATTERN`)

Couples casualty language with health personnel:

```
\b(injured|wounded|killed|dead)\b.{0,20}\b(patient|doctor|nurse|medic|staff)\b
```

## Bystander Filters

### F1: Enumeration False Positive

Detects health terms in civilian casualty lists without direct targeting:

```python
ENUMERATION_FP_PATTERN = r'(civilians?|villagers?|residents?).{0,50}(doctor|nurse|medic|patient)'
ENUMERATION_FP_NEGATIVE = r'(doctor|nurse|medic|health worker).{0,40}(killed|shot|arrested|abducted)'
```

A row is a bystander if the FP pattern matches AND the negative does NOT match.

### F3: Spatial-Only Proximity

Detects hospital mentioned as a location, not a target:

```python
HOSPITAL_BYSTANDER_PATTERN = r'\b(taken|sent|rushed|brought|admitted|transfer|transport|arrive|flee)\b.{0,20}\b(to|at|in|near).{0,15}\b(hospital|clinic|facility|dispensary)\b'
HOSPITAL_BYSTANDER_NEGATIVE = r'(hospital|clinic|facility).{0,40}(attack|bomb|shell|destroy|burn|raid|strike)'
```

A row is a bystander if the transport pattern matches AND no attack verb appears near the facility.

## Signal Functions

| Function | Returns | Logic |
|----------|---------|-------|
| `compute_health_mask(notes)` | True if any HEALTH_TERMS regex matches | `notes.str.contains('|'.join(HEALTH_TERMS))` |
| `compute_targeting_mask(notes)` | True if TARGETING_PATTERN matches | `notes.str.contains(TARGETING_PATTERN)` |
| `compute_phrase_mask(notes)` | True if any ACTION_PHRASES regex matches | `notes.str.contains('|'.join(ACTION_PHRASES))` |
| `compute_soft_health_mask(notes)` | True if SOFT_HEALTH_PATTERN matches | `notes.str.contains(SOFT_HEALTH_PATTERN)` |
| `compute_proximity_mask(notes, window=45)` | True if health and attack terms co-occur within window in either direction | Bidirectional regex with `{0,window}` |
| `compute_bystander_mask(notes)` | True if F1 or F3 pattern matches without override | `enumeration_fp | hospital_bystander` |
| `compute_event_coupling(...)` | True if any signal present AND not bystander | `(prox\|phrase\|soft\|target) & ~bystander` |
