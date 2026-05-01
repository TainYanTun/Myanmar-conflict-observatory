import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
from src.processing import extract_health_impacts

df = pd.read_csv('raw_data_output.csv')
df['is_hice'] = extract_health_impacts(df)
hice_df = df[df['is_hice']]
print("\n--- HICE Events by Region ---")
print(hice_df['admin1'].value_counts())
print("\n--- Total Fatalities by Region ---")
print(df.groupby('admin1')['fatalities'].sum().sort_values(ascending=False))
