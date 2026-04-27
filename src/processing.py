import pandas as pd
import numpy as np
import re
from collections import Counter

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
    RESEARCH-GRADE HICE DETECTION FRAMEWORK (Final Robustness Update).
    Implements capped confidence, bidirectional proximity, and mandatory action coupling.
    """
    notes = df['notes'].fillna('').str.lower()
    
    # 1. High-Signal Health Ontology (Restored Orgs)
    health_terms = [
        r'\bhospital(s)?\b', r'\bclinic(s)?\b', r'\bhealth center(s)?\b',
        r'\brural health center(s)?\b', r'\brhc\b', r'\bmedical facility\b',
        r'\bhealth facility\b', r'\btreatment center\b', r'\bdoctor(s)?\b', 
        r'\bnurse(s)?\b', r'\bhealth worker(s)?\b', r'\bmedic(s)?\b',
        r'\bmedical staff\b', r'\bambulance(s)?\b', r'\bmedical supplies\b',
        r'\bworld health organization\b', r'\bunicef\b', r'\bmsf\b', r'\bicrc\b',
        r'\bmedicine\b.{0,20}\b(shortage|destroyed|looted|burned|seized)\b',
        r'\bpatient(s)?\b.{0,15}\b(injured|treated|killed|arrested|wounded)\b'
    ]
    health_mask = notes.str.contains('|'.join(health_terms), regex=True)
    
    # 2. Action & Targeting Masks (Expanded Passive Voice)
    targeting_mask = notes.str.contains(r'\b(target(ed|ing)?|fired upon|opened fire on|hit by|raided|occupied)\b', regex=True)
    action_phrases = [
        r'\b(set fire to)\b',
        r'\b(was|were|had been) (destroyed|burned|attacked|looted)\b',
        r'\b(reportedly|allegedly) (attacked|targeted)\b',
        r'\bwas shot\b', r'\bwas arrested\b',
        r'\b(was forced to close|suspended operations|came under fire|sustained damage|was struck by|had to evacuate|was displaced|forced to flee)\b'
    ]
    phrase_mask = notes.str.contains('|'.join(action_phrases), regex=True)

    # 3. Bidirectional Proximity Linking (Refined health_infra)
    attack_terms = r'(?:attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit)'
    health_infra = r'(?:hospital|clinic|health center|doctor|nurse|medic|medical(?: facility| team| staff))'
    proximity_pattern = rf'({health_infra}.{{0,45}}{attack_terms})|({attack_terms}.{{0,45}}{health_infra})'
    proximity_mask = notes.str.contains(proximity_pattern, regex=True)
    
    # 4. Constrained Soft Health (Personnel/Patient context)
    soft_health_mask = notes.str.contains(r'\b(injured|wounded|killed|dead)\b.{0,20}\b(patient|doctor|nurse|medic|staff)\b', regex=True)

    # 5. ACLED Structured Filter
    attack_sub = ['Attack', 'Shelling/artillery/missile attack', 'Air/drone strike', 'Abduction/forced disappearance', 'Arrests', 'Looting/property destruction']
    violent_ev = ['Violence against civilians', 'Battles', 'Explosions/Remote violence']
    structure_mask = (df['sub_event_type'].isin(attack_sub)) | (df['event_type'].isin(violent_ev))
    
    # 6. Actor Presence (binary — avoids alias gaps in hardcoded actor lists)
    actor_presence = df['actor1'].notna().astype(int)

    # ROBUST CONFIDENCE SCORING (Capped overlaps)
    interaction_boost = (proximity_mask.astype(int) + targeting_mask.astype(int) + phrase_mask.astype(int)).clip(upper=2)
    confidence = (
        (interaction_boost * 2) +
        (health_mask.astype(int) * 2) +
        (soft_health_mask.astype(int) * 2) +
        actor_presence
    )
    
    # BYSTANDER DISAMBIGUATION FILTER (Negative Gate)
    enumeration_fp = notes.str.contains(r'(civilians?|villagers?|residents?).{0,50}(doctor|nurse|medic|patient)', regex=True) & \
                     ~notes.str.contains(r'(doctor|nurse|medic|health worker).{0,40}(killed|shot|arrested|abducted)', regex=True)
    hospital_bystander = notes.str.contains(r'\b(taken|sent|rushed|brought|admitted|transfer|transport|arrive|flee|arrive)\b.{0,20}\b(to|at|in|near).{0,15}\b(hospital|clinic|facility|dispensary)\b', regex=True) & \
                         ~notes.str.contains(r'(hospital|clinic|facility).{0,40}(attack|bomb|shell|destroy|burn|raid|strike)', regex=True)

    fp_mask = enumeration_fp | hospital_bystander

    # ACTION COUPLING & GATING
    event_coupling = (proximity_mask | phrase_mask | soft_health_mask | targeting_mask) & ~fp_mask
    strong_signal = (proximity_mask | targeting_mask) & ~fp_mask
    
    # TWO-TIER CONFIDENCE ARCHITECTURE
    tier1_mask = (health_mask | proximity_mask) & event_coupling & ((confidence >= 4) | strong_signal)
    tier2_mask = health_mask & structure_mask & event_coupling & ~tier1_mask & ~fp_mask
    
    return tier1_mask | tier2_mask

def classify_hice_type(df):
    """Classifies impacts into 5 research categories with adjusted priority."""
    notes = df['notes'].fillna('').str.lower()
    infra_markers = r'\b(hospital|clinic|pharmacy|dispensary|health center|medical center|medical facility|health facility|treatment center)\b'
    staff_markers = r'\b(doctor|nurse|midwife|surgeon|medic|medical staff|health worker)\b'
    access_markers = r'\b(closed|abandoned|no access|denied access|blocked)\b'

    # Proximity Violence (PV-HICE) routing
    attack_terms = r'(?:attack|burn|destroy|shell|raid|arrest|target|strike|fire|hit)'
    health_infra = r'(?:hospital|clinic|health center|doctor|nurse|medic|medical(?: facility| team| staff))'
    proximity_pattern = rf'({health_infra}.{{0,45}}{attack_terms})|({attack_terms}.{{0,45}}{health_infra})'
    proximity_mask = notes.str.contains(proximity_pattern, regex=True)
    direct_action = notes.str.contains(r'\b(target(ed|ing)?|fired upon|opened fire on|hit( by)?|struck( by)?|raided|occupied|destroyed|burned|attacked|looted|damaged|bomb(ed|s)?|shell(ed|s)?|airstrike|assaulted)\b', regex=True)
    pv_hice = proximity_mask & ~direct_action

    is_infra = notes.str.contains(infra_markers, regex=True)
    is_staff = notes.str.contains(staff_markers, regex=True)
    is_access = notes.str.contains(access_markers, regex=True) | pv_hice
    pers_harm = notes.str.contains(r'\b(killed|arrested|shot|abducted|beaten)\b.{0,15}\b(doctor|nurse|medic|midwife|staff)\b', regex=True)
    
    conditions = [
        pers_harm,
        is_access,
        is_infra & ~is_staff,
        is_staff & ~is_infra,
        is_infra & is_staff
    ]
    choices = ['personnel_targeting', 'access_disruption', 'infrastructure_damage', 'personnel_targeting', 'systemic_attack']
    
    return np.select(conditions, choices, default='humanitarian_disruption')

def calculate_hice_intensity(df):
    """Ranks event intensity based on ACLED sub-event type."""
    high_int = ['Air/drone strike', 'Shelling/artillery/missile attack', 'Remote explosive/landmine/IED']
    med_int = ['Attack', 'Abduction/forced disappearance', 'Arrests', 'Looting/property destruction']
    conditions = [df['sub_event_type'].isin(high_int), df['sub_event_type'].isin(med_int)]
    return np.select(conditions, ['high', 'medium'], default='low')

def extract_health_keyword_counts(text_series):
    """Counts high-precision health terms within detected HICE."""
    keywords = [
        'hospital', 'clinic', 'health center', 'medical facility', 'doctor', 'nurse', 'medic', 
        'ambulance', 'medical supplies', 'medicine', 'patient', 'world health organization', 'unicef', 'msf', 'icrc'
    ]
    combined_text = ' '.join(text_series.fillna('').str.lower())
    counts = []
    for kw in keywords:
        count = len(re.findall(r'\b' + re.escape(kw) + r'(s)?\b', combined_text))
        if count > 0:
            counts.append({'Keyword': kw.upper(), 'Frequency': count})
    return pd.DataFrame(counts).sort_values('Frequency', ascending=False)
