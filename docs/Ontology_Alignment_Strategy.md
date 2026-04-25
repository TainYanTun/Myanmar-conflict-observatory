# Strategy: Aligning NLP Ontology with Research Methodology

This document outlines the strategic decision to narrow the NLP keyword ontology to strictly reflect "attacks on medical infrastructure" as defined in the research methodology, ensuring absolute consistency between the research paper and the data pipeline.

## 1. The Discrepancy
*   **Research Paper (Methodology):** Defines HICE (Health-Impacting Conflict Events) as incidents involving "attacks on medical infrastructure" (SDG 3.d).
*   **Current Code (`src/processing.py`):** Includes broader outcome-based keywords like `displacement`, `malnutrition`, and `epidemic`.

## 2. The Solution: Precision-Focused Ontology
We are narrowing the keyword list to focus exclusively on **infrastructure and personnel**. This provides high-fidelity, high-precision results that align with the "Verified Floor" protocol described in the research paper.

### Revised Keyword Ontology (Layer 1)
| Category | Keywords |
| :--- | :--- |
| **Facilities** | hospital, clinic, pharmacy |
| **Personnel** | medical, doctor, nurse |
| **Assets** | ambulance, medicine, red cross |
| **Systemic** | healthcare |

## 3. Benefits of this Alignment
*   **Academic Rigor:** Eliminates the ambiguity of broad terms (e.g., "displacement") which are health *consequences* rather than *direct attacks* on infrastructure.
*   **Methodological Transparency:** The logic implemented in the code now exactly matches the methodology described in Section III-D of the research paper.
*   **High Precision:** A focused ontology significantly reduces false-positive rates, supporting the ~89% precision claim.

## 4. Implementation Path
1.  **Code Update:** Modify `src/processing.py` to use only the infrastructure-specific keywords.
2.  **Dashboard Update:** Ensure `app.py` reflects these high-precision results, making the "Health Impact" charts more focused and professional.
3.  **Validation Check:** Update `notebooks/NLP_Extraction_Assessment.ipynb` to visualize only these precise infrastructure hits.
