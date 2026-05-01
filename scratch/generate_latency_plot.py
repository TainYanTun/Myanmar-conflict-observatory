import matplotlib.pyplot as plt
import numpy as np
import os

# Data from the benchmark
labels = ['Python\n(Pandas)', 'Supabase\n(PostgreSQL)', 'PySpark\n(Simulated)']
latency = [3.1842, 13.5745, 2.5080]

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8, 5))

# Create bar chart
colors = ['#3498db', '#e74c3c', '#2ecc71']
bars = ax.bar(labels, latency, color=colors, width=0.6, edgecolor='black', alpha=0.8)

# Add labels and title
ax.set_ylabel('Execution Latency (Seconds)', fontsize=12, fontweight='bold')
ax.set_title('Computational Latency Comparison (n=80,133)', fontsize=14, fontweight='bold', pad=20)
ax.set_ylim(0, 16)

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
            f'{height:.2f}s', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add a horizontal line for the Spark baseline
ax.axhline(y=2.5080, color='gray', linestyle='--', alpha=0.5, label='Spark Baseline')

# Save the figure
output_path = '/Users/admin/Github_Project/Myanmar-conflict-observatory/research_tech_comparison/assets/latency_comparison.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Visualization saved to {output_path}")
