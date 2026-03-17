import pandas as pd

def categorize_actor(actor_name):
    if pd.isna(actor_name): return "Unidentified"
    name = str(actor_name).lower()
    
    # 1. State Forces & Pro-Junta Militias
    if any(x in name for x in ['military forces of myanmar', 'police forces of myanmar', 'state administration council', 'border guard force', 'people\'s militia force']):
        return 'State Forces'
    elif any(x in name for x in ['pyu saw htee', 'thway thauk', 'blood comrades', 'swan arr shin', 'pro-military']):
        return 'Pro-Junta Militia'
    
    # 2. Resistance (PDF/LDF/Guerrilla/Other Anti-Coup)
    resistance_keywords = [
        'pdf', 'people\'s defense force', 'local defense force', 'kndf', 'karenni nationalities defense force', 
        'chinland defense force', 'cdf', 'unidentified anti-coup armed group', 'guerrilla', 'ogre', 'revolution',
        'defense force', 'resistance', 'pafd', 'yaw defense force', 'ydf', 'dragon army', 'mrda', 'chindwin attack force',
        'myingyan black tiger', 'mbt', 'black eagle', 'underground warriors', 'young force', 'ug-force', 'guerrilla force',
        'defense team', 'ddt', 'special task force', 'sstf', 'attack force', 'generation z', 'gen z', 
        'drone strike', 'mdds', 'dark shadow', 'leopard army', 'blpa', 'chindwin brothers', 'taung nyo', 'eagle force', 
        'brave heart', 'danger force', 'red bandana', 'phoenix sgg', 'freeland attack', 'fla', 'support organization',
        'commando', 'special force', 'vanguard', 'victory force', 'justice force', 'strike force', 'task force',
        'people\'s army', 'liberation army', 'bha', 'tpf', 'kpaf', 'mmu', 'kso', 'sgg', 'baf', 'column', 'urban', 'cgm',
        'technical team', 'shar htoo waw', 'king cobra', 'defence force', 'defence team', 'militia', 'security force', 
        'black k', 'thu rain', 'freedom force', 'pdaf', 'galon force', 'federal army', 'tiger force', 'ranger group', 'truth army',
        'anonymous', 'oak awe', 'snake eyes'
    ]
    if any(x in name for x in resistance_keywords):
        return 'Resistance'
    
    # 3. EAOs (Ethnic Armed Organizations)
    eao_keywords = [
        'knu', 'knla', 'kndo', 'kia', 'kio', 'tnla', 'pslf', 'mndaa', 'mntjp', 'aa ', 'ula', 'rcss', 'ssa', 'knpp', 'ka ', 
        'cnp', 'sspp', 'pnlo', 'sna', 'cnf', 'cna', 'pno', 'pna', 'brotherhood alliance', 'northern alliance', 
        'three brotherhood', 'absdf', 'knlp', 'kpc', 'dkba', 'mnda', 'alp', 'ala', 'nssaa', 'shanni', 'kachin', 'karen', 'shan state', 'arakan',
        'mon state', 'nmsp', 'nmla', 'chin brotherhood', 'rohingya', 'arsa', 'kaw thoo lei', 'pa-oh', 'ta\'ang', 'palaung', 'kokang', 'wa state', 'uwsa',
        'mon national', 'naga', 'nscn', 'ktla'
    ]
    if any(x in name for x in eao_keywords):
        return 'EAOs'
    
    # 4. Civilians & Protesters
    if 'protesters' in name:
        return 'Protesters'
    elif 'rioters' in name:
        return 'Rioters'
    elif 'civilians' in name:
        return 'Civilians'
    
    # 5. Unidentified / Others
    if 'unidentified' in name:
        return 'Unidentified'
    else:
        return 'Other Groups'

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

def extract_health_impacts(df):
    """
    Identifies incidents impacting healthcare infrastructure AND broader human well-being.
    Aligned with SDG 3: Health and Well-being.
    """
    text_series = df['notes'].fillna('').str.lower()
    event_series = df['sub_event_type'].fillna('').str.lower()
    
    # 1. Direct Healthcare Infrastructure/Staff Keywords
    health_keywords = [
        r'\bhospital\b', r'\bclinic\b', r'\bmedical\b', r'\bdoctor\b', r'\bnurse\b', 
        r'\bhealth\b', r'\bambulance\b', r'\bmedicine\b', r'\bpatient\b', r'\bpharmacy\b', 
        r'\bred cross\b', r'\bworld health organization\b', r'\bwho-led\b', r'\bunicef\b', 
        r'\bdisplacement\b', r'\bmalnutrition\b', r'\binjury\b', r'\bwounded\b',
        r'\bhealthcare\b', r'\bsanitation\b', r'\bvaccination\b', r'\bepidemic\b',
        r'\bairstrike near hospital\b', r'\bshelling near hospital\b'
    ]
    pattern = '|'.join(health_keywords)
    health_hits = text_series.str.contains(pattern, case=False, regex=True)
    
    # 2. Broader Well-being & Human Rights (SDG 3.3, 3.4, 3.8)
    # We include sub-event types that represent systemic threats to well-being
    wellbeing_events = ['sexual violence', 'arrests', 'abduction', 'looting', 'property destruction']
    event_hits = event_series.apply(lambda x: any(e in x for e in wellbeing_events))
    
    # Return True if either healthcare is mentioned or high-impact well-being event occurs
    return health_hits | event_hits
