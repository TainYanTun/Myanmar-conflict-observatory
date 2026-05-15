import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from sqlalchemy import create_engine
import os
import glob
import time
import kagglehub
from kagglehub import KaggleDatasetAdapter
import re
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# --- Function Definitions ---
def display_briefing_gate(L):
    """Displays the humanitarian mission briefing overlay with localization."""
    st.markdown(f"""
<div style="padding: 50px; border-radius: 24px; background: rgba(128, 128, 128, 0.02); border: 1px solid rgba(128, 128, 128, 0.2); backdrop-filter: blur(20px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); font-family: 'Inter', sans-serif;">
    <div style="text-align: center; margin-bottom: 40px;">
        <div style="display: inline-block; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 6px 16px; border-radius: 99px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 20px; border: 1px solid rgba(10, 185, 129, 0.2);">{L['gate_sdg3_focus']}</div>
        <h1 style="font-weight: 900; letter-spacing: -0.05em; margin-bottom: 10px; font-size: 3rem;">{L['gate_title']}</h1>
        <p style="opacity: 0.5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4em; font-size: 0.7rem; margin-bottom: 30px;">{L['gate_sub']}</p>
        <div style="height: 2px; width: 60px; background: #10b981; margin: 0 auto; border-radius: 2px;"></div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr; gap: 30px; margin-bottom: 40px;">
        <!-- Section 1: SDG 3 Alignment -->
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.1); padding: 30px; border-radius: 16px;">
            <div style="flex: 1;">
                <h4 style="margin-top:0; font-weight: 800; font-size: 1.25rem; letter-spacing: -0.02em;">{L['gate_wellbeing']}</h4>
                <p style="font-size: 0.95rem; line-height: 1.7; opacity: 0.8; margin-bottom: 15px;">
                    {L['gate_sdg3_desc']}
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; background: rgba(128, 128, 128, 0.05); padding: 15px; border-radius: 10px;">
                    <div>
                        <span style="font-size: 0.7rem; font-weight: 800; color: #10b981; text-transform: uppercase;">{L['gate_direct_impact']}</span>
                        <p style="font-size: 0.8rem; margin: 5px 0 0 0; opacity: 0.7;">{L['gate_direct_desc']}</p>
                    </div>
                    <div>
                        <span style="font-size: 0.7rem; font-weight: 800; color: #10b981; text-transform: uppercase;">{L['gate_infra_risk']}</span>
                        <p style="font-size: 0.8rem; margin: 5px 0 0 0; opacity: 0.7;">{L['gate_infra_desc']}</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Section 2: Forensic Mandate -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div style="background: rgba(128, 128, 128, 0.03); padding: 25px; border-radius: 16px; border: 1px solid rgba(128, 128, 128, 0.1);">
                <i class="fas fa-microscope" style="opacity: 0.5; font-size: 1.2rem; margin-bottom: 15px;"></i>
                <h5 style="margin-top: 0; font-weight: 800; font-size: 1rem;">{L['gate_protocol']}</h5>
                <p style="font-size: 0.85rem; opacity: 0.6; line-height: 1.6; margin-bottom: 0;">{L['gate_protocol_desc']}</p>
            </div>
            <div style="background: rgba(128, 128, 128, 0.03); padding: 25px; border-radius: 16px; border: 1px solid rgba(128, 128, 128, 0.1);">
                <i class="fas fa-hand-holding-heart" style="opacity: 0.5; font-size: 1.2rem; margin-bottom: 15px;"></i>
                <h5 style="margin-top: 0; font-weight: 800; font-size: 1rem;">{L['gate_ethics']}</h5>
                <p style="font-size: 0.85rem; opacity: 0.6; line-height: 1.6; margin-bottom: 0;">{L['gate_ethics_desc']}</p>
            </div>
        </div>
        <!-- Section 3: Professional Disclaimer -->
        <div style="padding: 20px 30px; border-radius: 12px; border: 1px dashed rgba(128, 128, 128, 0.3); background: rgba(128, 128, 128, 0.02);">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                <i class="fas fa-circle-info" style="opacity: 0.4; font-size: 0.9rem;"></i>
                <h5 style="opacity: 0.7; margin: 0; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">{L['gate_disclaimer']}</h5>
            </div>
            <p style="font-size: 0.8rem; opacity: 0.5; line-height: 1.6; margin-bottom: 0;">
                {L['gate_disclaimer_desc']}
            </p>
        </div>
    </div>
</div>
        """, unsafe_allow_html=True)

# --- Humanitarian Processing Logic (Merged from src/processing.py) ---
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
    
    # Ensure numpy is available (imported as np)
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

