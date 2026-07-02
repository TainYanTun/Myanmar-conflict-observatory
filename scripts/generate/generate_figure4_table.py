import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_PATH = 'data/myanmar_conflict_clean.csv'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'research', 'assets', 'figure4_table.png')

df = pd.read_csv(DATA_PATH, low_memory=False)
mask = detect_hice_from_source(df, ACLEDAdapter())
notes = df['notes'].fillna('').str.lower()
types = classify_hice_type(notes)
hice_df = df[mask].copy()
hice_df['hice_type'] = types[mask]

pivot = pd.crosstab(hice_df['admin1'], hice_df['geo_precision'], margins=True, margins_name='All')
for c in [1, 2, 3]:
    if c not in pivot.columns:
        pivot[c] = 0
pivot = pivot[[1, 2, 3, 'All']]
pivot.columns = ['Point', 'Intersection', 'Bounding Box', 'Total']

regions = list(pivot.index[:-1])
totals = list(pivot.iloc[:-1].values)
all_row = list(pivot.iloc[-1].values)

fig, ax = plt.subplots(figsize=(9, 7))
ax.axis('off')

col_labels = ['Region', 'Point', 'Intersection', 'Bounding Box', 'Total']
row_data = []
for i, region in enumerate(regions):
    row_data.append([region, str(int(totals[i][0])), str(int(totals[i][1])), str(int(totals[i][2])), str(int(totals[i][3]))])

cell_text = row_data + [['All', str(int(all_row[0])), str(int(all_row[1])), str(int(all_row[2])), str(int(all_row[3]))]]

table = ax.table(cellText=cell_text, colLabels=col_labels,
                 loc='center', cellLoc='center')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.4)

for key, cell in table.get_celld().items():
    row_idx, col_idx = key
    cell.set_edgecolor('#d1d5db')
    cell.set_linewidth(0.6)
    if row_idx == 0:
        cell.set_text_props(fontweight='bold', color='white', fontsize=10)
        cell.set_facecolor('#1f2937')
    elif row_idx == len(cell_text):
        cell.set_text_props(fontweight='bold', fontsize=10)
        cell.set_facecolor('#f3f4f6')
    elif col_idx == 0:
        cell.set_text_props(ha='left', fontsize=9)
        cell.set_facecolor('#fafafa')
    else:
        cell.set_facecolor('white')

ax.set_title('Figure 4: HICE Incidents by Region and Geospatial Precision',
             fontsize=13, fontweight='bold', pad=16, color='#1f2937')
fig.text(0.5, 0.01, 'geo_precision: Point (exact coordinates), Intersection (admin centroid), Bounding Box (country-level). Myanmar, February 2021 \u2013 February 2025 (n = 463).',
         ha='center', fontsize=8, style='italic', color='#6b7280')

plt.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.08)
plt.savefig(OUTPUT_PATH, dpi=350, facecolor='white')
print(f'Saved: {OUTPUT_PATH}')

from PIL import Image
img = Image.open(OUTPUT_PATH)
print(f'Image: {img.size[0]}x{img.size[1]} px at 350 DPI')
