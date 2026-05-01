import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
from src.processing import extract_health_impacts

df = pd.read_csv('raw_data_output.csv')
df['is_hice'] = extract_health_impacts(df)

# Find events with health actors that are NOT detected as HICE
health_actors = ['Health Workers', 'Patients', 'Medicine', 'Hospital']
def has_health_actor(row):
    actors = str(row['assoc_actor_1']) + " " + str(row['assoc_actor_2'])
    return any(kw.lower() in actors.lower() for kw in health_actors)

df['has_health_actor'] = df.apply(has_health_actor, axis=1)
missed_hice = df[df['has_health_actor'] & ~df['is_hice']]

print(f"Total ACLED-tagged health events: {df['has_health_actor'].sum()}")
print(f"HICE detected: {df['is_hice'].sum()}")
print(f"Health-tagged events MISSED by HICE engine: {len(missed_hice)}")

print("\n--- Example Missed HICE (Tagged by ACLED but not detected) ---")
for i, note in enumerate(missed_hice['notes'].head(10), 1):
    print(f"{i}. {note[:200]}...")
