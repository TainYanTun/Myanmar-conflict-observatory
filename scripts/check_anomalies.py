
import pandas as pd
import os

def analyze_reporting_anomalies(file_path):
    df = pd.read_csv(file_path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    df['year_month'] = df['event_date'].dt.to_period('M')
    
    # Focus on Sagaing (the most active region)
    sagaing = df[df['admin1'] == 'Sagaing'].copy()
    
    # Events per month in Sagaing
    sagaing_counts = sagaing.groupby('year_month').size()
    
    # Calculate rolling average to find sudden drops
    rolling_avg = sagaing_counts.rolling(window=3).mean()
    anomalies = sagaing_counts[sagaing_counts < (rolling_avg * 0.5)] # Drop by more than 50% from rolling avg
    
    print("\n--- SAGAING REPORTING ANOMALIES (POTENTIAL BLACKOUTS) ---")
    if not anomalies.empty:
        print(anomalies)
    else:
        print("No sudden 50% drops detected in rolling 3-month window.")

    # Compare Sagaing to national trend
    national_counts = df.groupby('year_month').size()
    ratio = sagaing_counts / national_counts
    
    print("\n--- SAGAING-TO-NATIONAL EVENT RATIO (FIRST 5 & LAST 5) ---")
    print(ratio.head(5))
    print("...")
    print(ratio.tail(5))

    return ratio

if __name__ == "__main__":
    data_file = "data/myanmar_conflict_clean.csv"
    if os.path.exists(data_file):
        analyze_reporting_anomalies(data_file)
