# Plan: Robustness Testing for Vulnerability Score

## Objective
Verify the robustness of the Vulnerability Score configuration (0.7/0.3) as stated in the research paper (`research/main.tex`). The paper claims that varying weights within a ±10% range yields a regional ranking correlation (Spearman’s ρ) of > 0.95.

## Key Files & Context
- **Data Source**: `data/myanmar_conflict_clean.csv` (Preferred) or `raw_data_output.csv` (Fallback).
- **Cleaning Logic**: Standardized in `src/processing.py` via `clean_conflict_data()`.
- **Vulnerability Score Logic**: Formula `(Health_Events * 0.7) + (Fatalities * 0.3)` as implemented in `app.py`.

## Implementation Steps
1. **Create Validation Script**: Create `scripts/test_vulnerability_robustness.py`.
   - Load the cleaned dataset from `data/myanmar_conflict_clean.csv`.
   - If missing, load `raw_data_output.csv` and apply `src.processing.clean_conflict_data()`.
   - Extract Health-Impacting Conflict Events (HICE) using `src.processing.extract_health_impacts()`.
   - Aggregate health events and fatalities by administrative region (`admin1`).
   - Calculate the baseline score (0.7/0.3).
   - Perform Sensitivity Analysis:
     - Shift $W_{health}$ in range $[0.63, 0.77]$ (±10% of 0.7).
     - Keep $W_{total} = 1.0$ (or just use the ratio as per paper).
     - Calculate Spearman's ρ between the baseline ranking and each shifted ranking.
2. **Execute Script**: Run the script.
3. **Report Results**: Output the minimum Spearman's ρ and verify it is > 0.95.

## Verification & Testing
- The script itself is a verification tool.
- Output will display a table of variations and their corresponding Spearman's ρ values.
- Final success/failure message based on the 0.95 threshold.