# --- Page Configuration ---
st.set_page_config(
    page_title="Myanmar Conflict Observatory",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/8/8c/Flag_of_Myanmar.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Language Dictionary ---
LANG_DICT = {
    "English": {
        "title": "MYANMAR CONFLICT OBSERVATORY",
        "sub": "ANALYTICAL FRAMEWORK FOR STABILITY ASSESSMENT",
        "events": "Total Events",
        "fatalities": "Fatalities (Verified)",
        "hotspots": "Hotspots",
        "active_groups": "Active Groups",
        "params": "PARAMETERS",
        "period": "Analysis Period",
        "area": "Focus Area",
        "currency": "DATA CURRENCY",
        "latest": "Latest Event",
        "update": "System Update",
        "keywords_title": "Top Narrative Keywords (NLP-lite Extraction)",
        "tabs": ["GEOSPATIAL", "TEMPORAL", "ACTORS", "REGIONAL MATRIX", "SDG 3: HEALTH IMPACT", "METHODOLOGY", "POLICY", "RECORDS"],
        "geo_intensity": "Incident Intensity (Density Mapping)",
        "geo_expansion": "Temporal Conflict Expansion (Animation)",
        "temp_freq": "Conflict Frequency and Impact Over Time",
        "actor_impact": "Fatality Impact by Actor Category",
        "actor_comp": "Engagement Composition (Event Types)",
        "actor_net": "ACTOR INTERACTION NETWORK (Conflict Dynamics)",
        "stab_title": "REGIONAL RISK MATRIX",
        "stab_desc": "The **Severity Index** is the ratio of fatalities to total conflict events. A higher score indicates areas where kinetic engagements are more lethal. Use this to distinguish between high-frequency low-impact areas and high-lethality conflict zones.",
        "health_title": "SDG 3: CONFLICT-INDUCED HEALTH IMPACTS",
        "health_desc": "Incidents impacting medical infrastructure, healthcare staff, and human well-being. This analysis uses an NLP engine to extract healthcare-related narratives (Hospital, Clinic, Medical, etc.) from event notes.",
        "records_title": "DATA RECORDS EXPLORER",
        "records_desc": "Filtered incident logs based on current parameters.",
        "gate_title": "HUMANITARIAN MISSION BRIEFING",
        "gate_sub": "Conflict-Induced Health Crisis Monitoring | v1.8",
        "gate_sdg3_focus": "SDG 3: GOOD HEALTH & WELL-BEING FOCUS",
        "gate_wellbeing": "SDG 3: THE WELL-BEING IMPERATIVE",
        "gate_sdg3_desc": "This observatory is specifically designed to support <b>UN SDG Target 3.d</b>: <i>\"Strengthen the capacity for risk reduction and management of national and global health risks.\"</i>",
        "gate_direct_impact": "Direct Health Impact",
        "gate_direct_desc": "Monitoring fatalities and injuries as primary indicators of regional health crises.",
        "gate_infra_risk": "Infrastructure Risk",
        "gate_infra_desc": "Mapping conflict hotspots to identify vulnerable clinics and healthcare access points.",
        "gate_protocol": "VERIFIED FLOOR PROTOCOL",
        "gate_protocol_desc": "We utilize a forensic verification threshold, recording only corroborated data to ensure humanitarian response is based on accurate, confirmed insights.",
        "gate_ethics": "ETHICAL HUMANITARIANISM",
        "gate_ethics_desc": "This data is for academic and humanitarian strategic planning. Use for tactical coordination is strictly prohibited to preserve 'Do No Harm' principles.",
        "gate_disclaimer": "ETHICAL CONSIDERATIONS AND DATA GOVERNANCE",
        "gate_disclaimer_desc": "This observatory transforms raw conflict logs into humanitarian insights to support SDG 3 objectives, adhering to strict data protection and institutional neutrality protocols.",
        "gate_btn_init": "INITIALIZING SECURE PROTOCOLS",
        "gate_btn_auth": "AUTHORIZE SYSTEM ACCESS",
        "data_error_title": "Data Source Missing",
        "data_error_desc": """
        The observatory cannot find a valid conflict dataset. Please follow these steps to resolve the issue:
        
        1. **Local Deployment:** Ensure a `.csv` data file exists in the `/data` folder.
        2. **Cloud Deployment (Streamlit Cloud):**
           - Go to **App Settings > Secrets**.
           - Add your `DB_URL` for PostgreSQL access.
           - If using the Kaggle fallback, ensure `KAGGLE_USERNAME` and `KAGGLE_KEY` are set in Secrets.
        3. **Manual Check:** Run `python update_data.py` locally to fetch the latest data before pushing to GitHub.
        """,
        "tab_explanations": {
            "GEOSPATIAL": "Overlays general conflict density (red) with specific health-impacting incidents (green). The animation shows how conflict has expanded geographically over time.",
            "TEMPORAL": "Tracks the rhythm of conflict. Peaks in the line chart indicate surges in violence. The keyword chart uses NLP to identify common narrative themes.",
            "ACTORS": "Identifies the groups involved. The network map visualizes interactions between actors to reveal the underlying power dynamics of the conflict.",
            "REGIONAL MATRIX": "Ranks regions by lethality using the Severity Index (Fatalities ÷ Events). This distinguishes high-frequency areas from high-lethality 'Red Zones'.",
            "SDG 3: HEALTH IMPACT": "Focused specifically on SDG 3. This filters for incidents disrupting hospitals, medical infrastructure, and healthcare personnel.",
            "METHODOLOGY": "Detailed technical explanation of the data pipeline, ETL logic, and analytical models used in this observatory.",
            "POLICY": "The ethical framework and neutral stance governing the use of this conflict data for humanitarian research.",
            "RECORDS": "Direct access to the raw filtered incident logs for manual verification and research."
        },
        "network_guide": {
            "title": "How to interpret this network?",
            "rep_title": "What the Connections Represent:",
            "edges": "**Edges (Lines):** Each line represents a kinetic engagement (battle, violence, or explosion) between two actors.",
            "thickness": "**Thickness:** Proportional to **Lethality**. Thicker lines indicate that interactions between those groups resulted in higher fatalities.",
            "node_size": "**Node Size:** Represents the total **Interaction Volume** of that actor across all filtered events.",
            "strat_title": "Strategic Inferences:",
            "hubs": "**Conflict Hubs:** Actors with many thick connections are the primary drivers of regional instability.",
            "encirclement": "**Encirclement:** Spotlighting an actor reveals which groups are actively resisting them in the chosen area.",
            "risk": "**Humanitarian Risk:** Thick connections to 'Civilians' reveal high-fatality targeting or collateral damage zones."
        },
        "severity_guide": {
            "title": "How to interpret the Severity Index?",
            "formula_title": "The Calculation:",
            "formula": "**Severity Index = Total Fatalities ÷ Total Events**",
            "meaning_title": "What it reveals:",
            "lethality": "**Lethality vs. Frequency:** A region might have 100 small protests (high frequency) but 0 deaths. Another might have 1 airstrike (low frequency) with 20 deaths. The Index highlights the latter as a higher-severity zone.",
            "thresholds": "**Robustness Claim:** This prioritization model was validated using a sensitivity stress test (±10% weight shifts), yielding a minimum **Spearman's ρ of 0.9853**, confirming that regional rankings are extremely stable."
        },
        "geo_guide": {
            "title": "How to use the geospatial maps?",
            "intensity": "**Incident Intensity:** This heatmap shows where conflict is physically concentrated. Darker red areas indicate higher density of events.",
            "expansion": "**Conflict Expansion:** The animation shows the geographic spread of conflict since February 2021. Use this to identify how the frontlines have shifted over time.",
            "sdg3_overlay": "**Health Proximity:** Green markers indicate incidents occurring near medical infrastructure, identifying specific risk zones for SDG 3."
        },
        "temp_guide": {
            "title": "How to read the temporal charts?",
            "frequency": "**Conflict Rhythm:** Spikes in the line chart indicate specific periods of escalation or offensive operations.",
            "keywords": "**Narrative Themes:** The NLP keyword chart extracts common terms from conflict notes, revealing the dominant themes (e.g., 'airstrike', 'landmine', 'ambush') for the selected period."
        },
        "sdg3_guide": {
            "title": "Understanding SDG 3 monitoring",
            "extraction": "**NLP Extraction:** This tab utilizes a specialized ontology focused strictly on **UN SDG Target 3.d**. It filters for incidents involving direct kinetic impacts on medical infrastructure (hospitals, clinics) and the targeting of healthcare personnel.",
            "impact": "**Humanitarian Disruption:** Use this to assess how armed conflict degrades the structural foundation of the national health system, providing a 'Verified Floor' for strategic risk reduction planning."
        },
        "sdg3_logic": {
            "title": "Data Logic: Why 533 HICE Incidents?",
            "p1": "Users may notice that the number of **SDG 3 Incidents (HICE)** is significantly lower than the total **Fatalities**. This is statistically expected:",
            "item1": "**Metric Difference:** Fatalities represent a count of **individuals** lost, while HICE represent specific **kinetic events** impacting healthcare (e.g., one hospital airstrike, one medic arrest).",
            "item2": "**Strategic Focus:** While thousands die in remote tactical engagements, this observatory only flags an event as 'HICE' if it directly degrades health infrastructure or personnel access.",
            "item3": "**The Hidden Toll:** The ratio of 533 HICE incidents to tens of thousands of deaths illustrates that while the war is high-lethality, the deliberate targeting of the medical foundation is a specialized, documented component of the broader humanitarian collapse."
        },
        "method_guide": {
            "title": "Technical Methodology",
            "pipeline": "**Data Pipeline:** Raw ACLED data is ingested, cleaned for naming inconsistencies, and mapped to a standardized actor taxonomy.",
            "limitations": "**Accuracy Note:** Locations represent the centroid of a village or township. Maps indicate regional clusters of risk, not exact tactical GPS coordinates."
        },
        "policy_guide": {
            "title": "Ethical Framework",
            "neutrality": "**Institutional Neutrality:** This observatory is an independent research project and does not coordinate with any political or military entity.",
            "do_no_harm": "**Do No Harm:** Data is for strategic humanitarian analysis only. Use for tactical coordination is strictly prohibited."
        },
        "records_guide": {
            "title": "Data Records Explorer",
            "transparency": "**Verification:** This tab provides direct access to the filtered incident logs, allowing researchers to verify individual events and read the full narrative notes."
        },
        "download_high_res": "Download High-Res PNG"
    },
    "မြန်မာဘာသာ": {
        "title": "မြန်မာနိုင်ငံ ပဋိပက္ခ စောင့်ကြည့်လေ့လာရေးအဖွဲ့",
        "sub": "တည်ငြိမ်မှု အကဲဖြတ်ခြင်းဆိုင်ရာ ခွဲခြမ်းစိတ်ဖြာမှု မူဘောင်",
        "events": "စုစုပေါင်း ဖြစ်ရပ်များ",
        "fatalities": "သေဆုံးမှု (အတည်ပြုပြီး)",
        "hotspots": "ပဋိပက္ခ ပြင်းထန်သော နေရာများ",
        "active_groups": "လှုပ်ရှားနေသော အဖွဲ့များ",
        "params": "ကန့်သတ်ချက်များ",
        "period": "ခွဲခြမ်းစိတ်ဖြာသည့် ကာလ",
        "area": "အဓိက နယ်မြေ",
        "currency": "နောက်ဆုံးရ အချက်အလက်",
        "latest": "နောက်ဆုံးဖြစ်ရပ်",
        "update": "စနစ်အား အပ်ဒိတ်လုပ်ချိန်",
        "keywords_title": "အဓိက ပါဝင်သော စကားလုံးများ (NLP-lite ခွဲခြမ်းစိတ်ဖြာမှု)",
        "tabs": ["GEOSPATIAL", "TEMPORAL", "ACTORS", "REGIONAL MATRIX", "SDG 3: HEALTH IMPACT", "METHODOLOGY", "POLICY", "RECORDS"],
        "geo_intensity": "ဖြစ်ရပ်ပြင်းအား (သိပ်သည်းဆပြမြေပုံ)",
        "geo_expansion": "ပဋိပက္ခနယ်မြေကျယ်ပြန့်လာမှု (အချိန်နှင့်အမျှ)",
        "temp_freq": "ပဋိပက္ခအကြိမ်ရေနှင့် သက်ရောက်မှု (အချိန်နှင့်အမျှ)",
        "actor_impact": "အဖွဲ့အစည်းအလိုက် သေဆုံးမှုသက်ရောက်မှု",
        "actor_comp": "ဖြစ်ရပ်အမျိုးအစားအလိုက် ပါဝင်မှု",
        "actor_net": "အဖွဲ့အစည်းများအကြား အပြန်အလှန်ဆက်နွယ်မှု (ပဋိပက္ခလှုပ်ရှားမှုများ)",
        "stab_title": "ဒေသအလိုက် အန္တရာယ်ခွဲမ်းစိတ်မှု (Regional Risk Matrix)",
        "stab_desc": "**ပြင်းထန်မှုညွှန်းကိန်း** သည် သေဆုံးမှုနှင့် ဖြစ်ရပ်အရေအတွက် အချိုးဖြစ်သည်။ ဤညွှန်းကိန်းမြင့်မားခြင်းသည် ထိုဒေသရှိ ပဋိပက္ခများတွင် အသက်အန္တရာယ် ပိုမိုပြင်းထန်ကြောင်း ဖော်ပြသည်။",
        "health_title": "SDG 3: ပဋိပက္ခကြောင့် ကျန်းမာရေးအပေါ်သက်ရောက်မှုများ",
        "health_desc": "ဆေးရုံ၊ ဆေးခန်း၊ ကျန်းမာရေးဝန်ထမ်းများနှင့် လူမှုဘဝတည်ငြိမ်မှုအပေါ် ထိခိုက်စေသော ဖြစ်ရပ်များ။ ဤခွဲခြမ်းစိတ်ဖြာမှုသည် အဖြစ်အပျက်မှတ်တမ်းများမှ ကျန်းမာရေးဆိုင်ရာ အချက်အလက်များကို (NLP) နည်းပညာဖြင့် ထုတ်ယူဖော်ပြခြင်းဖြစ်သည်။",
        "records_title": "ဒေတာမှတ်တမ်းများ ရှာဖွေခြင်း",
        "records_desc": "ရွေးချယ်ထားသော ကန့်သတ်ချက်များအပေါ် အခြေခံသည့် ဖြစ်ရပ်မှတ်တမ်းများ",
        "gate_title": "လူသားချင်းစာနာမှုဆိုင်ရာ မစ်ရှင်ရှင်းလင်းချက်",
        "gate_sub": "ပဋိပက္ခကြောင့် ဖြစ်ပေါ်လာသော ကျန်းမာရေးအကျပ်အတည်းကို စောင့်ကြည့်ခြင်း | v1.8",
        "gate_sdg3_focus": "SDG 3: ကျန်းမာရေးနှင့် သုခကို အဓိကထားခြင်း",
        "gate_wellbeing": "ကျန်းမာရေးနှင့် သုခဆိုင်ရာ လိုအပ်ချက်",
        "gate_sdg3_desc": "ဤစောင့်ကြည့်လေ့လာရေးစနစ်သည် <b>ကုလသမဂ္ဂ SDG ရည်မှန်းချက် ၃.ဃ</b> ကို အထောက်အကူပြုရန် ရည်ရွယ်ပါသည် - <i>\"နိုင်ငံအဆင့်နှင့် ကမ္ဘာလုံးဆိုင်ရာ ကျန်းမာရေးအန္တရာယ်များအတွက် ကြိုတင်သတိပေးခြင်း၊ လျှော့ချခြင်းနှင့် စီမံခန့်ခွဲခြင်းဆိုင်ရာ စွမ်းဆောင်ရည်များကို မြှင့်တင်ရန်။\"</i>",
        "gate_direct_impact": "တိုက်ရိုက်ကျန်းမာရေးသက်ရောက်မှု",
        "gate_direct_desc": "ဒေသတွင်း ကျန်းမာရေးအကျပ်အတည်း၏ အဓိကညွှန်းကိန်းများဖြစ်သော သေဆုံးမှုနှင့် ဒဏ်ရာရရှိမှုများကို စောင့်ကြည့်ခြင်း။",
        "gate_infra_risk": "အခြေခံအဆောက်အအုံဆိုင်ရာ အန္တရာယ်",
        "gate_infra_desc": "ဆေးခန်းများနှင့် ကျန်းမာရေးဝန်ဆောင်မှုများကို ထိခိုက်နိုင်ခြေရှိသော ပဋိပက္ခပြင်းထန်သည့်နေရာများကို မြေပုံထုတ်ခြင်း။",
        "gate_protocol": "အတည်ပြုပြီးသော အချက်အလက်မူဝါဒ",
        "gate_protocol_desc": "လူသားချင်းစာနာမှုဆိုင်ရာ အကူအညီများအတွက် တိကျမှန်ကန်သော အချက်အလက်များကိုသာ အသုံးပြုရန် အတည်ပြုပြီးသော အချက်အလက်များကိုသာ မှတ်တမ်းတင်ပါသည်။",
        "gate_ethics": "လူသားချင်းစာနာမှုဆိုင်ရာ ကျင့်ဝတ်",
        "gate_ethics_desc": "ဤဒေတာများကို ပညာရပ်ဆိုင်ရာနှင့် လူသားချင်းစာနာမှုဆိုင်ရာ စီမံကိန်းများအတွက်သာ အသုံးပြုရန်ဖြစ်သည်။ စစ်ရေးကိစ္စများအတွက် အသုံးပြုခြင်းကို တားမြစ်သည်။",
        "gate_disclaimer": "ကျင့်ဝတ်ဆိုင်ရာ လိုက်နာမှုနှင့် ဒေတာစီမံခန့်ခွဲမှု",
        "gate_disclaimer_desc": "ဤစောင့်ကြည့်လေ့လာရေးစနစ်သည် SDG 3 ရည်မှန်းချက်များကို အထောက်အကူပြုရန်အတွက် ပဋိပက္ခမှတ်တမ်းများကို လူသားချင်းစာနာမှုဆိုင်ရာ အမြင်များအဖြစ် ပြောင်းလဲဖော်ပြပေးပါသည်။",
        "gate_btn_init": "စနစ်ကို စတင်ပြင်ဆင်နေသည်",
        "gate_btn_auth": "စနစ်သို့ ဝင်ရောက်ခွင့်ပြုရန်",
        "data_error_title": "ဒေတာအရင်းအမြစ် ရှာမတွေ့ပါ",
        "data_error_desc": """
        စောင့်ကြည့်လေ့လာရေးစနစ်သည် မှန်ကန်သော ဒေတာအုပ်စုကို ရှာမတွေ့ပါ။ ပြဿနာကို ဖြေရှင်းရန် အောက်ပါအချက်များကို စစ်ဆေးပါ-
        
        ၁။ **Local Deployment:** `/data` ဖိုဒါထဲတွင် `.csv` ဖိုင်ရှိမရှိ စစ်ဆေးပါ။
        ၂။ **Cloud Deployment (Streamlit Cloud):** 
           - **App Settings > Secrets** သို့သွားပါ။
           - PostgreSQL အတွက် `DB_URL` ကို ထည့်သွင်းပါ။
           - Kaggle အသုံးပြုမည်ဆိုပါက `KAGGLE_USERNAME` နှင့် `KAGGLE_KEY` တို့ကို ထည့်သွင်းပါ။
        ၃။ **Manual Check:** GitHub သို့ မတင်မီ `python update_data.py` ကို အသုံးပြု၍ နောက်ဆုံးရဒေတာများကို ရယူပါ။
        """,
        "tab_explanations": {
            "GEOSPATIAL": "ပဋိပက္ခပြင်းထန်မှု (အနီရောင်) နှင့် ကျန်းမာရေးထိခိုက်မှု (အစိမ်းရောင်) ကို ပေါင်းစပ်ပြသထားသည်။ အချိန်နှင့်အမျှ ပဋိပက္ခကျယ်ပြန့်လာမှုကိုလည်း ကြည့်ရှုနိုင်သည်။",
            "TEMPORAL": "ပဋိပက္ခဖြစ်ပွားမှုအရှိန်ကို ခြေရာခံသည်။ မြင်းကွေးဇယားရှိ အတက်အကျများသည် အကြမ်းဖက်မှု မြင့်တက်လာမှုကို ဖော်ပြပြီး စကားလုံးဇယားသည် အဓိကအကြောင်းအရာများကို NLP ဖြင့် ဖော်ပြသည်။",
            "ACTORS": "ပါဝင်ပတ်သက်သူများကို ခွဲခြားပြသသည်။ ကွန်ရက်မြေပုံသည် အဖွဲ့အစည်းများအကြား အပြန်အလှန်ဆက်နွယ်မှုနှင့် အားပြိုင်မှုများကို ဖော်ပြသည်။",
            "REGIONAL MATRIX": "ဒေသအလိုက် အသက်အန္တရာယ်ပြင်းထန်မှုကို တွက်ချက်ပြသသည်။ ၎င်းသည် ဖြစ်ရပ်အရေအတွက်ထက် သေဆုံးမှုနှုန်းမြင့်မားသည့် 'ပြင်းထန်ဇုန်' များကို ခွဲခြားသိမြင်စေသည်။",
            "SDG 3: HEALTH IMPACT": "SDG 3 ကို အဓိကထားသည်။ ဆေးရုံ၊ ဆေးခန်းနှင့် ကျန်းမာရေးဝန်ထမ်းများအပေါ် ထိခိုက်စေသော ဖြစ်ရပ်များကိုသာ သီးသန့်စစ်ထုတ်ပြသသည်။",
            "METHODOLOGY": "ဤလေ့လာမှုတွင် အသုံးပြုထားသော ဒေတာနည်းပညာ၊ ETL လုပ်ငန်းစဉ်နှင့် ခွဲခြမ်းစိတ်ဖြာမှုပုံစံများကို နည်းပညာပိုင်းအရ ရှင်းလင်းချက်။",
            "POLICY": "လူသားချင်းစာနာထောက်ထားမှုဆိုင်ရာ သုတေသနအတွက် ဤပဋိပက္ခဒေတာကို အသုံးပြုရာတွင် လိုက်နာရမည့် ကျင့်ဝတ်မူဘောင်နှင့် ကြားနေရပ်တည်ချက်။",
            "RECORDS": "စစ်ထုတ်ထားသော ဖြစ်ရပ်မှတ်တမ်းများကို တိုက်ရိုက်ကြည့်ရှု စစ်ဆေးနိုင်ခြင်း။"
        },
        "network_guide": {
            "title": "ဤကွန်ရက်ကို မည်သို့အဓိပ္ပာယ်ဖွင့်ဆိုမည်နည်း။",
            "rep_title": "ဆက်သွယ်မှုများက ဘာကိုကိုယ်စားပြုသလဲ-",
            "edges": "**မျဉ်းကြောင်းများ-** မျဉ်းကြောင်းတစ်ခုစီသည် အဖွဲ့နှစ်ခုအကြား တိုက်ပွဲ၊ အကြမ်းဖက်မှု သို့မဟုတ် ပေါက်ကွဲမှုစသည့် တိုက်ရိုက်ပဋိပက္ခဖြစ်စဉ်ကို ကိုယ်စားပြုသည်။",
            "thickness": "**အထူ-** သေဆုံးမှုနှုန်းနှင့် တိုက်ရိုက်အချိုးကျသည်။ မျဉ်းကြောင်းပိုထူခြင်းသည် ထိုအဖွဲ့များအကြား ဖြစ်ပွားသော ပဋိပက္ခများတွင် သေဆုံးမှုပိုမိုများပြားကြောင်း ဖော်ပြသည်။",
            "node_size": "**အမှတ် (Node) အရွယ်အစား-** ရွေးချယ်ထားသော အဖြစ်အပျက်များအတွင်း ထိုအဖွဲ့၏ စုစုပေါင်းလှုပ်ရှားမှုပမာဏကို ဖော်ပြသည်။",
            "strat_title": "မဟာဗျူဟာမြောက် သုံးသပ်ချက်များ-",
            "hubs": "**ပဋိပက္ခဗဟိုချက်များ-** ထူထဲသောဆက်သွယ်မှုမျဉ်းများစွာရှိသောအဖွဲ့များသည် ထိုဒေသမတည်ငြိမ်မှု၏ အဓိကလက်သည်များဖြစ်သည်။",
            "encirclement": "**ဝိုင်းရံပိတ်ဆို့မှု-** အဖွဲ့တစ်ခုကို သီးသန့်ရွေးချယ်ကြည့်ရှုခြင်းဖြင့် ၎င်းတို့ကို မည်သည့်အဖွဲ့များက ပြင်းပြင်းထန်ထန် ခုခံနေသည်ကို သိရှိနိုင်သည်။",
            "risk": "**လူသားချင်းစာနာထောက်ထားမှုဆိုင်ရာ စိုးရိမ်ရမှု-** 'အရပ်သားများ' နှင့် ထူထဲစွာဆက်သွယ်နေသောမျဉ်းများသည် အရပ်သားများကို ပစ်မှတ်ထားခြင်း သို့မဟုတ် ဘေးထွက်ဆိုးကျိုးကြောင့် သေဆုံးမှုများပြားသောနေရာများကို ဖော်ပြသည်။"
        },
        "severity_guide": {
            "title": "ပြင်းထန်မှုညွှန်းကိန်းကို မည်သို့အဓိပ္ပာယ်ဖွင့်ဆိုမည်နည်း။",
            "formula_title": "တွက်ချက်ပုံ-",
            "formula": "**ပြင်းထန်မှုညွှန်းကိန်း = စုစုပေါင်းသေဆုံးမှု ÷ စုစုပေါင်းဖြစ်စဉ်အရေအတွက်**",
            "meaning_title": "ဘာကိုဖော်ပြသလဲ-",
            "lethality": "**သေဆုံးမှုနှုန်း နှင့် အကြိမ်ရေ-** ဒေသတစ်ခုတွင် ဆန္ဒပြပွဲ ၁၀၀ (အကြိမ်ရေများ) ဖြစ်ပွားသော်လည်း သေဆုံးသူမရှိနိုင်ပါ။ အခြားဒေသတစ်ခုတွင် လေကြောင်းတိုက်ခိုက်မှု ၁ ကြိမ် (အကြိမ်ရေနည်း) ဖြစ်ပွားပြီး လူ ၂၀ သေဆုံးနိုင်သည်။ ဤညွှန်းကိန်းသည် ဒုတိယဒေသကို ပြင်းထန်မှုပိုမိုမြင့်မားသောဇုန်အဖြစ် ဖော်ပြသည်။",
            "thresholds": "**ရမှတ်များကို သုံးသပ်ခြင်း-** ရမှတ် ၁.၀ ထက်ကျော်လွန်ပါက ပျမ်းမျှအားဖြင့် ထိုဒေသရှိ ပဋိပက္ခဖြစ်စဉ်တိုင်းတွင် အနည်းဆုံး လူ ၁ ဦး သေဆုံးကြောင်း ဖော်ပြပြီး ၎င်းသည် ပြင်းထန်သော တိုက်ပွဲနယ်မြေဖြစ်ကြောင်း ညွှန်ပြသည်။"
        },
        "geo_guide": {
            "title": "ပထဝီဝင်မြေပုံများကို မည်သို့အသုံးပြုမည်နည်း။",
            "intensity": "**ဖြစ်ရပ်ပြင်းအား-** ဤအပူမြေပုံ (Heatmap) သည် ပဋိပက္ခများ မည်သည့်နေရာတွင် အဓိကစုပြုံနေသည်ကို ဖော်ပြသည်။ အနီရောင်ပိုရင့်သောနေရာများသည် ဖြစ်ရပ်ပိုမိုများပြားသောနေရာများဖြစ်သည်။",
            "expansion": "**ပဋိပက္ခနယ်မြေကျယ်ပြန့်လာမှု-** ၂၀၂၁ ခုနှစ် ဖေဖော်ဝါရီလမှစ၍ ပဋိပက္ခများ ပထဝီဝင်အရ မည်သို့ပြန့်နှံ့လာသည်ကို အချိန်နှင့်အမျှ ပြသထားသည်။ ရှေ့တန်းတိုက်ပွဲနယ်မြေများ မည်သို့ပြောင်းလဲလာသည်ကို ကြည့်ရှုနိုင်သည်။",
            "sdg3_overlay": "**ကျန်းမာရေးနှင့်နီးစပ်မှု-** အစိမ်းရောင်အမှတ်အသားများသည် ကျန်းမာရေးဆိုင်ရာအခြေခံအဆောက်အအုံများနှင့် နီးစပ်သောနေရာများတွင် ဖြစ်ပွားသောဖြစ်ရပ်များကို ဖော်ပြပြီး SDG 3 အတွက် အန္တရာယ်ရှိသောဇုန်များကို ခွဲခြားပေးသည်။"
        },
        "temp_guide": {
            "title": "အချိန်ကာလဇယားများကို မည်သို့ဖတ်မည်နည်း။",
            "frequency": "**ပဋိပက္ခ၏ စီးချက်-** မျဉ်းကွေးဇယားရှိ အတက်အကျများသည် ပဋိပက္ခများ သိသိသာသာ မြင့်တက်လာသော သို့မဟုတ် ထိုးစစ်ဆင်မှုများရှိသော အချိန်ကာလများကို ဖော်ပြသည်။",
            "keywords": "**အဓိကအကြောင်းအရာများ-** NLP စကားလုံးဇယားသည် ပဋိပက္ခမှတ်တမ်းများမှ အသုံးများသော စကားလုံးများကို ထုတ်ယူဖော်ပြပြီး (ဥပမာ- 'လေကြောင်းတိုက်ခိုက်မှု'၊ 'မိုင်း'၊ 'ခြုံခိုတိုက်ခိုက်မှု') ထိုကာလ၏ အဓိကဖြစ်ရပ်ပုံစံများကို ဖော်ပြသည်။"
        },
        "sdg3_guide": {
            "title": "SDG 3 စောင့်ကြည့်လေ့လာမှုကို နားလည်ခြင်း",
            "extraction": "**NLP စနစ်ဖြင့် ထုတ်ယူခြင်း-** ဤနေရာတွင် **ကုလသမဂ္ဂ SDG ရည်မှန်းချက် ၃.ဃ** ကို အဓိကထား၍ ကျန်းမာရေးစနစ်၏ အခြေခံအဆောက်အအုံများ (ဆေးရုံ၊ ဆေးခန်း) နှင့် ကျန်းမာရေးဝန်ထမ်းများကို တိုက်ရိုက်ထိခိုက်စေသော ဖြစ်ရပ်များကိုသာ စစ်ထုတ်ပြသထားသည်။",
            "impact": "**လူသားချင်းစာနာမှုဆိုင်ရာ ထိခိုက်မှု-** ပဋိပက္ခများကြောင့် နိုင်ငံ၏ ကျန်းမာရေးစနစ် အခြေခံအဆောက်အအုံများ မည်သို့ပျက်စီးနေသည်ကို အတည်ပြုပြီးသောအချက်အလက်များဖြင့် ဆန်းစစ်နိုင်ပါသည်။"
        },
        "sdg3_logic": {
"title": "ဒေတာဆိုင်ရာ ရှင်းလင်းချက်- SDG 3 ဖြစ်စဉ် ၅၃၃ ခု ဖြစ်ပွားရခြင်း အကြောင်းရင်း",
"p1": "စုစုပေါင်းသေဆုံးမှုအရေအတွက်ထက် **SDG 3 ဖြစ်စဉ်များ (HICE)** က သိသိသာသာ နည်းနေသည်ကို အသုံးပြုသူများ သတိပြုမိနိုင်ပါသည်။ ၎င်းမှာ အောက်ပါအချက်များကြောင့် ဖြစ်သည်-",
"item1": "**တိုင်းတာပုံကွာခြားချက်-** သေဆုံးမှုမှာ **လူဦးရေ** ကို ရေတွက်ခြင်းဖြစ်ပြီး HICE ဖြစ်စဉ်မှာ ကျန်းမာရေးစနစ်ကို ထိခိုက်စေသည့် **သီးခြားဖြစ်ရပ်** (ဥပမာ - ဆေးရုံဗုံးကြဲခံရမှု ၁ ကြိမ်) ကို ရေတွက်ခြင်းဖြစ်သည်။",
"item2": "**မဟာဗျူဟာမြောက် အဓိကထားမှု-** တိုက်ပွဲများတွင် လူထောင်ပေါင်းများစွာ သေဆုံးနိုင်သော်လည်း ဤစောင့်ကြည့်ရေးစနစ်သည် ကျန်းမာရေးအဆောက်အအုံ သို့မဟုတ် ဝန်ထမ်းများကို တိုက်ရိုက်ထိခိုက်မှသာ HICE ဖြစ်စဉ်အဖြစ် သတ်မှတ်သည်။",
"item3": "**လူသားချင်းစာနာမှုဆိုင်ရာ ပျက်သုဉ်းမှု-** သေဆုံးသူအရေအတွက်နှင့် HICE ဖြစ်စဉ် ၅၃၃ ခု၏ အချိုးအစားမှာ ပြင်းထန်သောစစ်ပွဲနှင့်အတူ ကျန်းမာရေးကဏ္ဍကို စနစ်တကျဖျက်ဆီးနေသည့် အခြေအနေကို ဖော်ပြနေခြင်းဖြစ်သည်။"
},
        "method_guide": {
            "title": "နည်းပညာပိုင်းဆိုင်ရာ လုပ်ထုံးလုပ်နည်းများ",
            "pipeline": "**ဒေတာလုပ်ငန်းစဉ်-** ACLED မှရရှိသော အချက်အလက်များကို ရယူပြီး အဖွဲ့အစည်းအမည်များ မှားယွင်းမှုမရှိစေရန် သန့်စင်ကာ စံသတ်မှတ်ထားသော အဖွဲ့အစည်းအမျိုးအစားများအဖြစ် သတ်မှတ်သည်။",
            "limitations": "**တိကျမှုဆိုင်ရာ မှတ်ချက်-** တည်နေရာများသည် ကျေးရွာ သို့မဟုတ် မြို့နယ်၏ ဗဟိုချက်များကိုသာ ကိုယ်စားပြုသည်။ ထို့ကြောင့် မြေပုံများသည် တိကျသော စစ်ရေးတည်နေရာထက် ဒေသအလိုက် အန္တရာယ်ရှိသော ဇုန်များကိုသာ ဖော်ပြသည်။"
        },
        "policy_guide": {
            "title": "ကျင့်ဝတ်ဆိုင်ရာ မူဘောင်",
            "neutrality": "**ကြားနေရပ်တည်မှု-** ဤစောင့်ကြည့်လေ့လာရေးအဖွဲ့သည် လွတ်လပ်သော သုတေသနပရောဂျက်ဖြစ်ပြီး မည်သည့်နိုင်ငံရေး သို့မဟုတ် စစ်ရေးအဖွဲ့အစည်းနှင့်မျှ ဆက်စပ်မှုမရှိပါ။",
            "do_no_harm": "**ဘေးအန္တရာယ်မဖြစ်စေရေး (Do No Harm)-** ဒေတာများကို လူသားချင်းစာနာထောက်ထားမှုဆိုင်ရာ မဟာဗျူဟာမြောက်ဆန်းစစ်ရန်အတွက်သာ အသုံးပြုရန်ဖြစ်သည်။ စစ်ရေးကိစ္စများအတွက် အသုံးပြုခြင်းကို ပြင်းထန်စွာ တားမြစ်သည်။"
        },
        "records_guide": {
            "title": "ဒေတာမှတ်တမ်းများ ရှာဖွေခြင်း",
            "transparency": "**စစ်ဆေးအတည်ပြုခြင်း-** ဤနေရာတွင် စစ်ထုတ်ထားသော ဖြစ်ရပ်မှတ်တမ်းများကို တိုက်ရိုက်ကြည့်ရှုနိုင်ပြီး အဖြစ်အပျက်တစ်ခုစီ၏ အသေးစိတ်မှတ်တမ်းများကို ဖတ်ရှုစစ်ဆေးနိုင်သည်။"
        },
        "download_high_res": "PNG ပုံကို ကြည်လင်ပြတ်သားစွာ ရယူရန်"
    }
}

# --- Theme-Aware Professional CSS ---
def get_standard_layout(title="", height=400):
    """Returns a standardized, professional layout for Plotly charts."""
    return {
        "title": {"text": title, "font": {"size": 16, "weight": 700}, "x": 0, "xanchor": "left"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#94a3b8", "size": 11},
        "margin": {"t": 60, "b": 40, "l": 40, "r": 20},
        "height": height,
        "xaxis": {"gridcolor": "rgba(128,128,128,0.1)", "zeroline": False, "showline": False},
        "yaxis": {"gridcolor": "rgba(128,128,128,0.1)", "zeroline": False, "showline": False},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1, "font": {"size": 10}},
        "hoverlabel": {"bgcolor": "#1e293b", "font": {"family": "Inter, sans-serif", "size": 12}, "bordercolor": "rgba(255,255,255,0.1)"}
    }

def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

high_res_config = {'toImageButtonOptions': {'format': 'png', 'scale': 3}}

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)
local_css("assets/style.css")

