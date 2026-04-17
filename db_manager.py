from sqlalchemy import create_engine, text
import pandas as pd
import os
import glob
from datetime import datetime
from dotenv import load_dotenv
from src.processing import clean_conflict_data

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
    df = clean_conflict_data(df)
    
    # 2. Performance Check: Skip if latest data already in DB
    engine = create_engine(DB_URL, connect_args={'options': '-c statement_timeout=30000 -c lock_timeout=10000'})
    try:
        with engine.connect() as conn:
            # Set a shorter lock timeout for the session
            conn.execute(text("SET lock_timeout = '10s'"))
            result = conn.execute(text("SELECT MAX(event_date) FROM conflict_events"))
            db_max_date = result.scalar()
            if db_max_date and pd.to_datetime(db_max_date) >= df['event_date'].max():
                print("Database is already up to date with the latest CSV.")
                return True
    except Exception:
        pass # Table might not exist

    # 3. Robust Ingestion (Upsert Approach)
    print(f"Uploading {len(df)} records to staging...")
    df.to_sql('conflict_events_staging', engine, if_exists='replace', index=False)
    
    with engine.connect() as conn:
        # Ensure target table exists with primary key
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conflict_events (
                event_id_cnty TEXT PRIMARY KEY,
                event_date DATE,
                admin1 TEXT,
                event_type TEXT,
                sub_event_type TEXT,
                actor1 TEXT,
                assoc_actor_1 TEXT,
                inter1 INTEGER,
                actor2 TEXT,
                assoc_actor_2 TEXT,
                inter2 INTEGER,
                interaction INTEGER,
                iso INTEGER,
                region TEXT,
                country TEXT,
                admin2 TEXT,
                admin3 TEXT,
                location TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                geo_precision INTEGER,
                source TEXT,
                source_scale TEXT,
                notes TEXT,
                fatalities INTEGER,
                tags TEXT,
                timestamp TIMESTAMP
            );
        """))
        
        # Upsert: Insert new records or update existing ones based on primary key
        # Dynamically build the column list from the dataframe
        cols = ", ".join(df.columns)
        update_cols = ", ".join([f"{col} = EXCLUDED.{col}" for col in df.columns if col != 'event_id_cnty'])
        
        upsert_query = text(f"""
            INSERT INTO conflict_events ({cols})
            SELECT {cols} FROM conflict_events_staging
            ON CONFLICT (event_id_cnty) 
            DO UPDATE SET {update_cols};
            
            DROP TABLE IF EXISTS conflict_events_staging;
            CREATE INDEX IF NOT EXISTS idx_event_date ON conflict_events (event_date);
            CREATE INDEX IF NOT EXISTS idx_admin1 ON conflict_events (admin1);
        """)
        
        conn.execute(upsert_query)
        conn.commit()
    
    print(f"Ingestion successful. 'conflict_events' updated with upsert logic.")
    return True

if __name__ == "__main__":
    ingest_data()
