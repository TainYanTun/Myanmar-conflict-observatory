"""
HICE Sensitivity Analysis.
Tests rank stability under +/-10% weight perturbations across 5 categories.
Output: Spearman's rho table + worst-case identification.
"""

import os, sys
import pandas as pd, numpy as np
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_PATH = os.path.join(ROOT, "data", "myanmar_conflict_clean.csv")

W_BASE = dict(personnel_targeting=1.0, systemic_attack=0.9,
              infrastructure_damage=0.6, access_disruption=0.5,
              humanitarian_disruption=0.3)
LABELS = dict(personnel_targeting="Personnel", systemic_attack="Systemic",
              infrastructure_damage="Infrastructure", access_disruption="Access",
              humanitarian_disruption="Humanitarian")


def load_data():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    mask = detect_hice_from_source(df, ACLEDAdapter())
    notes = df['notes'].fillna('').str.lower()
    types = classify_hice_type(notes)
    hice_df = df[mask].copy()
    hice_df['hice_type'] = types[mask]
    return hice_df


def compute_rankings(hice_df, weights):
    h = hice_df.copy()
    h['w'] = h['hice_type'].map(weights).fillna(0.3)
    h['impact'] = h['w'] * (1 + np.log1p(h['fatalities'].clip(lower=0)))
    v = h.groupby('admin1').agg(Score=('impact', 'sum')).reset_index()
    v = v.sort_values('Score', ascending=False)
    v['Rank'] = range(1, len(v) + 1)
    return v[['admin1', 'Score', 'Rank']]


def main():
    hice_df = load_data()
    baseline = compute_rankings(hice_df, W_BASE)

    print("\nBaseline regional ranking:")
    print(baseline.to_string(index=False))

    perturbations = [p / 100.0 for p in range(-10, 11, 2)]
    print(f"\n{'Pert (%)':>8s}", end="")
    for p in W_BASE:
        print(f" {LABELS[p]:>14s}", end="")
    print(f" {'Min Rho':>8s}")
    print("-" * 85)

    min_overall, worst_param, worst_pct = 1.0, None, None
    for pct in perturbations:
        print(f"{pct * 100:>+7.1f}% ", end="")
        min_rho = 1.0
        for param in W_BASE:
            w = W_BASE.copy()
            w[param] = W_BASE[param] * (1 + pct)
            result = compute_rankings(hice_df, w)
            m = baseline.merge(result, on='admin1', suffixes=('_b', '_p'))
            rho, _ = spearmanr(m['Rank_b'], m['Rank_p'])
            print(f" {rho:>14.4f}", end="")
            if rho < min_rho:
                min_rho = rho
            if rho < min_overall:
                min_overall = rho
                worst_param, worst_pct = param, pct
        print(f" {min_rho:>8.4f}")

    print(f"\nWorst case: {LABELS[worst_param]} at {worst_pct * 100:+.0f}%")
    print(f"Minimum Spearman's rho = {min_overall:.4f}")

    print("\nCategory distribution:")
    for t, w in W_BASE.items():
        n = (hice_df['hice_type'] == t).sum()
        print(f"  {t:30s}: n={n:3d} ({n / len(hice_df) * 100:.1f}%)  w={w}")


if __name__ == "__main__":
    main()
