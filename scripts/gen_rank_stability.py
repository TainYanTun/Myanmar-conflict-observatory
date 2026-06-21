import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd, numpy as np
from scipy.stats import spearmanr, linregress
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

df = pd.read_csv("data/myanmar_conflict_clean.csv", low_memory=False)
mask = detect_hice_from_source(df, ACLEDAdapter())
notes = df['notes'].fillna('').str.lower()
types = classify_hice_type(notes)
hice_df = df[mask].copy()
hice_df['hice_type'] = types[mask]

W_BASE = dict(personnel_targeting=1.0, systemic_attack=0.9,
              infrastructure_damage=0.6, access_disruption=0.5,
              humanitarian_disruption=0.3)

def compute_rankings(weights):
    h = hice_df.copy()
    h['w'] = h['hice_type'].map(weights).fillna(0.3)
    h['impact'] = h['w'] * (1 + np.log1p(h['fatalities'].clip(lower=0)))
    v = h.groupby('admin1').agg(Score=('impact','sum')).reset_index()
    v = v.sort_values('Score', ascending=False)
    v['Rank'] = range(1, len(v)+1)
    return v[['admin1','Score','Rank']]

baseline = compute_rankings(W_BASE)

# Find worst case
worst_rho, worst_info = 1.0, None
for pct in [p/100.0 for p in range(-10, 11, 2)]:
    for param in W_BASE:
        w = W_BASE.copy(); w[param] = W_BASE[param] * (1 + pct)
        result = compute_rankings(w)
        m = baseline.merge(result, on='admin1', suffixes=('_b','_p'))
        rho, _ = spearmanr(m['Rank_b'], m['Rank_p'])
        if rho < worst_rho:
            worst_rho = rho
            worst_info = (pct, param, rho)

pct, param, rho = worst_info
W_CASE = W_BASE.copy(); W_CASE[param] = W_BASE[param] * (1 + pct)
perturbed = compute_rankings(W_CASE)
merged = baseline.merge(perturbed, on='admin1', suffixes=('_base','_pert'))

fig, ax = plt.subplots(1, 1, figsize=(12, 5))
x, y = merged['Rank_base'], merged['Rank_pert']

slope, intercept, _, _, _ = linregress(x, y)
xx = np.linspace(0.5, 17.5, 100)
ax.plot(xx, slope * xx + intercept, color='#0066cc', linewidth=1.8, linestyle='--')
ax.plot([0, 18], [0, 18], color='#c0c0c0', linewidth=1, zorder=0)

for _, row in merged.iterrows():
    ax.annotate(row['admin1'], (row['Rank_base'], row['Rank_pert']),
                fontsize=10, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points', color='#1d1d1f')
ax.scatter(x, y, s=70, color='#0066cc', edgecolors='white', linewidth=0.8, zorder=5)

label = param.replace('_', ' ')
ax.text(0.3, 16.6, f"Spearman's \u03c1 = {rho:.4f}", fontsize=14,
        fontweight='bold', color='#1d1d1f', va='top')
ax.text(0.3, 15.3, f'{label} weight +10%', fontsize=11, color='#555', va='top')

ax.set_xlabel('Baseline Regional Rank', fontsize=14, fontweight='bold')
ax.set_ylabel('Perturbed Regional Rank', fontsize=14, fontweight='bold')
ax.set_title('Regional Rank Stability (Worst-Case Perturbation)', fontsize=16, fontweight='bold')
ax.set_xlim(0, 18); ax.set_ylim(0, 18)
ax.set_xticks(range(1, 18)); ax.set_yticks(range(1, 18))
ax.tick_params(labelsize=11)
ax.grid(True, alpha=0.2, color='#999')

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "..", "research", "assets", "rank_stability.png")
plt.savefig(out, dpi=400, bbox_inches='tight', facecolor='white')
from PIL import Image
img = Image.open(out)
print(f'Saved: {img.size[0]}x{img.size[1]} px at 400 DPI')
