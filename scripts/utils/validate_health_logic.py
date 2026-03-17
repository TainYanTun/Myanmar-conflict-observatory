import pandas as pd
import os
import sys
import re

# Add root directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.processing import extract_health_impacts, clean_conflict_data

def validate_health_logic():
    data_path = "data/ACLED Data Feb 14 2026.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return

    print(f"Loading dataset: {data_path}")
    df = pd.read_csv(data_path)
    
    # Apply standard cleaning
    df = clean_conflict_data(df)
    
    print(f"Total events in Myanmar (post-coup): {len(df)}")
    
    # Apply health impact extraction
    health_mask = extract_health_impacts(df)
    health_df = df[health_mask]
    
    health_count = len(health_df)
    health_percentage = (health_count / len(df)) * 100
    
    print(f"Health-related incidents identified: {health_count} ({health_percentage:.2f}%)")
    
    if health_count > 0:
        print("\n--- SAMPLE NARRATIVES (HEALTH IMPACT) ---")
        sample_size = min(10, health_count)
        sample = health_df.sample(sample_size, random_state=42)
        
        for idx, row in sample.iterrows():
            print(f"\n[{row['event_date'].strftime('%Y-%m-%d')}] {row['location']} ({row['admin1']})")
            print(f"Notes: {row['notes'][:300]}...") 
            print("-" * 50)
            
        # Dynamically extract keywords from the function source if possible, or just use a refined list
        # For validation purposes, let's use the list we know is in src/processing.py
        health_keywords = [
            r'\bhospital\b', r'\bclinic\b', r'\bmedical\b', r'\bdoctor\b', r'\bnurse\b', 
            r'\bhealth\b', r'\bambulance\b', r'\bmedicine\b', r'\bpatient\b', r'\bpharmacy\b', 
            r'\bred cross\b', r'\bworld health organization\b', r'\bwho-led\b', r'\bunicef\b', 
            r'\bdisplacement\b', r'\bmalnutrition\b', r'\binjury\b', r'\bwounded\b',
            r'\bhealthcare\b', r'\bsanitation\b', r'\bvaccination\b', r'\bepidemic\b'
        ]
        
        keyword_counts = {}
        notes_lower = health_df['notes'].fillna('').str.lower()
        for kw in health_keywords:
            clean_kw = kw.replace(r'\b', '')
            keyword_counts[clean_kw] = notes_lower.str.contains(kw, regex=True).sum()
            
        print("\n--- KEYWORD HIT COUNTS (REFINED) ---")
        for kw, count in sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True):
            if count > 0:
                print(f"{kw.upper()}: {count}")

    else:
        print("\nNo health-related incidents found.")

if __name__ == "__main__":
    validate_health_logic()
