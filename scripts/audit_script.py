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
    print(f"Auditing: {os.path.basename(file_path)}")
    df = pd.read_csv(file_path)
    # Basic consistency check
    nulls = df[['event_date', 'latitude', 'longitude', 'fatalities']].isnull().sum()
    print("\n--- Technical Integrity ---")
    print(nulls)
except Exception as e:
    print(f"Audit failed: {e}")
