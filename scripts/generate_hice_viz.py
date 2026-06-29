import matplotlib.pyplot as plt
import pandas as pd
import os

# --- Configuration ---
# Validated numbers from Table IV of the research paper
data = {
    'Category': [
        'Infrastructure Damage', 
        'Access Disruption', 
        'Personnel Targeting', 
        'Humanitarian Disruption', 
        'Systemic Attack'
    ],
    'Count': [124, 137, 38, 157, 7],
}

df = pd.DataFrame(data)

# Standard HICE colors from app.py
hice_color_map = {
    'Infrastructure Damage': '#ef4444', # Red
    'Access Disruption': '#3b82f6',     # Blue
    'Personnel Targeting': '#f59e0b',    # Amber
    'Humanitarian Disruption': '#10b981', # Green
    'Systemic Attack': '#8b5cf6'        # Violet
}

# Map colors to categories
df['Color'] = df['Category'].map(hice_color_map)

# Set the style for an academic paper
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12
})

# Create the figure
fig, ax = plt.subplots(figsize=(10, 8))

# Define the donut hole size
wedge_properties = {'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}

# Plot the pie chart
wedges, texts, autotexts = ax.pie(
    df['Count'], 
    labels=df['Category'], 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=df['Color'],
    pctdistance=0.80, 
    wedgeprops=wedge_properties,
    textprops={'fontweight': 'bold'}
)

# Customizing the labels
plt.setp(autotexts, size=11, color="white", weight="bold")
plt.setp(texts, size=12)

# Add a title in the center or above
plt.title('HICE Impact Classification (NLP Engine Extraction)', fontsize=16, pad=20, fontweight='bold')

# Ensure the aspect ratio is circular
ax.axis('equal')  

# Add a central label inside the donut hole
total_hice = df['Count'].sum()
plt.text(0, 0, f'TOTAL HICE\nn = {total_hice}', ha='center', va='center', fontsize=14, fontweight='bold')

# Clean up layout
plt.tight_layout()

# Save the figure in high resolution
output_path = 'research/assets/hice_classification.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight')

print(f"Success! Circular HICE visualization generated at: {output_path}")
