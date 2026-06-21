# Visualization & Analytical Guide

The **Myanmar Conflict Observatory (MCO)** utilizes high-fidelity visualizations to transform complex ACLED forensic logs into actionable humanitarian intelligence. This guide explains how to interpret each primary analytical component.

---

## 1. Geospatial Dynamics (WebGL Map)
**Visualization:** An animated, multi-layered map showing event density and temporal expansion.
*   **What it represents:** The spatiotemporal "creep" of the conflict. It visualizes how kinetic engagements have moved from ethnic borderlands into the central "Anyar" heartlands (Sagaing, Magway, Mandalay).
*   **Strategic Use:** Identifies new "Hotspots" where conflict is intensifying or shifting, helping responders prepare for emerging IDP (Internally Displaced Persons) crises.

## 2. Regional Risk Matrix (Quadrant Analysis)
**Visualization:** A scatter plot with the X-axis representing **Event Frequency** and the Y-axis representing **Conflict Lethality** (Fatalities).
*   **The Quadrants:**
    *   **High Frequency / High Lethality (Red Zone):** High-intensity conventional warfare zones (e.g., Sagaing).
    *   **High Frequency / Low Lethality:** Areas characterized by frequent but lower-intensity skirmishes or protests (e.g., Yangon).
    *   **Low Frequency / High Lethality:** Potential locations of mass-casualty events or targeted airstrikes.
*   **Strategic Use:** Allows for rapid cross-regional comparisons to prioritize humanitarian aid based on the *nature* of the violence, not just the volume.

## 3. Temporal Conflict Pulse (Time-Series)
**Visualization:** A dynamic line chart with moving averages and event-type filtering.
*   **What it represents:** The "heartbeat" of the conflict. It shows cycles of violence, seasonal trends, and the impact of major political or military offensive shifts.
*   **Strategic Use:** Detects surges in specific warfare modes (e.g., a sudden spike in "Explosions/Remote Violence" may indicate a new aerial campaign).

## 4. Actor Interaction Network (Network Graph)
**Visualization:** A node-and-edge graph mapping engagements between the six primary actor categories.
*   **What it represents:** The "Who vs. Who" of the conflict. 
    *   **Node Size:** Represents the total activity of that actor group.
    *   **Edge Thickness:** Represents the frequency of direct kinetic engagements between two groups.
*   **Strategic Use:** Visualizes the **Hybridization Trend**—how EAOs and Resistance forces are increasingly coordinating their efforts against State Forces.

## 5. HICE Impact Distribution (Sunburst Chart)
**Visualization:** A hierarchical sunburst chart showing the breakdown of Healthcare Interference Conflict Events.
*   **Structure:**
    *   **Inner Ring:** Primary Health Impact (e.g., Infrastructure Damage).
    *   **Outer Ring:** Specific Event Types (e.g., Arson, Airstrike).
*   **Strategic Use:** Quantifies the *mode* of attack on healthcare. For example, if "Airstrikes" are the dominant outer ring for "Infrastructure Damage," it signals a need for anti-shelling protection or mobile clinic strategies.

## 6. Humanitarian Spotlight (Forensic Detail)
**Visualization:** A high-contrast detail card with Actor badges and verified narrative text.
*   **What it represents:** The "Deep Dive." It provides the full, verified forensic notes for a single incident.
*   **Strategic Use:** Used for formal human rights documentation and accountability. The color-coded Actor badges provide instant forensic clarity on who was involved without reading long reports.

---

### Exporting Visualizations
All charts in the MCO are interactive and support **High-Resolution (PNG/SVG)** exports. Researchers are encouraged to use these for reporting and advocacy, provided the ACLED source is appropriately cited as per the [Data Dictionary](data_dictionary.md).
