import pandas as pd

def categorize_actor(actor_name):
    if pd.isna(actor_name): return "Unidentified"
    name = str(actor_name).lower()
    if 'military forces of myanmar' in name or 'police forces of myanmar' in name: return 'State Forces'
    elif 'pdf' in name or "people's defence force" in name or 'local defense force' in name: return 'Resistance'
    elif 'protesters' in name: return 'Protesters'
    elif 'civilians' in name: return 'Civilians'
    elif any(eao in name for eao in ['knu', 'kia', 'tnla', 'mndaa', 'rcss', 'knpp', 'cnp', 'aa ']): return 'EAOs'
    else: return 'Other Groups'

def clean_conflict_data(df):
    """
    Standard cleaning logic for Myanmar conflict data.
    """
    df = df[df['country'] == 'Myanmar']
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df[df['event_date'] >= '2021-02-01']
    return df
