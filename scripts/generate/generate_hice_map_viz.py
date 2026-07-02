import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_PATH = 'data/myanmar_conflict_clean.csv'
BOUNDARY_PATH = os.path.join(os.path.dirname(__file__), '..', 'research', 'assets', 'myanmar_boundary.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'research', 'assets', 'hice_geospatial_types.png')

COLORS = {
    'infrastructure_damage': '#ef4444',
    'access_disruption': '#3b82f6',
    'personnel_targeting': '#f59e0b',
    'humanitarian_disruption': '#10b981',
    'systemic_attack': '#8b5cf6',
}
LABELS = {
    'infrastructure_damage': 'Infrastructure Damage',
    'access_disruption': 'Access Disruption',
    'personnel_targeting': 'Personnel Targeting',
    'humanitarian_disruption': 'Humanitarian Disruption',
    'systemic_attack': 'Systemic Attack',
}

df = pd.read_csv(DATA_PATH, low_memory=False)
mask = detect_hice_from_source(df, ACLEDAdapter())
notes = df['notes'].fillna('').str.lower()
types = classify_hice_type(notes)
hice_df = df[mask].copy()
hice_df['hice_type'] = types[mask]

fig, ax = plt.subplots(1, 1, figsize=(10, 12))

# Myanmar country outline
with open(BOUNDARY_PATH) as f:
    boundary = json.load(f)
for ring in boundary['coordinates']:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    poly = Polygon(list(zip(xs, ys)), facecolor='#f0f0f0',
                   edgecolor='#c0c0c0', linewidth=1.2, zorder=1)
    ax.add_patch(poly)

# HICE scatter points
for htype in ['infrastructure_damage', 'access_disruption', 'personnel_targeting',
              'humanitarian_disruption', 'systemic_attack']:
    subset = hice_df[hice_df['hice_type'] == htype]
    ax.scatter(subset['longitude'], subset['latitude'],
               label=LABELS[htype], color=COLORS[htype],
               alpha=0.6, s=28, edgecolors='white', linewidth=0.4, zorder=3)

# Top-5 region labels
top5 = hice_df['admin1'].value_counts().head(5).index
for region in top5:
    coords = hice_df[hice_df['admin1'] == region][['latitude', 'longitude']].mean()
    ax.text(coords['longitude'], coords['latitude'], region,
            fontsize=10, fontweight='bold', color='#1d1d1f', alpha=0.85,
            ha='center', va='bottom', zorder=4)

ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.set_title('Geospatial Distribution of HICE by Impact Type (2021\u20132025)', fontsize=14, fontweight='bold')
ax.legend(title='Impact Category', fontsize=9, title_fontsize=10,
          loc='upper left', bbox_to_anchor=(1.02, 1))
ax.tick_params(labelsize=9)
ax.set_xlim(92, 102)
ax.set_ylim(9, 29)
ax.set_facecolor('white')
ax.grid(True, alpha=0.15, color='#999')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=350, bbox_inches='tight', facecolor='white')
print(f'Saved: {OUTPUT_PATH}')

from PIL import Image
img = Image.open(OUTPUT_PATH)
print(f'Image: {img.size[0]}x{img.size[1]} px at 350 DPI')
