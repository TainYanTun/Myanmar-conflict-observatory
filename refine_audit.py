import pandas as pd
import glob
import os

def get_latest_data():
    data_dir = os.path.join(os.getcwd(), "data")
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not files:
        raise FileNotFoundError("No ACLED CSV found in /data directory.")
    return max(files, key=os.path.getmtime)

try:
    file_path = get_latest_data()
    print(f"Refining Audit for: {os.path.basename(file_path)}")
    df = pd.read_csv(file_path)
    # Check for lethal events
    lethal = df[df['fatalities'] > 50]
    print(f"\n--- Super-Events Detected: {len(lethal)} ---")
    print(lethal[['event_date', 'location', 'fatalities']].head())
except Exception as e:
    print(f"Refinement failed: {e}")
