from sqlalchemy import create_engine, text
import pandas as pd
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

def get_latest_csv():
    data_dir = "data"
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def ingest_data():
    if not DB_URL:
        print("Error: DB_URL not found in .env file.")
        return False

    csv_path = get_latest_csv()
    if not csv_path:
        print("No CSV files found in data/ for ingestion.")
        return False
    
    print(f"Ingesting data from: {os.path.basename(csv_path)}")
    df = pd.read_csv(csv_path)
    
    # 1. Cleaning and Filtering
    df = df[df['country'] == 'Myanmar']
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df[df['event_date'] >= '2021-02-01']
    
    # 2. Performance Check: Skip if latest data already in DB
    engine = create_engine(DB_URL)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(event_date) FROM conflict_events"))
            db_max_date = result.scalar()
            if db_max_date and pd.to_datetime(db_max_date) >= df['event_date'].max():
                print("Database is already up to date with the latest CSV.")
                return True
    except Exception:
        pass # Table might not exist

    # 3. Robust Ingestion (Staging Approach)
    # Using a staging table ensures the final rename is atomic and indexes/PK are clean
    print(f"Uploading {len(df)} records to staging...")
    df.to_sql('conflict_events_staging', engine, if_exists='replace', index=False)
    
    with engine.connect() as conn:
        # Define Schema (Primary Key and Indexes) on staging table
        conn.execute(text("ALTER TABLE conflict_events_staging ADD PRIMARY KEY (event_id_cnty)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_event_date ON conflict_events_staging (event_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_admin1 ON conflict_events_staging (admin1)"))
        
        # Atomic Swap: Drop old, rename new
        conn.execute(text("DROP TABLE IF EXISTS conflict_events"))
        conn.execute(text("ALTER TABLE conflict_events_staging RENAME TO conflict_events"))
        
        # Standardize Final Indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_event_date ON conflict_events (event_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_admin1 ON conflict_events (admin1)"))
        
        conn.commit()
    
    print(f"Ingestion successful. 'conflict_events' table optimized with Primary Key (event_id_cnty).")
    return True

if __name__ == "__main__":
    ingest_data()
