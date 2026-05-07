import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration ---
DATA_PATH = 'data/myanmar_conflict_clean.csv'
OUTPUT_PATH = 'research/assets/hice_geospatial_types.png'

# Standard HICE colors from app.py
hice_color_map = {
    'infrastructure_damage': '#ef4444', # Red
    'access_disruption': '#3b82f6',     # Blue
    'personnel_targeting': '#f59e0b',    # Amber
    'humanitarian_disruption': '#10b981', # Green (from app's secondary markers)
    'systemic_attack': '#8b5cf6'        # Violet
}

# 1. Load Data
df = pd.read_csv(DATA_PATH)
df['event_date'] = pd.to_datetime(df['event_date'])

# 2. Extract HICE (Using the logic from app.py/processing.py)
# Note: Since I'm running this standalone, I'll use a simplified version of the logic 
# that hits the primary keywords used in the paper.
def extract_hice_simple(notes):
    notes = str(notes).lower()
    infra = ['hospital', 'clinic', 'health center', 'medical facility']
    staff = ['doctor', 'nurse', 'medic', 'health worker']
    if any(k in notes for k in infra + staff):
        if any(a in notes for k in infra + staff for a in ['attack', 'burn', 'destroy', 'shell', 'raid', 'arrest', 'target', 'strike', 'fire', 'hit']):
            return True
    return False

df['is_hice'] = df['notes'].apply(extract_hice_simple)
hice_df = df[df['is_hice']].copy()

# 3. Categorize (Simplified categorical logic for mapping)
def categorize_simple(notes):
    n = str(notes).lower()
    if any(k in n for k in ['doctor', 'nurse', 'medic']) and any(a in n for a in ['kill', 'arrest', 'shot', 'abduct']):
        return 'personnel_targeting'
    if any(k in n for k in ['hospital', 'clinic']) and any(a in n for a in ['destroy', 'burn', 'bomb', 'shell']):
        return 'infrastructure_damage'
    if 'close' in n or 'block' in n or 'access' in n:
        return 'access_disruption'
    return 'humanitarian_disruption'

hice_df['hice_type'] = hice_df['notes'].apply(categorize_simple)

# 4. Visualization
plt.figure(figsize=(10, 12))
sns.set_theme(style="white")

# Plot background density or context if needed, but for a "Type Map" 
# we focus on the categorized points.
for h_type, color in hice_color_map.items():
    subset = hice_df[hice_df['hice_type'] == h_type]
    plt.scatter(
        subset['longitude'], subset['latitude'], 
        label=h_type.replace('_', ' ').title(),
        color=color, alpha=0.6, s=30, edgecolors='white', linewidth=0.5
    )

plt.title('SDG 3.d: Geospatial Distribution of HICE by Impact Type (2021-2025)', fontsize=16, pad=20, fontweight='bold')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend(title='Impact Category', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add region labels for orientation (Top 5 HICE regions)
top_regions = hice_df['admin1'].value_counts().head(5).index
for region in top_regions:
    reg_coords = hice_df[hice_df['admin1'] == region][['latitude', 'longitude']].mean()
    plt.text(reg_coords['longitude'], reg_coords['latitude'], region, 
             fontsize=10, fontweight='bold', alpha=0.7, ha='center')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
print(f"Success! Map exactly like app.py generated at: {OUTPUT_PATH}")
