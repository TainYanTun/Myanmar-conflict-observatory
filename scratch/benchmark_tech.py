import pandas as pd
import numpy as np
import time
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_URL = os.getenv("DB_URL")
CSV_PATH = "raw_data_output.csv"

def benchmark_python(df):
    print("Benchmarking Python (Pandas)...")
    start_time = time.time()
    
    # Task A: Simulated HICE Detection (NLP-like string search)
    hice_keywords = ['hospital', 'clinic', 'medical', 'health', 'doctor', 'nurse']
    action_keywords = ['attack', 'shell', 'bomb', 'burn', 'raid', 'arrest']
    
    pattern_hice = '|'.join(hice_keywords)
    pattern_action = '|'.join(action_keywords)
    
    df_hice = df[df['notes'].str.contains(pattern_hice, case=False, na=False) & 
                 df['notes'].str.contains(pattern_action, case=False, na=False)]
    
    # Task B: Geospatial/Regional Aggregation
    severity = df.groupby('admin1').agg({
        'fatalities': ['mean', 'sum', 'count']
    })
    
    end_time = time.time()
    latency = end_time - start_time
    print(f"Python Latency: {latency:.4f}s")
    return latency

def benchmark_supabase():
    if not DB_URL:
        print("Supabase DB_URL not found in .env")
        return None
    
    print("Benchmarking Supabase (PostgreSQL)...")
    try:
        engine = create_engine(DB_URL)
        
        start_time = time.time()
        
        # Task A: SQL HICE Detection
        sql_hice = text("""
        SELECT COUNT(*) FROM conflict_events 
        WHERE (notes ~* 'hospital|clinic|medical|health|doctor|nurse')
        AND (notes ~* 'attack|shell|bomb|burn|raid|arrest')
        """)
        with engine.connect() as conn:
            conn.execute(sql_hice)
            
        # Task B: SQL Regional Aggregation
        sql_agg = text("""
        SELECT admin1, AVG(fatalities), SUM(fatalities), COUNT(*) 
        FROM conflict_events 
        GROUP BY admin1
        """)
        with engine.connect() as conn:
            conn.execute(sql_agg)
            
        end_time = time.time()
        latency = end_time - start_time
        print(f"Supabase Latency: {latency:.4f}s")
        return latency
    except Exception as e:
        print(f"Supabase Error: {e}")
        return None

def benchmark_spark_simulation(df):
    print("Simulating PySpark (Distributed)...")
    # Simulation: Distributed overhead + parallel execution
    # For small data, Spark is slower due to JVM startup and scheduling
    base_latency = 2.5 # Simulated JVM/Context startup
    processing_time = (len(df) / 1000000) * 0.1 # Parallel processing is fast
    
    latency = base_latency + processing_time
    print(f"Spark (Simulated) Latency: {latency:.4f}s")
    return latency

if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        print(f"CSV file not found: {CSV_PATH}")
    else:
        df = pd.read_csv(CSV_PATH)
        print(f"Dataset size: {len(df)} rows")
        
        results = {}
        results['Python'] = benchmark_python(df)
        results['Supabase'] = benchmark_supabase()
        results['PySpark (Sim)'] = benchmark_spark_simulation(df)
        
        print("\n--- Summary ---")
        for tech, lat in results.items():
            if lat:
                print(f"{tech}: {lat:.4f}s")
