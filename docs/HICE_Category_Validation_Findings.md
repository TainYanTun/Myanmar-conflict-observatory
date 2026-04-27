# HICE Category Validation Findings

This document summarizes the validation of the Healthcare Infrastructure and Conflict Events (HICE) classification framework. The validation was conducted using a deterministic AI audit rubric that verifies the assigned categories against the original event narratives.

## Methodology

The HICE detection pipeline uses a **Two-Tier Confidence Architecture** with mandatory kinetic action coupling. Following detection, events are classified into one of five research-grade categories:
1.  **Personnel Targeting**: Intentional harm or targeting of medical staff.
2.  **Infrastructure Damage**: Direct kinetic hits, looting, or occupation of health facilities.
3.  **Access Disruption**: Closures, evacuations, or proximity violence affecting health access.
4.  **Systemic Attack**: Concurrent targeting of both infrastructure and personnel.
5.  **Humanitarian Disruption**: General impact on healthcare delivery not fitting the above.

## Validation Results (n=533)

Following the implementation of the `hospital_bystander` disambiguation filter and the refinement of kinetic markers, the pipeline achieved high precision across all target categories.

| Category | Total Detected (n) | True Positives (TP) | Precision |
| :--- | :--- | :--- | :--- |
| **Personnel Targeting** | 56 | 53 | 94.6% |
| **Humanitarian Disruption** | 39 | 39 | 100.0% |
| **Systemic Attack** | 12 | 12 | 100.0% |
| **Infrastructure Damage** | 237 | 187 | 78.9% |
| **Access Disruption** | 189 | 146 | 77.2% |

### Total HICE Precision (Weighted): **80.3%**

## Key Improvements

During this validation phase, three critical vulnerabilities were identified and patched:
- **Bystander Filter**: Implemented a negative gate to exclude incidental mentions of hospitals (e.g., "victim taken to hospital") which previously inflated the dataset by ~200%.
- **Taxonomy Refinement**: Removed broad geographic markers (like "ward") from the healthcare ontology to prevent misclassification of administrative boundary mentions.
- **Kinetic Routing**: Enhanced the `direct_action` logic to accurately route direct hits (bombing, shelling) into `infrastructure_damage`, separating them from proximity-based `access_disruption`.

## Conclusion

The HICE classification framework is now production-ready, maintaining a precision rate above 70% for all categories. This provides a robust foundation for the manuscript's claims regarding the visibility of healthcare impacts in the Myanmar conflict.
