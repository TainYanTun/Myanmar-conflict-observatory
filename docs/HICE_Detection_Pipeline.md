# HICE Detection Pipeline

The core three-layer rule-based NLP pipeline for detecting Healthcare Interference Conflict Events (HICE) from unstructured conflict narrative text.

## Architecture Overview

```
Raw ACLED records (80,000+)
        │
        ▼
┌─────────────────────────────────────┐
│  Layer 1: Structural Gate           │
│  Only kinetic events pass           │
│  (battles, explosions, attacks,     │
│   shelling, airstrikes, arrests,    │
│   abductions, looting)              │
└─────────────────────────────────────┘
        │ (filtered events proceed)
        ▼
┌─────────────────────────────────────┐
│  Layer 2: Keyword Coupling          │
│  4 parallel signals evaluated in    │
│  a 45-character bidirectional       │
│  proximity window:                  │
│  ├─ Proximity (health + attack)     │
│  ├─ Targeting (explicit verbs)      │
│  ├─ Action phrases (passive voice)  │
│  └─ Soft coupling (casualty+staff)  │
└─────────────────────────────────────┘
        │ (any signal = candidate)
        ▼
┌─────────────────────────────────────┐
│  Layer 3: Bystander Disambiguation  │
│  F1: Civilian casualty enumeration  │
│  F2: Humanitarian aid context       │
│  F3: Spatial-only proximity         │
└─────────────────────────────────────┘
        │ (HICE = health + coupling - bystander)
        ▼
   HICE Classification
   (5 impact categories)
```

## Implementation

**File:** `hice_framework/_detector.py`

### `detect_hice(notes, structure_mask)`

The main detection function. Returns a boolean mask where True = HICE event.

```python
def detect_hice(notes, structure_mask):
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
    bystander = compute_bystander_mask(gated_notes)
    result = health & coupling & ~bystander
    mask = pd.Series(False, index=notes.index)
    mask.loc[gated_idx] = result
    return mask
```

### `detect_hice_from_source(df, adapter)`

Convenience function that extracts notes and structure mask via the given adapter, then calls `detect_hice()`.

## Layer Descriptions

### Layer 1: Structural Gate

Only kinetic conflict events pass. Defined per data source via the adapter:
- **ACLED:** `sub_event_type` in `[Attack, Shelling/artillery/missile attack, Air/drone strike, Abduction/forced disappearance, Arrests, Looting/property destruction]` OR `event_type` in `[Violence against civilians, Battles, Explosions/Remote violence]`
- **UCDP GED:** All events pass (all UCDP GED events are kinetic by definition)

### Layer 2: Keyword Coupling

Four parallel signals, any of which suffices for a candidate:

| Signal | Function | What it detects |
|--------|----------|-----------------|
| **Proximity** | `compute_proximity_mask()` | Health term and attack verb within 45 characters, bidirectional |
| **Targeting** | `compute_targeting_mask()` | Explicit targeting verbs (targeted, fired upon, raided, occupied) |
| **Action Phrases** | `compute_phrase_mask()` | Passive-voice hostile actions (was destroyed, came under fire) |
| **Soft Coupling** | `compute_soft_health_mask()` | Casualty language near health personnel (patient killed, nurse wounded) |

### Layer 3: Bystander Disambiguation

Three false-positive filters:

| Filter | Pattern | Negative override |
|--------|---------|-------------------|
| **F1** | Civilian casualty enumeration: `"civilians/villagers/residents + doctor/nurse/medic"` | Direct harm: `"doctor/nurse .{0,40} killed/shot/arrested"` |
| **F2** | Humanitarian aid context (no hostile act) — handled by L1 structural gate | N/A |
| **F3** | Spatial-only proximity: `"taken/sent/rushed/admitted + to/at/in/near + hospital/clinic"` | Direct attack: `"hospital/clinic .{0,40} attack/bomb/shell"` |
