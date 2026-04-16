
import pandas as pd
import re
import os

def analyze_new_patterns(file_path):
    print(f"Analyzing {file_path} for new patterns...")
    df = pd.read_csv(file_path)
    
    # 1. Extract Military Units (LIB, IB, LID)
    # Pattern: LIB followed by numbers, or Infantry Battalion followed by numbers
    unit_pattern = r'\b(LIB|IB|LID|Division|Battalion)\s*(\d+)\b'
    
    def extract_units(text):
        if pd.isna(text): return []
        matches = re.findall(unit_pattern, str(text), re.IGNORECASE)
        return [f"{m[0].upper()} {m[1]}" for m in matches]

    df['military_units'] = df['notes'].apply(extract_units)
    
    # 2. Extract Drone-Specific Groups & Tactics
    drone_keywords = [
        'drone', 'uav', 'shar htoo waw', 'federal wings', 'cloud wings', 
        'kloud', 'fixed-wing', 'octocopter', 'quadcopter', 'drop bomb'
    ]
    drone_pattern = '|'.join(drone_keywords)
    df['is_drone_event'] = df['notes'].fillna('').str.contains(drone_pattern, case=False, regex=True)
    
    # 3. Analyze Urban-Rural Kinetic Flip
    # Assume admin1/admin2/admin3 gives us granularity.
    # We can look at the ratio of 'Protests' vs 'Battles' + 'Explosions' over time per township.
    
    # Summary of Military Units
    all_units = [unit for sublist in df['military_units'] for unit in sublist]
    unit_counts = pd.Series(all_units).value_counts().head(20)
    
    # Summary of Drone Events over time
    df['event_date'] = pd.to_datetime(df['event_date'])
    drone_trend = df[df['is_drone_event']].groupby(df['event_date'].dt.to_period('M')).size()
    
    # Results
    print("\n--- TOP 20 IDENTIFIED MILITARY UNITS IN NOTES ---")
    print(unit_counts)
    
    print("\n--- DRONE TACTICS TREND (FIRST 5 & LAST 5 MONTHS) ---")
    print(drone_trend.head(5))
    print("...")
    print(drone_trend.tail(5))
    
    # Correlation: Drone Events vs Fatalities
    avg_fat_drone = df[df['is_drone_event']]['fatalities'].mean()
    avg_fat_non_drone = df[~df['is_drone_event'] & (df['event_type'].isin(['Battles', 'Explosions/Remote violence']))]['fatalities'].mean()
    
    print(f"\n--- FATALITY IMPACT ANALYSIS ---")
    print(f"Average Fatalities (Drone Events): {avg_fat_drone:.2f}")
    print(f"Average Fatalities (Non-Drone Kinetic Events): {avg_fat_non_drone:.2f}")

    # Return some data for further use if needed
    return df

if __name__ == "__main__":
    # Use the clean file
    data_file = "data/myanmar_conflict_clean.csv"
    if os.path.exists(data_file):
        analyze_new_patterns(data_file)
    else:
        # Fallback to any csv in data/
        import glob
        csvs = glob.glob("data/*.csv")
        if csvs:
            analyze_new_patterns(csvs[0])
