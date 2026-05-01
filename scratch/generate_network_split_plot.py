import matplotlib.pyplot as plt
import os

# Data for Supabase latency split (Estimated based on 13.57s total)
# 65% Network (approx 8.82s), 35% Compute (approx 4.75s)
labels = ['Network Latency\n(Cross-Regional)', 'Query Execution\n(PostgreSQL Engine)']
sizes = [65, 35]
colors = ['#e74c3c', '#f1c40f']
explode = (0.1, 0)  # explode the 1st slice

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(6, 6))

ax.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140, 
        textprops={'fontsize': 12, 'fontweight': 'bold'})

ax.set_title('Supabase Latency Decomposition (Total: 13.57s)', fontsize=14, fontweight='bold', pad=20)

# Save the figure
output_path = '/Users/admin/Github_Project/Myanmar-conflict-observatory/research_tech_comparison/assets/network_split.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Visualization saved to {output_path}")
