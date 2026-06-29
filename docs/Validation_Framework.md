# Validation Framework

Three complementary validation mechanisms that establish the precision and reliability of the HICE detection pipeline.

**Files:** `scripts/validation/run_audit.py`, `run_category_audit.py`, `run_sensitivity.py`, `run_all.py`

## Orchestrator: `run_all.py`

Runs all three validations sequentially and produces a summary:

```
scripts/validation/run_all.py
  ├── run_audit.py          (3-pass AI precision audit)
  ├── run_sensitivity.py    (weight perturbation sensitivity)
  └── run_category_audit.py (per-category validation)

Output: validation/validation_summary.json
```

## 1. AI Precision Audit (`run_audit.py`)

Three independent passes with rule-based rubric evaluation.

**Method:**
- Draw 3 random samples of n=150 each from the HICE pool (seeds: 42, 137, 2025)
- Each sample evaluated against an independent rule-based rubric
- Rubric checks: health entity present AND kinetic act present AND NOT bystander (F1/F2/F3)

**Rubric Logic:**
```python
def rubric_evaluate(note, sub_event_type):
    # 1. Entity check: health term present?
    # 2. Kinetic check: attack verb present OR structural sub_event_type?
    # 3. F2 exclusion: purely humanitarian aid language with no attack?
    # 4. F3 exclusion: spatial-only proximity ("near hospital")?
    # 5. F1 exclusion: incidental health term in casualty list?
    # If all checks pass → TP, otherwise FP with reason
```

**Current Results:**

| Pass | TP | FP | Precision |
|------|----|----|-----------|
| Pass 1 (s=42) | 142 | 8 | 94.7% |
| Pass 2 (s=137) | 145 | 5 | 96.7% |
| Pass 3 (s=2025) | 145 | 5 | 96.7% |
| Combined (n=450) | 432 | 18 | **96.0% (SD 1.2%)** |

**FP breakdown:** F1 (casualty enumeration) = 11 errors, F3 (spatial-only) = 7 errors, F2 = 0 errors.

## 2. Category Validation (`run_category_audit.py`)

Validates the assigned HICE type for every detected event against an independent per-category rubric.

**Rubric per category:**
- **personnel_targeting:** Staff harm keywords near staff terms (bidirectional within 150 chars)
- **access_disruption:** Closure/blockade markers OR proximity violence pattern
- **infrastructure_damage:** Facility term near damage verb (bidirectional within 250 chars)
- **systemic_attack:** Both facility and staff terms present in the narrative
- **humanitarian_disruption:** Always TP (default catch-all)

**Current Results:**

| Category | Total | TP | Precision |
|----------|-------|----|-----------|
| Humanitarian Disruption | 157 | 157 | 100.0% |
| Access Disruption | 137 | 110 | 80.3% |
| Infrastructure Damage | 124 | 116 | 93.5% |
| Personnel Targeting | 38 | 38 | 100.0% |
| Systemic Attack | 7 | 7 | 100.0% |

## 3. Sensitivity Analysis (`run_sensitivity.py`)

Tests the stability of regional vulnerability rankings under weight perturbations.

**Method:**
- Perturb each of the 5 category weights independently by ±10% in 2% steps
- 11 perturbation levels × 5 categories = 55 scenarios
- Spearman's rank correlation (ρ) between baseline and perturbed rankings

**Current Results:**

| Perturbation | Personnel | Systemic | Infra | Access | Human. | Min ρ |
|-------------|-----------|----------|-------|--------|--------|-------|
| -10% | .9975 | 1.0 | 1.0 | .9951 | 1.0 | .9951 |
| -8% to +2% | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| +4% | 1.0 | 1.0 | .9975 | 1.0 | 1.0 | .9975 |
| +6% | 1.0 | 1.0 | .9951 | 1.0 | 1.0 | .9951 |
| +8% | 1.0 | 1.0 | .9951 | 1.0 | 1.0 | .9951 |
| +10% | 1.0 | 1.0 | **.9926** | 1.0 | 1.0 | **.9926** |

**Worst case:** Infrastructure damage at +10% weight increase (ρ = 0.9926).

## Output Files

All validation output is written to `validation/`:

| File | Contents |
|------|----------|
| `validation_summary.json` | Aggregate results from all three validations |
| `hice_ai_audit_results.json` | Per-pass audit metrics and FP breakdown |
| `hice_ai_sample_seed{42,137,2025}.csv` | Per-sample full audit results |
| `hice_category_validation_metrics.json` | Per-category precision metrics |
| `hice_cat_sample_{category}.csv` | Per-category sample for manual review |
| `hice_manual_sample_n30.csv` | 30-event sheet for researcher manual audit |
