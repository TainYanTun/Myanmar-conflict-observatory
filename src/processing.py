import pandas as pd
import numpy as np
import re
from collections import Counter

# Source-agnostic HICE detection framework
from .hice_detector import (
    ACLEDAdapter,
    detect_hice_from_source,
    classify_hice_type as _classify_hice_type,
    extract_health_keyword_counts as _extract_health_keyword_counts,
    calculate_hice_intensity as _calculate_hice_intensity,
)

# Re-export for backward compatibility
extract_health_keyword_counts = _extract_health_keyword_counts


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

def dynamic_actor2_cleaner(row):
    """Cleans actor2 field by inferring opponent based on event type if missing."""
    EVENT_ACTOR_MAP = {
        'protest': 'Unopposed Protest',
        'battle': 'Unknown Opponent (Missing Data)',
        'strategic development': 'Strategic Movement (No Opponent)',
        'explosion': 'Remote Attack (No Direct Opponent)'
    }
    if pd.notna(row['actor2']) and str(row['actor2']).strip() != '':
        return row['actor2']
    
    event = str(row['event_type']).lower()
    for key, label in EVENT_ACTOR_MAP.items():
        if key in event:
            return label
    return "No Opponent Identified"

def extract_social_features(df):
    """Extracts social impact features from the tags column."""
    social_map = {
        'is_women_targeted': 'women targeted',
        'women_political_party': 'political party',
        'women_girls': 'girls',
        'women_relatives': 'relatives',
        'is_armed_presence': 'armed presence'
    }
    for col, keyword in social_map.items():
        df[col] = df['tags'].fillna('').str.contains(keyword, case=False, na=False)
    return df

def clean_conflict_data(df):
    """Standard cleaning logic for Myanmar conflict data."""
    df = df[df['country'] == 'Myanmar'].copy()
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df[df['event_date'] >= '2021-02-01']
    df['admin3'] = df['admin3'].fillna("Unknown Township")
    df['civilian_targeting'] = df['civilian_targeting'].fillna("Not Targeted")
    df['actor2_viz'] = df.apply(dynamic_actor2_cleaner, axis=1)
    df['assoc_actor_1_viz'] = df['assoc_actor_1'].fillna("Sole Actor")
    df['assoc_actor_2_viz'] = df['assoc_actor_2'].fillna("Sole Actor")
    df['inter2_viz'] = df['inter2'].fillna("No Interaction/Single Actor")
    df['actor1_clean'] = df['actor1'].apply(categorize_actor)
    df['actor2_clean'] = df['actor2'].apply(categorize_actor)
    df = extract_social_features(df)
    return df

def extract_keywords(text_series, top_n=20):
    """Simple keyword extraction for conflict narratives."""
    stopwords = set(['the', 'and', 'a', 'to', 'in', 'of', 'on', 'with', 'for', 'at', 'by', 'from', 'an', 'is', 'was', 'were', 'it', 'as', 'that', 'this', 'reported', 'took', 'place', 'around', 'near', 'village', 'township', 'district', 'region', 'state', 'myanmar', 'burma', 'forces', 'military', 'junta', 'people', 'defence', 'force', 'pdf', 'tatmadaw', 'knu', 'kia', 'pdf', 'ldf', 'eao', 'ia', 'army'])
    all_words = ' '.join(text_series.fillna('').str.lower().replace(r'[^a-zA-Z\s]', '', regex=True)).split()
    filtered_words = [word for word in all_words if word not in stopwords and len(word) > 3]
    counts = Counter(filtered_words).most_common(top_n)
    return pd.DataFrame(counts, columns=['Keyword', 'Frequency'])

def extract_health_impacts(df):
    """
    Detect Healthcare Interference Conflict Events (HICE) using the source-agnostic
    NLP pipeline with the ACLED adapter.

    See ``hice_detector.detect_hice()`` for the 4-layer detection logic.
    """
    adapter = ACLEDAdapter()
    return detect_hice_from_source(df, adapter)

def classify_hice_type(df):
    """Classify HICE into thematic categories. Delegates to hice_detector."""
    notes = df['notes'].fillna('').str.lower()
    return pd.Series(_classify_hice_type(notes), index=notes.index, name='hice_type')

def calculate_hice_intensity(df):
    """Rank HICE intensity. Delegates to hice_detector."""
    return _calculate_hice_intensity(df['sub_event_type'])
