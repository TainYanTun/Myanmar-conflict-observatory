# Analysis Strategy: SDG 3 Focus vs. SDG 16 Integration

This document outlines the strategic decision to maintain a focused research scope centered on **SDG 3 (Health Infrastructure Vulnerability)** rather than integrating **SDG 16 (Peace & Justice)**.

## 1. Current State
*   **Code Implementation:** The `extract_health_impacts` function in `src/processing.py` currently includes a "Layer 2" filter for justice violations (looting, arrests, etc.).
*   **Research Paper (`main.tex`):** The abstract and methodology currently claim an "integrated Conflict-Health Nexus" approach incorporating both SDG 3 and SDG 16.
*   **The Mismatch:** While the code tracks these behavioral indicators (SDG 16), the research findings, case studies, and risk matrices are almost exclusively driven by SDG 3 (health infrastructure) and fatality counts. 

## 2. Recommendation: Stripping SDG 16
To maintain academic rigor and clarity, it is recommended to remove the SDG 16 narrative from both the code and the research paper. A focused, high-precision study on **SDG 3 (Health Infrastructure Vulnerability)** is more defensible and easier to present than a broader study that claims to measure "Justice" but provides no corresponding metric.

### Action Plan
1.  **Refine `src/processing.py`**: Strip the "Layer 2" (SDG 16) extraction logic to focus strictly on healthcare infrastructure.
2.  **Refine `research/main.tex`**: Remove abstract/introduction/methodology claims regarding the "Conflict-Health Nexus" and SDG 16. 
3.  **Refine `notebooks/`**: Remove behavioral/justice event visualisations, focusing entirely on healthcare infrastructure precision and the vulnerability score stability.

## 3. Justification for Focusing on SDG 3
*   **Data Quality:** You have high-fidelity keyword data for medical infrastructure (hospital, clinic, etc.). You have less reliable ground-truth data for systematic "Justice" violations.
*   **Analytical Clarity:** Your "Vulnerability Score" ($0.7$ Health / $0.3$ Fatalities) relies on direct health infrastructure hits. Introducing "Justice" markers muddies the definition of the Vulnerability Score.
*   **Scientific Integrity:** Removing the claim of "SDG 16 integration" avoids the critique that your model lacks metrics for the "Justice/Peace" aspects of the conflict.
