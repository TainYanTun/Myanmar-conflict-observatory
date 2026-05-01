import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())
from src.processing import extract_health_impacts, classify_hice_type

df = pd.read_csv('raw_data_output.csv')
df['is_hice'] = extract_health_impacts(df)
hice_df = df[df['is_hice']].copy()
hice_df['hice_type'] = classify_hice_type(hice_df)

print("\n--- HICE by Actor 1 ---")
print(hice_df['actor1'].value_counts().head(10))

print("\n--- HICE by Event Type ---")
print(hice_df['event_type'].value_counts())

print("\n--- HICE over Time (Yearly) ---")
hice_df['event_date'] = pd.to_datetime(hice_df['event_date'])
print(hice_df.groupby(hice_df['event_date'].dt.year).size())

# Specific keyword check
keywords = ['ambulance', 'oxygen', 'vaccine', 'clinic', 'hospital', 'medic', 'doctor', 'nurse']
for kw in keywords:
    count = hice_df['notes'].str.contains(kw, case=False).sum()
    print(f"HICE mentions '{kw}': {count}")

print("\n--- HICE with high fatalities (>10) ---")
print(len(hice_df[hice_df['fatalities'] > 10]))
