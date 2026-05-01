import pandas as pd
import re

df = pd.read_csv('data/myanmar_conflict_clean_2026-04-24.csv', low_memory=False)
notes = df['notes'].fillna('').str.lower()

terms = [
    r'maternity', r'surgical', r'emergency ward', r'oxygen', r'icu', 
    r'operating theater', r'medical supplies', r'vaccination', 
    r'blood bank', r'midwife', r'pharmacy', r'dispensary', r'clinic'
]

for t in terms:
    count = notes.str.contains(t, regex=True).sum()
    print(f"{t}: {count}")
