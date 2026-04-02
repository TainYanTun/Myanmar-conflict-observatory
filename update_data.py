import os
import requests
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv
from src.processing import clean_conflict_data

load_dotenv()

ACLED_EMAIL = os.getenv('ACLED_EMAIL')
ACLED_PASSWORD = os.getenv('ACLED_PASSWORD')

def get_acled_token():
    auth_url = "https://acleddata.com/oauth/token"
    auth_payload = {
        'username': ACLED_EMAIL,
        'password': ACLED_PASSWORD,
        'grant_type': 'password',
        'client_id': 'acled'
    }
    try:
        res = requests.post(auth_url, data=auth_payload)
        res.raise_for_status()
        return res.json().get('access_token')
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def download_data(token, country="Myanmar"):
    all_data = []
    page = 1
    headers = {'Authorization': f'Bearer {token}'}
    print(f"Starting download for {country}...")
    
    while True:
        params = {
            'country': country,
            'limit': 5000,
            'page': page,
            'event_date': '2021-02-01',
            'event_date_where': '>='
        }
        response = requests.get("https://acleddata.com/api/acled/read", params=params, headers=headers)
        if response.status_code == 200:
            batch = response.json().get('data', [])
            if not batch:
                break
            all_data.extend(batch)
            print(f"Page {page} done (Total: {len(all_data)} rows)")
            page += 1
            time.sleep(0.5)
        else:
            print(f"API Error: {response.status_code}")
            break
    return all_data

def main():
    if not ACLED_EMAIL or not ACLED_PASSWORD:
        print("Error: ACLED credentials not found in .env")
        return

    token = get_acled_token()
    if not token: return

    data = download_data(token)
    if not data:
        print("No data downloaded.")
        return

    # 1. Save Raw Data
    df_raw = pd.DataFrame(data)
    df_raw.to_csv('raw_data_output.csv', index=False)
    print("Raw data saved to raw_data_output.csv")

    # 2. Process Data using standardized logic
    print("Starting processing and cleaning...")
    df_clean = clean_conflict_data(df_raw)

    # 3. Save Final Datasets
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Generic name for the app to find
    df_clean.to_csv("data/myanmar_conflict_clean.csv", index=False)
    
    # Timestamped archive
    archive_name = f"data/myanmar_conflict_clean_{timestamp}.csv"
    df_clean.to_csv(archive_name, index=False)
    
    print("-" * 50)
    print(f"Update Successful!")
    print(f"Clean File: {archive_name}")
    print(f"Total Records: {len(df_clean):,} rows")
    print("-" * 50)

if __name__ == "__main__":
    main()