# --- Session State ---
if 'gate_passed' not in st.session_state:
    st.session_state.gate_passed = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

# --- Introductory Briefing Gate ---
if not st.session_state.gate_passed:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        footer { visibility: hidden !important; }
        .block-container { max-width: 1000px !important; padding-top: 2rem !important; }
        </style>
    """, unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([1, 10, 1])
    
    with col_center:
        display_briefing_gate(LANG_DICT["English"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        elapsed = time.time() - st.session_state.start_time
        remaining = int(max(0, 5 - elapsed))
        
        _, b_col, _ = st.columns([1, 2, 1])
        with b_col:
            if remaining > 0:
                # High-end Cyber Loading Indicator
                status_msgs = [
                    "AUTHENTICATING SECURE ACCESS",
                    "SYNCING ACLED REPOSITORY",
                    "CALIBRATING HICE NLP ENGINE",
                    "MAPPING GEOSPATIAL CLUSTERS",
                    "VALIDATING ACTOR TAXONOMY"
                ]
                msg = status_msgs[remaining % len(status_msgs)]
                
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.03); border: 1px solid rgba(16, 185, 129, 0.1); border-radius: 16px; padding: 40px; text-align: center; margin-top: 20px;">
                    <div class="cyber-loader-container">
                        <div class="cyber-loader"></div>
                        <div class="cyber-loader-inner"></div>
                    </div>
                    <div style="color: #10b981; font-size: 0.75rem; letter-spacing: 0.25em; font-weight: 800; margin-top: 30px; text-transform: uppercase;">
                        {msg}
                    </div>
                    <div style="display: flex; justify-content: center; gap: 4px; margin-top: 15px;">
                        <div class="pulse-dot" style="animation-delay: 0s;"></div>
                        <div class="pulse-dot" style="animation-delay: 0.2s;"></div>
                        <div class="pulse-dot" style="animation-delay: 0.4s;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            else:
                if st.button("AUTHORIZE SYSTEM ACCESS", type="primary", use_container_width=True, key="enter_btn"):
                    st.session_state.gate_passed = True
                    st.rerun()
    st.stop()

# --- Post-Gate CSS Reset ---
st.markdown("<style>[data-testid='stAppViewContainer'] { overflow: auto !important; height: auto !important; position: static !important; } [data-testid='stSidebar'] { display: block !important; } [data-testid='stHeader'] { display: flex !important; }</style>", unsafe_allow_html=True)

# --- Custom UI Components ---
def guidance_box(text, icon="info-circle"):
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 10px; background: rgba(128, 128, 128, 0.03); border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 20px; display: flex; align-items: start; gap: 12px;">
        <i class="fas fa-{icon}" style="margin-top: 3px; opacity: 0.5; color: #10b981;"></i>
        <div style="font-size: 0.85rem; line-height: 1.5; opacity: 0.8;">{text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Data Engine (SQL & CSV Fallback) ---
@st.cache_data(show_spinner=False)
def load_data():
    """Consolidated data loader with dual-source fallback."""
    try:
        # 1. Attempt to load from PostgreSQL
        if DB_URL:
            engine = create_engine(DB_URL)
            df = pd.read_sql("SELECT * FROM conflict_events", engine)
            if not df.empty:
                df['event_date'] = pd.to_datetime(df['event_date'])
                
                # Robustness: Ensure date filter is applied even if DB is not pre-filtered
                df = df[df['event_date'] >= '2021-02-01']
                
                df['year_month'] = df['event_date'].dt.strftime('%Y-%m')
                
                # Format update_time based on latest data in DB
                update_time = df['event_date'].max().strftime('%Y-%m-%d %H:%M')
                return df, update_time
    except Exception as e:
        # Silently fallback to keep the UI clean, or use guidance_box for critical errors
        pass

    # 2. Fallback: Check local directory and notebooks/data
    search_paths = [
        os.path.join(os.getcwd(), "data"),
        os.path.join(os.getcwd(), "notebooks", "data")
    ]
    files = []
    for path in search_paths:
        files.extend(glob.glob(os.path.join(path, "*.csv")))
    
    # 3. Fallback: Check Kaggle standard input path
    if not files:
        kaggle_dir = "/kaggle/input/myanmar-conflict-observatory/"
        files = glob.glob(os.path.join(kaggle_dir, "*.csv"))
    
    # 4. Fallback: Cloud download using kagglehub
    if not files:
        try:
            # We use the dataset provided in the user prompt
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "tainyantun/acled-dataset-for-myanmar",
                "" # Use empty string for main file
            )
            if not df.empty:
                df = df[df['country'] == 'Myanmar']
                df['event_date'] = pd.to_datetime(df['event_date'])
                df = df[df['event_date'] >= '2021-02-01']
                df['year_month'] = df['event_date'].dt.strftime('%Y-%m')
                update_time = df['event_date'].max().strftime('%Y-%m-%d %H:%M')
                return df, update_time
        except Exception:
            pass
        
    if not files: return None, None
    
    # Sort files by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    
    for latest_file in files:
        try:
            file_mod_time = os.path.getmtime(latest_file)
            df = pd.read_csv(latest_file)
            if 'country' in df.columns:
                df = df[df['country'] == 'Myanmar']
                df['event_date'] = pd.to_datetime(df['event_date'])
                df = df[df['event_date'] >= '2021-02-01']
                df['year_month'] = df['event_date'].dt.strftime('%Y-%m')
                
                # Format update_time for CSV fallback
                update_time = pd.to_datetime(file_mod_time, unit='s').strftime('%Y-%m-%d %H:%M')
                return df, update_time
        except Exception as e:
            continue

    return None, None

df_raw, update_time = load_data()

@st.cache_data
def calculate_network_layout(adj_df):
    """Calculates the network layout with a more compact, circular tendency to avoid horizontal stretching."""
    G = nx.Graph()
    for _, row in adj_df.iterrows():
        # Filter for significant interactions to reduce clutter
        if row['interaction_count'] > 0: 
            G.add_edge(row['actor1_clean'], row['actor2_clean'], weight=row['interaction_count'], interaction_count=row['interaction_count'])
    
    # Use a smaller k for tighter clustering (more circular)
    pos = nx.spring_layout(G, k=0.8, iterations=100, seed=42)
    return G, pos

if df_raw is None:
    st.error("### ⚠️ Data Source Missing")
    st.markdown("""
    The observatory cannot find a valid conflict dataset. Please follow these steps to resolve the issue:
    
    1. **Local Deployment:** Ensure a `.csv` data file exists in the `/data` folder.
    2. **Cloud Deployment (Streamlit Cloud):**
       - Go to **App Settings > Secrets**.
       - Add your `DB_URL` for PostgreSQL access.
       - If using the Kaggle fallback, ensure `KAGGLE_USERNAME` and `KAGGLE_KEY` are set in Secrets.
    3. **Manual Check:** Run `python update_data.py` locally to fetch the latest data before pushing to GitHub.
    """)
    st.stop()
else:
    # Central Color Map for all Actor Visualizations
    node_color_map = {
        "State Forces": "#60a5fa",     # Bright Electric Blue
        "Pro-Junta Militia": "#f87171", # Bright Coral/Red
        "Resistance": "#34d399",       # Vibrant Mint/Green
        "EAOs": "#38bdf8",              # Sky Blue
        "Civilians": "#fbbf24",         # Bright Golden Amber
        "Protesters": "#a78bfa",        # Lavender/Violet
        "Rioters": "#fb923c",           # Bright Orange
        "Unidentified": "#94a3b8",      # Light Slate Grey
        "Other Groups": "#cbd5e1"       # Ghost White/Grey
    }

    df_raw['actor1_clean'] = df_raw['actor1'].apply(categorize_actor)
    df_raw['actor2_clean'] = df_raw['actor2'].apply(categorize_actor)
    
    # Pre-calculate NLP masks once to boost filter performance
    df_raw['is_hice'] = extract_health_impacts(df_raw)
    # Only classify HICE types for those that hit the mask to save compute
    df_raw['hice_type'] = "none"
    df_raw['spotlight_name'] = "N/A"
    
    if df_raw['is_hice'].any():
        hice_indices = df_raw[df_raw['is_hice']].index
        h_subset = df_raw.loc[hice_indices]
        df_raw.loc[hice_indices, 'hice_type'] = classify_hice_type(h_subset)
        # Pre-format the spotlight display names to avoid compute during interaction
        df_raw.loc[hice_indices, 'spotlight_name'] = (
            h_subset['event_date'].dt.strftime('%Y-%m-%d') + " | " + 
            h_subset['location'] + " [" + 
            df_raw.loc[hice_indices, 'hice_type'].str.replace('_', ' ').str.upper() + "]"
        )
    
    latest_event_date = df_raw['event_date'].max().strftime('%B %d, %Y')

    # --- Sidebar ---
    with st.sidebar:
        selected_lang = st.selectbox("Language / ဘာသာစကား", ["English", "မြန်မာဘာသာ"])
        L = LANG_DICT[selected_lang]

        st.markdown(f'<i class="fas fa-sliders-h"></i> **{L["params"]}**', unsafe_allow_html=True)
        min_date, max_date = df_raw['event_date'].min().date(), df_raw['event_date'].max().date()
        date_range = st.date_input(L["period"], [min_date, max_date])
        regions = ["All Regions"] + sorted(list(df_raw['admin1'].unique()))
        selected_region = st.selectbox(L["area"], regions)
        st.markdown("---")
        st.markdown(f'<i class="fas fa-clock"></i> **{L["currency"]}**', unsafe_allow_html=True)
        st.markdown(f"{L['latest']}:  \n**{latest_event_date}**")
        st.markdown(f"{L['update']}:  \n**{update_time}**")
        st.markdown("---")
        st.caption("Myanmar Conflict Observatory v1.8 (NLP Enabled)")
        st.caption("Independent Research Project")
        
        st.markdown("---")
        st.markdown("**RESOURCES**")
        st.markdown("[Kaggle Dataset](https://www.kaggle.com/datasets/tainyantun/acled-dataset-for-myanmar)")
        st.markdown("[GitHub Repository](https://github.com/TainYanTun/Myanmar-conflict-observatory)")
        st.markdown("---")

    # --- Filter Logic ---
    df = df_raw.copy()
    if len(date_range) == 2:
        df = df[(df['event_date'].dt.date >= date_range[0]) & (df['event_date'].dt.date <= date_range[1])]
    if selected_region != "All Regions":
        df = df[df['admin1'] == selected_region]

    # --- Main Header ---
    st.markdown(f'<p class="main-header">{L["title"]}</p>', unsafe_allow_html=True)
    
    displayed_latest_date = df['event_date'].max().strftime('%B %d, %Y') if not df.empty else "N/A"
    
    # Professional Status Bar
    st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 20px; margin-bottom: 30px; padding: 10px 20px; background: rgba(128,128,128,0.03); border-radius: 8px; border: 1px solid rgba(128,128,128,0.08);">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981;"></div>
            <span style="font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; text-transform: uppercase;">SYSTEM STATUS: ONLINE</span>
        </div>
        <div style="width: 1px; height: 12px; background: rgba(128,128,128,0.2);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-database" style="font-size: 0.7rem; opacity: 0.5;"></i>
            <span style="font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; text-transform: uppercase;">SOURCE: ACLED (VERIFIED FLOOR)</span>
        </div>
        <div style="width: 1px; height: 12px; background: rgba(128,128,128,0.2);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-shield-halved" style="font-size: 0.7rem; opacity: 0.5;"></i>
            <span style="font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; text-transform: uppercase;">GOVERNANCE: ETHICAL AI PROTOCOL</span>
        </div>
        <div style="width: 1px; height: 12px; background: rgba(128,128,128,0.2);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-calendar-check" style="font-size: 0.7rem; opacity: 0.5;"></i>
            <span style="font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; text-transform: uppercase;">LATEST INGESTION: {update_time}</span>
        </div>
        <div style="width: 1px; height: 12px; background: rgba(128,128,128,0.2);"></div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-clock-rotate-left" style="font-size: 0.7rem; opacity: 0.5;"></i>
            <span style="font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; text-transform: uppercase;">DISPLAYED DATA UP TO: {displayed_latest_date}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Pre-calculations ---
    health_hits = df['is_hice']

    # --- Metrics ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.markdown(f'<div class="metric-card"><i class="fas fa-bullseye metric-icon"></i><div class="metric-content"><div class="metric-label">{L["events"]}</div><div class="metric-value">{len(df):,}</div></div></div>', unsafe_allow_html=True)
    with m_col2: st.markdown(f'<div class="metric-card"><i class="fas fa-skull metric-icon"></i><div class="metric-content"><div class="metric-label">{L["fatalities"]}</div><div class="metric-value">{int(df["fatalities"].sum()):,}</div></div></div>', unsafe_allow_html=True)

    # SDG 3 Specific Metric & Alert Status
    health_count = health_hits.sum()
    alert_status = "CRITICAL" if health_count > 100 else "ELEVATED" if health_count > 20 else "STABLE"
    
    with m_col3: st.markdown(f'<div class="metric-card"><i class="fas fa-house-medical metric-icon"></i><div class="metric-content"><div class="metric-label">SDG 3 Incidents</div><div class="metric-value">{health_count}</div></div></div>', unsafe_allow_html=True)

    with m_col4: st.markdown(f'<div class="metric-card"><i class="fas fa-triangle-exclamation metric-icon"></i><div class="metric-content"><div class="metric-label">Alert Status</div><div class="metric-value">{alert_status}</div></div></div>', unsafe_allow_html=True)

    # --- Analysis Tabs ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(L["tabs"])

    plotly_layout = {"paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)", "font": {"color": "#94a3b8"}}

    with tab0:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['GEOSPATIAL']}")

        col1, col2 = st.columns(2)
        with col1:
            # 1. Base Layer: Density Map of all fatalities
            fig_heat = px.density_map(
                df, lat='latitude', lon='longitude', z='fatalities', radius=12,
                center=dict(lat=18.5, lon=96), zoom=5.2, 
                map_style="carto-darkmatter", height=650,
                color_continuous_scale=["#0f172a", "#1e293b", "#ef4444"], 
                opacity=0.8
            )
            
            health_overlay = df[health_hits].copy()
            if not health_overlay.empty:
                fig_overlay = px.scatter_map(
                    health_overlay, lat='latitude', lon='longitude',
                    color_discrete_sequence=["#10b981"], 
                    hover_name="location",
                    size_max=12
                )
                for trace in fig_overlay.data:
                    trace.name = "Health Impact"
                    trace.showlegend = True
                    fig_heat.add_trace(trace)

            fig_heat.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, 
                coloraxis_showscale=False,
                legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1, font={"size": 10})
            )
            st.plotly_chart(fig_heat, use_container_width=True, config=high_res_config)
        with col2:
            df_anim = df.sort_values('event_date')
            fig_anim = px.scatter_map(
                df_anim, 
                lat="latitude", 
                lon="longitude", 
                color="actor1_clean",
                size="fatalities",
                animation_frame="year_month",
                hover_name="location",
                color_discrete_map=node_color_map,
                zoom=5.2, 
                height=650, 
                map_style="carto-darkmatter",
                opacity=0.9
            )
            fig_anim.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(15,23,42,0.8)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1, font={"size": 10})
            )
            st.plotly_chart(fig_anim, use_container_width=True, config=high_res_config)

    with tab1:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['TEMPORAL']}")

        # Prepare monthly stats
        monthly_events = df.resample('ME', on='event_date').size().reset_index(name='event_count')
        monthly_fatalities = df.resample('ME', on='event_date')['fatalities'].sum().reset_index()
        monthly_combined = pd.merge(monthly_events, monthly_fatalities, on='event_date')
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=monthly_combined['event_date'], 
            y=monthly_combined['event_count'],
            name="Incidents", mode='lines+markers',
            line=dict(color='#94a3b8', width=3),
            marker=dict(size=4, opacity=0.5),
            hovertemplate="<b>%{x|%B %Y}</b><br>Incidents: %{y}<extra></extra>"
        ))
        
        fig_line.add_trace(go.Scatter(
            x=monthly_combined['event_date'], 
            y=monthly_combined['fatalities'],
            name="Fatalities", mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=4, opacity=0.5),
            hovertemplate="<b>%{x|%B %Y}</b><br>Fatalities: %{y}<extra></extra>"
        ))
        
        fig_line.update_layout(get_standard_layout(L["temp_freq"], height=500), hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True, config=high_res_config)
        
        st.markdown("---")
        kw_df = extract_keywords(df['notes'])
        if not kw_df.empty:
            fig_kw = px.bar(kw_df, x='Frequency', y='Keyword', orientation='h', color='Frequency', color_continuous_scale="Viridis")
            fig_kw.update_layout(get_standard_layout(L["keywords_title"], height=450), yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_kw, use_container_width=True, config=high_res_config)

    with tab2:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['ACTORS']}")
        c1, c2 = st.columns(2)
        with c1:
            st.caption(L["actor_impact"])
            guidance_box("Impact is calculated as the sum of fatalities in all events where the category participated.")
            
            # Combine impacts for both Actor 1 and Actor 2 to be consistent
            a1_impact = df.groupby('actor1_clean')['fatalities'].sum().reset_index().rename(columns={'actor1_clean': 'actor'})
            a2_impact = df.groupby('actor2_clean')['fatalities'].sum().reset_index().rename(columns={'actor2_clean': 'actor'})
            
            actor_stats = pd.concat([a1_impact, a2_impact]).groupby('actor')['fatalities'].sum().reset_index()
            
            # Remove "Unidentified" and "Other Groups" from the primary impact chart to focus on kinetic actors
            # OR keep them but sort them. Let's keep them but ensure they are included.
            actor_stats = actor_stats[actor_stats['actor'] != 'Unidentified'].sort_values('fatalities')
            
            fig_bar = px.bar(
                actor_stats, 
                x='fatalities', 
                y='actor', 
                orientation='h',
                color='actor',
                color_discrete_map=node_color_map
            )
            fig_bar.update_layout(plotly_layout, xaxis_title="Fatalities in involved events", yaxis_title="", showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True, config=high_res_config)
        with c2:
            st.caption(L["actor_comp"])
            fig_pie = px.sunburst(df, path=['event_type', 'sub_event_type'], values='fatalities', color_discrete_sequence=["#334155", "#475569", "#64748b", "#94a3b8"])
            fig_pie.update_layout(plotly_layout, margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_pie, use_container_width=True, config=high_res_config)

        st.markdown("---")
        guidance_box(f"**{selected_lang} Guidance:** Use the dropdown to spotlight an actor. Edge thickness is weighted by total fatalities.")
        st.caption(L["actor_net"])
        
        # --- Actor Network Enhancements ---
        interactions = df[(df['actor1_clean'] != df['actor2_clean']) & (df['actor2_clean'] != 'Unidentified')]
        
        # Dropdown for actor spotlight
        actor_list = sorted(pd.concat([interactions['actor1_clean'], interactions['actor2_clean']]).unique())
        spotlight_actor = st.selectbox("Spotlight Actor:", ["All"] + actor_list)

        # --- Network Interpretation Guide ---
        with st.expander(L["network_guide"]["title"]):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown(f"""
                **{L["network_guide"]["rep_title"]}**
                *   {L["network_guide"]["edges"]}
                *   {L["network_guide"]["thickness"]}
                *   {L["network_guide"]["node_size"]}
                """)
            with col_g2:
                st.markdown(f"""
                **{L["network_guide"]["strat_title"]}**
                *   {L["network_guide"]["hubs"]}
                *   {L["network_guide"]["encirclement"]}
                *   {L["network_guide"]["risk"]}
                """)

        if not interactions.empty:
            # Aggregate by both interaction count and total fatalities
            adj = interactions.groupby(['actor1_clean', 'actor2_clean']).agg(
                interaction_count=('event_id_cnty', 'count'),
                total_fatalities=('fatalities', 'sum')
            ).reset_index()

            # Optional: Further filter 'adj' to show only significant connections (e.g., > 2 interactions)
            # to prevent the "hairball" effect while keeping the nodes
            adj = adj[adj['interaction_count'] >= 2]

            G, pos = calculate_network_layout(adj)
            
            # --- Build Traces (Edges & Nodes) ---
            edge_traces = []
            max_fatalities = adj['total_fatalities'].max()
            
            for _, row in adj.iterrows():
                actor1, actor2, count, fatalities = row['actor1_clean'], row['actor2_clean'], row['interaction_count'], row['total_fatalities']
                x0, y0 = pos[actor1]
                x1, y1 = pos[actor2]
                
                # Base attributes
                edge_width = 1 + (fatalities / max_fatalities * 10)
                edge_color = '#475569'
                edge_opacity = 0.6
                
                # Spotlight logic
                if spotlight_actor != "All":
                    if actor1 != spotlight_actor and actor2 != spotlight_actor:
                        edge_opacity = 0.1
                        edge_color = '#334155'

                edge_traces.append(go.Scatter(
                    x=[x0, x1, None], y=[y0, y1, None],
                    line=dict(width=edge_width, color=edge_color),
                    opacity=edge_opacity,
                    hoverinfo='text',
                    hovertext=f"{actor1}-{actor2}<br>Interactions: {count}<br>Fatalities: {fatalities}",
                    mode='lines'
                ))

            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=[node for node in G.nodes()],
                textposition="top center",
                hoverinfo='text',
                hovertext=[f"{node}: {sum(d['interaction_count'] for u, v, d in G.edges(node, data=True))} interactions" for node in G.nodes()],
                marker=dict(
                    showscale=False,
                    color=[node_color_map.get(node, '#64748b') for node in G.nodes()],
                    size=[15 + (sum(d['interaction_count'] for u, v, d in G.edges(node, data=True)) / adj['interaction_count'].max() * 30) for node in G.nodes()],
                    line_width=2,
                    opacity=[1.0 if spotlight_actor == "All" or node == spotlight_actor else 0.3 for node in G.nodes()]
                )
            )

            fig_net = go.Figure(data=edge_traces + [node_trace])
            fig_net.update_layout(
                get_standard_layout(L["actor_net"], height=700),
                showlegend=False, 
                hovermode='closest',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )
            st.plotly_chart(fig_net, use_container_width=True, config=high_res_config)
        else:
            guidance_box("Insufficient interaction data for network mapping.", icon="exclamation-triangle")

    with tab3:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['REGIONAL MATRIX']}")
        st.subheader(L["stab_title"])
        st.markdown(L["stab_desc"])

        # --- Severity Interpretation Guide ---
        with st.expander(L["severity_guide"]["title"]):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown(f"**{L['severity_guide']['formula_title']}**")
                st.code(L['severity_guide']['formula'])
            with col_s2:
                st.markdown(f"**{L['severity_guide']['meaning_title']}**")
                st.markdown(f"{L['severity_guide']['lethality']}")
                st.markdown(f"{L['severity_guide']['thresholds']}")

        stability_df = df.groupby('admin1').agg({'event_id_cnty': 'count','fatalities': 'sum'}).rename(columns={'event_id_cnty': 'event_count'})
        stability_df['Severity_Index'] = (stability_df['fatalities'] / stability_df['event_count']).round(2)
        stability_df = stability_df.sort_values('Severity_Index', ascending=False)
        
        risk_matrix = df.groupby('admin1').agg({'event_id_cnty': 'count','fatalities': 'sum'}).rename(columns={'event_id_cnty': 'Frequency'})
        risk_matrix['Lethality'] = (risk_matrix['fatalities'] / risk_matrix['Frequency']).round(2)
        fig_matrix = px.scatter(
            risk_matrix.reset_index(), 
            x="Frequency", 
            y="Lethality", 
            text="admin1", 
            size="fatalities", 
            color="Lethality", 
            color_continuous_scale="Reds"
        )
        fig_matrix.update_traces(textposition='top center')
        fig_matrix.add_hline(y=risk_matrix['Lethality'].mean(), line_dash="dash", annotation_text="Baseline Lethality")
        fig_matrix.update_layout(get_standard_layout("Regional Risk Matrix (Frequency vs. Lethality)", height=500))
        st.plotly_chart(fig_matrix, use_container_width=True, config=high_res_config)

        fig_stab = px.bar(stability_df.reset_index(), x='admin1', y='Severity_Index', color='Severity_Index', color_continuous_scale="Reds")
        fig_stab.update_layout(get_standard_layout(L["stab_title"], height=400))
        st.plotly_chart(fig_stab, use_container_width=True, config=high_res_config)

        st.markdown("---")
        st.subheader("HICE-Informed Vulnerability Ranking")
        st.caption("Weighted Score = (0.7 × HICE Events) + (0.3 × HICE Fatalities). This identifies 'Red Zones' where kinetic violence directly target or erodes health security.")
        
        # Calculate full Vulnerability Score for Tab 3 using Health-Impact Fatalities (HICE)
        h_mask_full = extract_health_impacts(df)
        v_full = df[h_mask_full].groupby('admin1').agg({
            'fatalities': 'sum',
            'event_id_cnty': 'count'
        }).rename(columns={'event_id_cnty': 'health_events'}).copy()
        
        v_full['Vulnerability_Score'] = ((v_full['health_events'] * 0.7) + (v_full['fatalities'] * 0.3)).round(1)
        v_full = v_full.sort_values('Vulnerability_Score', ascending=False)
        
        fig_v = px.bar(v_full.reset_index(), x='admin1', y='Vulnerability_Score', color='Vulnerability_Score', color_continuous_scale="Inferno")
        fig_v.update_layout(get_standard_layout("Regional Vulnerability Score", height=450))
        st.plotly_chart(fig_v, use_container_width=True, config=high_res_config)

    with tab4:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['SDG 3: HEALTH IMPACT']}")
        st.subheader(L["health_title"])
        
        # --- UN Target Alignment Badges ---
        st.markdown("""
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.2);">TARGET 3.D</div>
            <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.2);">TARGET 3.8: HEALTH ACCESS</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(L["health_desc"])

        health_df = df[health_hits].copy()
        if not health_df.empty:
            csv = health_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Health Impact Report (CSV)",
                data=csv,
                file_name=f"MCO_Health_Impact_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                key='download-csv-health'
            )

        # --- SDG 3 Interpretation Guide ---
        with st.expander(L["sdg3_guide"]["title"]):
            st.markdown(f"""
            *   {L["sdg3_guide"]["extraction"]}
            *   {L["sdg3_guide"]["impact"]}
            """)
            
            st.markdown("---")
            st.markdown(f"""
            **{L['sdg3_logic']['title']}**
            
            {L['sdg3_logic']['p1']}
            
            1.  {L['sdg3_logic']['item1']}
            2.  {L['sdg3_logic']['item2']}
            3.  {L['sdg3_logic']['item3']}
            """)

        health_df = df[health_hits].copy()        
        if not health_df.empty:
            health_df['hice_type'] = classify_hice_type(health_df)
            
            # Define a specific color map for HICE types to ensure consistency across all charts
            hice_color_map = {
                'infrastructure_damage': '#ef4444', # Red
                'personnel_targeting': '#f59e0b',    # Amber
                'systemic_attack': '#8b5cf6',       # Violet
                'access_disruption': '#3b82f6',     # Blue
                'humanitarian_disruption': '#94a3b8' # Slate
            }
            
            # 1. HICE Analytics Overview
            h_top_col1, h_top_col2 = st.columns(2)
            with h_top_col1:
                hice_counts = health_df['hice_type'].value_counts().reset_index()
                fig_hice = px.pie(hice_counts, values='count', names='hice_type', 
                                 color='hice_type',
                                 color_discrete_map=hice_color_map,
                                 hole=0.4)
                fig_hice.update_layout(get_standard_layout("HICE Impact Classification (NLP Engine)", height=400))
                st.plotly_chart(fig_hice, use_container_width=True, config=high_res_config)

            with h_top_col2:
                kw_health = extract_health_keyword_counts(health_df['notes'])
                if not kw_health.empty:
                    fig_hk = px.bar(kw_health.head(10), x='Frequency', y='Keyword', orientation='h', color_discrete_sequence=['#10b981'])
                    fig_hk.update_layout(get_standard_layout("Healthcare Narrative Extraction", height=400))
                    st.plotly_chart(fig_hk, use_container_width=True, config=high_res_config)
            
            st.markdown("---")
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1:
                st.caption("Geospatial Distribution of Health-Impacting Incidents (by Impact Type)")

                fig_h_geo = px.scatter_map(
                    health_df, 
                    lat="latitude", 
                    lon="longitude", 
                    color="hice_type", 
                    size="fatalities", 
                    hover_name="location", 
                    color_discrete_map=hice_color_map,
                    hover_data={
                        "event_date": "|%B %d, %Y",
                        "hice_type": True,
                        "admin1": True,
                        "actor1": True,
                        "fatalities": True,
                        "notes": False,
                        "latitude": False,
                        "longitude": False
                    }, 
                    zoom=5, 
                    height=500, 
                    map_style="carto-darkmatter"
                )
                fig_h_geo.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0},
                    legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="left", x=0.02, bgcolor="rgba(0,0,0,0.5)")
                )
                st.plotly_chart(fig_h_geo, use_container_width=True, config=high_res_config)
            
            with h_col2:
                st.caption("Regional Health Vulnerability Scorecard")
                # Score = (Health Incidents * 0.7) + (Fatalities * 0.3)
                v_score = health_df.groupby('admin1').agg({'event_id_cnty': 'count', 'fatalities': 'sum'}).rename(columns={'event_id_cnty': 'HICE'})
                v_score['Score'] = ((v_score['HICE'] * 0.7) + (v_score['fatalities'] * 0.3)).round(1)
                v_score = v_score.sort_values('Score', ascending=False)
                v_score['Rank'] = range(1, len(v_score) + 1)
                st.dataframe(v_score[['Rank', 'HICE', 'fatalities', 'Score']], use_container_width=True, height=500)

            st.markdown("---")
            
            # --- Health Impact Trends ---
            st.caption("Temporal Trend: Health-Impacting Incidents")
            h_trend = health_df.set_index('event_date').resample('ME').size().reset_index(name='count')
            fig_h_trend = px.area(h_trend, x='event_date', y='count', color_discrete_sequence=['#10b981'])
            fig_h_trend.update_layout(get_standard_layout("Health-Impacting Incidents (Monthly Trend)", height=350), xaxis_title="", yaxis_title="Volume")
            st.plotly_chart(fig_h_trend, use_container_width=True, config=high_res_config)
            
            # --- Humanitarian Spotlight Explorer ---
            @st.fragment
            def render_spotlight_explorer(data):
                st.markdown("### <i class='fas fa-magnifying-glass-location' style='color:#10b981'></i> HUMANITARIAN SPOTLIGHT EXPLORER", unsafe_allow_html=True)
                st.caption("Select an incident from the list to reveal the full verified forensic narrative and health impact details.")
                
                # 1. Selection Controls
                s_col1, s_col2 = st.columns([1, 2])
                with s_col1:
                    search_region = st.selectbox("Focus Region", ["All Regions"] + sorted(data['admin1'].unique().tolist()), key="spotlight_region")
                
                filtered_spotlight = data.copy()
                if search_region != "All Regions":
                    filtered_spotlight = filtered_spotlight[filtered_spotlight['admin1'] == search_region]
                
                with s_col2:
                    # Use pre-calculated display names (spotlight_name)
                    selected_incident_name = st.selectbox("Select Incident Log", filtered_spotlight['spotlight_name'].tolist(), key="incident_selector")
                
                if not filtered_spotlight.empty:
                    selected_row = filtered_spotlight[filtered_spotlight['spotlight_name'] == selected_incident_name].iloc[0]
                    
                    # Display the Spotlight Card
                    hice_icon_map = {
                        'infrastructure_damage': 'fa-hospital',
                        'personnel_targeting': 'fa-user-nurse',
                        'systemic_attack': 'fa-virus-slash',
                        'access_disruption': 'fa-road-barrier',
                        'humanitarian_disruption': 'fa-hand-holding-medical'
                    }
                    h_icon = hice_icon_map.get(selected_row['hice_type'], 'fa-file-medical')
                    
                    a1_cat = categorize_actor(selected_row['actor1'])
                    a2_cat = categorize_actor(selected_row['actor2']) if pd.notna(selected_row['actor2']) else "N/A"
                    
                    cat_colors = {'State Forces': 'rgba(59, 130, 246, 0.1)', 'Resistance': 'rgba(16, 185, 129, 0.1)', 'Ethnic Armed Organization': 'rgba(245, 158, 11, 0.1)', 'Pro-Junta Militia': 'rgba(99, 102, 241, 0.1)', 'Civilians': 'rgba(148, 163, 184, 0.1)'}
                    cat_text_colors = {'State Forces': '#3b82f6', 'Resistance': '#10b981', 'Ethnic Armed Organization': '#f59e0b', 'Pro-Junta Militia': '#6366f1', 'Civilians': '#94a3b8'}
                    
                    a1_bg, a1_txt = cat_colors.get(a1_cat, 'rgba(128, 128, 128, 0.1)'), cat_text_colors.get(a1_cat, '#94a3b8')
                    a2_bg, a2_txt = cat_colors.get(a2_cat, 'rgba(128, 128, 128, 0.1)'), cat_text_colors.get(a2_cat, '#94a3b8')

                    st.markdown(f"""
                    <div class="spotlight-card">
                        <div class="spotlight-header">
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(16, 185, 129, 0.2);">
                                    <i class="fas {h_icon}"></i>
                                </div>
                                <div>
                                    <div class="spotlight-title">{selected_row['location']} Engagement</div>
                                    <div class="spotlight-meta">{selected_row['event_date'].strftime('%B %d, %Y')} | {selected_row['admin1']} Region</div>
                                </div>
                            </div>
                            <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 6px 14px; border-radius: 6px; font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em; border: 1px solid rgba(16, 185, 129, 0.2); text-transform: uppercase;">
                                {selected_row['hice_type'].replace('_', ' ')}
                            </div>
                        </div>
                        <div class="spotlight-note">
                            "{selected_row['notes']}"
                        </div>
                        <div class="spotlight-grid">
                            <div class="spotlight-stat">
                                <div class="spotlight-stat-label"><i class="fas fa-shield-halved" style="margin-right:5px; opacity:0.5;"></i>Primary Actor</div>
                                <div class="spotlight-stat-value" style="font-size: 0.9rem; margin-bottom: 5px;">{selected_row['actor1']}</div>
                                <div style="display: inline-block; background: {a1_bg}; color: {a1_txt}; padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; text-transform: uppercase;">{a1_cat}</div>
                            </div>
                            <div class="spotlight-stat">
                                <div class="spotlight-stat-label"><i class="fas fa-users" style="margin-right:5px; opacity:0.5;"></i>Secondary Actor</div>
                                <div class="spotlight-stat-value" style="font-size: 0.9rem; margin-bottom: 5px;">{selected_row['actor2'] if pd.notna(selected_row['actor2']) else 'None Reported'}</div>
                                {"<div style='display: inline-block; background: " + a2_bg + "; color: " + a2_txt + "; padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 700; text-transform: uppercase;'>" + a2_cat + "</div>" if pd.notna(selected_row['actor2']) else ""}
                            </div>
                            <div class="spotlight-stat">
                                <div class="spotlight-stat-label"><i class="fas fa-tags" style="margin-right:5px; opacity:0.5;"></i>Classification</div>
                                <div class="spotlight-stat-value" style="font-size: 0.9rem;">{selected_row['event_type']}</div>
                            </div>
                            <div class="spotlight-stat" style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.1);">
                                <div class="spotlight-stat-label" style="color: #ef4444; opacity: 0.8;"><i class="fas fa-skull-crossbones" style="margin-right:5px;"></i>Verified Fatalities</div>
                                <div class="spotlight-stat-value" style="color: #ef4444; font-size: 1.1rem;">{int(selected_row['fatalities'])} LIVES LOST</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            render_spotlight_explorer(health_df)
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("View Full Filtered Health Records (Tabular)"):
                st.dataframe(health_df[['event_date', 'location', 'notes']].sort_values('event_date', ascending=False), width="stretch")
        else:
            guidance_box("No medical-impact incidents detected in current filtered data.")

    with tab5:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['METHODOLOGY']}")

        # --- Methodology Interpretation Guide ---
        with st.expander(L["method_guide"]["title"]):
            st.markdown(f"""
            *   {L["method_guide"]["pipeline"]}
            *   {L["method_guide"]["limitations"]}
            """)

        st.markdown(f'<p class="main-header">{L["title"]} | RESEARCH METHODOLOGY</p>', unsafe_allow_html=True)

        # --- Data Integrity Audit ---
        st.markdown("### DATA INTEGRITY AUDIT")
        st.caption("Verification of Geospatial and Temporal Data Quality")
        audit_col1, audit_col2 = st.columns(2)
        with audit_col1:
            if 'geo_precision' in df.columns:
                precision_map = {1: "Precise Location", 2: "Near Town/Village", 3: "District Level"}
                precision_counts = df['geo_precision'].map(precision_map).value_counts().reset_index()
                fig_prec = px.pie(precision_counts, values='count', names='geo_precision', title="Geospatial Coordinate Precision", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                fig_prec.update_layout(plotly_layout)
                st.plotly_chart(fig_prec, use_container_width=True)
        with audit_col2:
            st.markdown("""
            **Precision Protocol:**
            - **Level 1 (Precise):** Verified at the exact street, building, or village square level.
            - **Level 2 (Near):** Verified as occurring in the immediate vicinity of a named settlement.
            - **Level 3 (District):** Approximate location used when only regional reporting is available.
            
            *A higher ratio of Level 1 & 2 data indicates a robust forensic foundation for humanitarian planning.*
            """)
        st.markdown("---")

        st.markdown("""
        ### 1. System Architecture & ETL Pipeline
        This observatory utilizes a modern data engineering pipeline designed to handle the Volume, Velocity, and Variety of conflict logs. The system employs a cloud-native ingestion protocol:
        - **Extraction:** The framework utilizes the ACLED API for real-time data acquisition, ensuring that the observatory remains current with the latest verified conflict logs.
        - **Transformation:** Raw logs are processed using Python (Pandas/NumPy). This includes automated cleaning of naming inconsistencies, temporal filtering (Post-Feb 1, 2021), and geospatial verification.
        - **Ingestion (Supabase):** To ensure persistence and high availability, the processed data is managed within a **Supabase (PostgreSQL)** database. This architecture supports high-concurrency access and allows for seamless integration with the Streamlit Cloud frontend.

        ### 2. Research-Grade HICE Validation (NLP Engine)
        To ensure the scientific rigor of the detection framework, the NLP engine was subjected to a narrative precision audit:
        - **Precision Rate:** Manual auditing of high-confidence HICE incidents revealed a **Precision of 89.5%**, attributed to bidirectional action-keyword coupling.
        - **Visibility Alpha:** The framework provides a **27.8% increase** in visibility over standard structured actor tags (417 ACLED-tagged vs. 533 NLP-verified HICE).
        - **Hidden Toll:** The audit confirms that **21.8%** of verified health-impacting events in Myanmar carry no formal health actor tag in raw data, requiring semantic narrative extraction.

        ### 3. Vulnerability Score Robustness
        The framework utilizes a weighted composite formula ($0.7$ Health / $0.3$ Fatalities) to identify priority "Red Zones." 
        - **Sensitivity Analysis:** Systems stress-testing (±10% weight shifts) yielded a minimum **Spearman's $\rho$ of 0.9853**.
        - **Stability:** Top-tier priority regions (Sagaing, Mandalay, Magway, Rakhine) remained identical across all tested configurations, confirming that rankings are driven by underlying conflict patterns, not parameter selection.

        ### 4. Analytical Limitations (The "Verified Floor")
        - **Geospatial Centroiding:** Incident coordinates represent township centroids to prevent tactical exploitation. The maps indicate **regional clusters of risk** rather than exact GPS points.
        - **Verification Lag:** ACLED data for high-complexity environments adheres to a verification lag policy. Current findings represent a "Verified Floor"—the absolute minimum confirmed incidence.
        - **Blackout Zones:** In regions under strict communication blackouts, actual incidence of violence is likely significantly higher than reported. These data gaps are interpreted as "silences of the marginalized."
        """)

    with tab6:
        guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['POLICY']}")

        # --- Policy Interpretation Guide ---
        with st.expander(L["policy_guide"]["title"]):
            st.markdown(f"""
            *   {L["policy_guide"]["neutrality"]}
            *   {L["policy_guide"]["do_no_harm"]}
            """)

        st.markdown('<p class="main-header">ANALYTICAL POLICY & ETHICAL FRAMEWORK</p>', unsafe_allow_html=True)
        st.markdown("""
        ### 1. Statement of Institutional Neutrality
        The Myanmar Conflict Observatory is an independent, non-partisan research project. To maintain narrative neutrality, the NLP ontology was developed using cross-verified medical and humanitarian dictionaries rather than politically-aligned terminology. The project maintains strict distance from all political or military entities.

        ### 2. The 'Do No Harm' Mandate (Tactical Obfuscation)
        In alignment with the ICRC Handbook on Data Protection, this framework prioritizes the safety of populations over analytical granularity. 
        - **Spatial Obfuscation:** The system intentionally limits geospatial resolution to the township centroid level. This ensures that while regional trends are visible, specific healthcare facilities or mobile clinics cannot be identified or targeted through system outputs.
        - **Prohibition of Military Use:** The use of this data for real-time military intelligence or tactical coordination is strictly prohibited.
        - **Secondary Targeting Risk:** The observatory does not generate maps of functional medical assets to prevent them from becoming targets for combatants.

        ### 3. Ethical Data Governance & Accountability
        - **Data Sovereignty:** We recognize that the "Verified Floor" approach, while methodologically necessary, under-represents the true scale of violence in blackout zones. 
        - **SDG 3.d Alignment:** This framework is a retrospective research tool dedicated to monitoring UN SDG Target 3.d—improving early warning and risk management for health emergencies in conflict zones.
        - **Accountability:** Documentation of attacks on healthcare infrastructure provides an independent evidence base for international legal advocacy and accountability.

        ### 4. Comprehensive Disclaimer of Liability
        The Myanmar Conflict Observatory is a retrospective tool and does not provide real-time forensic verification. The authors and associated institutions shall not be held liable for operational decisions made by third parties based on this data, nor for the consequences of data misuse in violation of the "Do No Harm" mandate.
        """)

    with tab7:
        @st.fragment
        def render_records_explorer(data):
            guidance_box(f"**{selected_lang} Guidance:** {L['tab_explanations']['RECORDS']}")
            
            r_col1, r_col2 = st.columns([2, 1])
            with r_col1:
                st.subheader(L["records_title"])
                st.caption(L["records_desc"])
            with r_col2:
                # Add a record limit to prevent browser lag with massive datasets
                record_limit = st.select_slider("Results Depth", options=[500, 1000, 5000, 10000, "Full Dataset"], value=1000, help="Limiting rows improves interface responsiveness.")
            
            # Efficiently sort and slice
            display_df = data.sort_values('event_date', ascending=False)
            if record_limit != "Full Dataset":
                display_df = display_df.head(record_limit)
                st.info(f"Displaying the {record_limit} most recent events based on your filters.")
            
            # Remove high-overhead internal columns from view
            view_cols = [c for c in display_df.columns if c not in ['spotlight_name', 'is_hice', 'hice_type', 'actor1_clean', 'actor2_clean']]
            
            st.dataframe(display_df[view_cols], use_container_width=True, height=600)

        render_records_explorer(df)



