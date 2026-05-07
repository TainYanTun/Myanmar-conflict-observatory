# HICE Framework: NLP Intelligence & Classification Logic

This document provides a technical overview of how the **Health-Impact-Conflict-Event (HICE)** engine identifies and classifies incidents impacting the healthcare system in Myanmar.

---

## 1. The NLP Intelligence Pipeline
The system uses a multi-stage NLP pipeline to distinguish between direct attacks on health infrastructure and "noise" (incidents where health facilities are mentioned incidentally).

```mermaid
graph TD
    A[Raw Conflict Note] --> B{NLP Feature Extraction}
    
    subgraph "Phase 1: Signal Detection"
    B --> B1[Health Ontology: hospitals, medics, RHC, MSF]
    B --> B2[Action Masking: raided, shelled, burned, arrested]
    B --> B3[Proximity Linking: 'clinic' within 45 chars of 'attack']
    end
    
    B1 & B2 & B3 --> C[Confidence Scoring]
    
    subgraph "Phase 2: The Negative Gate"
    C --> D{Bystander Filter}
    D -- "e.g. 'Taken to hospital'" --> E[FALSE POSITIVE: Discard]
    D -- "e.g. 'Hospital was shelled'" --> F[VALID SIGNAL]
    end
    
    F --> G{Confidence Tier}
    G -- "Score >= 4 OR Strong Proximity" --> H[Tier 1: High Certainty HICE]
    G -- "Health keyword + Violent Event" --> I[Tier 2: Probable HICE]
    
    H & I --> J[is_hice = TRUE]
```

### Key Technical Mechanisms:
*   **Bidirectional Proximity:** The `proximity_pattern` in `src/processing.py` scans for a health term and an attack term within a 45-character window.
*   **The Negative Gate (`fp_mask`):** Specifically filters out narratives where patients are simply "transported" or "admitted" to a hospital following a non-HICE event.
*   **Confidence Scoring:** Boosts the score if multiple indicators (proximity + action phrases + structured actor tags) overlap.

---

## 2. HICE Classification Taxonomy
Once an event is flagged as `is_hice`, it is routed into one of five research categories based on prioritized keyword triggers.

| Category | Priority | Key NLP Trigger | Impact Description |
| :--- | :---: | :--- | :--- |
| **Personnel Targeting** | 1 | `killed`, `arrested` + `doctor`, `nurse`, `medic` | Direct violence or detention of healthcare workers. |
| **Access Disruption** | 2 | `closed`, `blocked` OR `proximity violence` | Barriers to care, forced closures, or danger-based denial of service. |
| **Infrastructure Damage** | 3 | `hospital`, `clinic`, `pharmacy` + `burned`, `shelled` | Physical destruction or looting of medical facilities. |
| **Systemic Attack** | 4 | `Infra Damage` + `Personnel Targeting` | Multi-vector attacks destroying both the facility and its staff. |
| **Humanitarian Disruption** | 5 | `General Health Signal` | Broad disruption to medical supply chains or healthcare delivery. |

---

## 3. Decision Logic Flow
The classification follows a "waterfall" logic to ensure the most severe or specific impact is captured.

```mermaid
graph LR
    Start([Detected HICE]) --> P1{Staff harmed?}
    P1 -- Yes --> C1[Personnel Targeting]
    P1 -- No --> P2{Access blocked or <br/>Proximity violence?}
    P2 -- Yes --> C2[Access Disruption]
    P2 -- No --> P3{Facility damaged?}
    P3 -- Yes --> C3[Infrastructure Damage]
    P3 -- No --> C4[Humanitarian Disruption]
```

---

## 4. Analytical Impact
The resulting `hice_type` and `is_hice` flags are used to calculate the **Vulnerability Score**:
> **Vulnerability Score** = `(0.7 * HICE_Count) + (0.3 * Fatalities)`

This score prioritizes regions where the healthcare infrastructure is being systematically degraded, providing a more nuanced view of conflict impact than fatalities alone.
