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

def extract_keywords(text_series, top_n=20):
    """
    Simple keyword extraction for conflict narratives.
    """
    # Common English stopwords + conflict-specific noise
    stopwords = set(['the', 'and', 'a', 'to', 'in', 'of', 'on', 'with', 'for', 'at', 'by', 'from', 'an', 'is', 'was', 'were', 'it', 'as', 'that', 'this', 'reported', 'took', 'place', 'around', 'near', 'village', 'township', 'district', 'region', 'state', 'myanmar', 'burma', 'forces', 'military', 'junta', 'people', 'defence', 'force', 'pdf', 'tatmadaw', 'knu', 'kia', 'pdf', 'ldf', 'eao', 'ia', 'army'])
    
    all_words = ' '.join(text_series.fillna('').str.lower().replace(r'[^a-zA-Z\s]', '', regex=True)).split()
    filtered_words = [word for word in all_words if word not in stopwords and len(word) > 3]
    
    from collections import Counter
    counts = Counter(filtered_words).most_common(top_n)
    return pd.DataFrame(counts, columns=['Keyword', 'Frequency'])

def extract_health_impacts(text_series):
    """
    Identifies incidents specifically impacting healthcare infrastructure and well-being.
    Aligned with SDG 3: Health and Well-being.
    """
    # Use word boundaries \b to avoid matching sub-strings
    health_keywords = [
        r'\bhospital\b', r'\bclinic\b', r'\bmedical\b', r'\bdoctor\b', r'\bnurse\b', 
        r'\bhealth\b', r'\bambulance\b', r'\bmedicine\b', r'\bpatient\b', r'\bpharmacy\b', 
        r'\bred cross\b', r'\bworld health organization\b', r'\bwho-led\b', r'\bunicef\b', 
        r'\bdisplacement\b', r'\bmalnutrition\b', r'\binjury\b', r'\bwounded\b',
        r'\bhealthcare\b', r'\bsanitation\b', r'\bvaccination\b', r'\bepidemic\b',
        r'\bairstrike near hospital\b', r'\bshelling near hospital\b'
    ]
    
    # Create a pattern that handles case insensitivity and word boundaries
    pattern = '|'.join(health_keywords)
    
    # Filter series - Note: we use regex=True to support \b
    health_incidents = text_series.fillna('').str.lower().str.contains(pattern, case=False, regex=True)
    
    # Additional precision: if it matched 'who', ensure it's likely the organization
    # ACLED notes usually capitalize WHO if it's the org, but str.lower() removes that.
    # However, 'who' as a pronoun is extremely common. 
    # Let's check if 'who' is preceded or followed by other medical context if possible, 
    # or just rely on the other 20+ keywords which are more specific.
    
    return health_incidents
