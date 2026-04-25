import pandas as pd
import numpy as np
import sys
import os

# Import the functions from src/processing.py
sys.path.append(os.getcwd())
from src.processing import extract_health_impacts, classify_hice_type

def analyze_hice():
    # 1. Load data
    df = pd.read_csv('raw_data_output.csv')
    
    # 2. Apply HICE Detection
    df['is_hice'] = extract_health_impacts(df)
    hice_df = df[df['is_hice']].copy()
    
    # 3. Apply Classification
    hice_df['hice_type'] = classify_hice_type(hice_df)
    
    # 4. Generate Summary Statistics
    total_events = len(df)
    detected_hice = len(hice_df)
    
    hice_breakdown = hice_df['hice_type'].value_counts().to_dict()
    
    # 5. Automated Cross-Validation
    # Count how many detected HICE events contain 'Health Workers', 'Patients', 'Medicine', or 'Hospital' 
    # in ACLED's 'assoc_actor_1' or 'assoc_actor_2' columns.
    cross_val_keywords = ['Health Workers', 'Patients', 'Medicine', 'Hospital']
    
    def check_keywords(val):
        if pd.isna(val): return False
        val_str = str(val)
        return any(kw.lower() in val_str.lower() for kw in cross_val_keywords)

    hice_df['cross_val_match'] = hice_df['assoc_actor_1'].apply(check_keywords) | hice_df['assoc_actor_2'].apply(check_keywords)
    cross_val_count = hice_df['cross_val_match'].sum()
    
    # 6. Top 5 Regions
    top_regions = hice_df['admin1'].value_counts().head(5).to_dict()
    
    # 7. Example Notes Snippets
    example_notes = hice_df['notes'].head(5).tolist()
    
    # Output Results
    print(f"--- HICE Detection Analysis Report ---")
    print(f"Total Events: {total_events}")
    print(f"Detected HICE Events: {detected_hice} ({(detected_hice/total_events)*100:.2f}%)")
    print("\nBreakdown of HICE by Type:")
    for t, count in hice_breakdown.items():
        print(f"  - {t}: {count}")
    
    print(f"\nAutomated Cross-Validation:")
    print(f"  - Events matching ACLED Structured Actor Tags: {cross_val_count} ({(cross_val_count/detected_hice)*100:.2f}% of HICE)")
    
    print("\nTop 5 Regions with Highest HICE Counts:")
    for region, count in top_regions.items():
        print(f"  - {region}: {count}")
    
    print("\nExample HICE Note Snippets:")
    for i, note in enumerate(example_notes, 1):
        # Truncate note for brevity
        snippet = (note[:150] + '...') if len(note) > 150 else note
        print(f"  {i}. {snippet}")

if __name__ == "__main__":
    analyze_hice()
