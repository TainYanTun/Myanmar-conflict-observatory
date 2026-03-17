import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from sqlalchemy import create_engine
import os
import glob
import time
import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime
from dotenv import load_dotenv
from src.processing import categorize_actor, extract_keywords, extract_health_impacts

# Load Environment Variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# --- Function Definitions ---
def display_briefing_gate():
    """Displays the humanitarian mission briefing overlay."""
    st.markdown("""
<div style="padding: 50px; border-radius: 24px; background: rgba(128, 128, 128, 0.02); border: 1px solid rgba(128, 128, 128, 0.2); backdrop-filter: blur(20px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); font-family: 'Inter', sans-serif;">
    <div style="text-align: center; margin-bottom: 40px;">
        <div style="display: inline-block; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 6px 16px; border-radius: 99px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 20px; border: 1px solid rgba(10, 185, 129, 0.2);">SDG 3: GOOD HEALTH & WELL-BEING FOCUS</div>
        <h1 style="font-weight: 900; letter-spacing: -0.05em; margin-bottom: 10px; font-size: 3rem;">HUMANITARIAN MISSION BRIEFING</h1>
        <p style="opacity: 0.5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4em; font-size: 0.7rem; margin-bottom: 30px;">Conflict-Induced Health Crisis Monitoring | v1.8 (Hackathon Edition)</p>
        <div style="height: 2px; width: 60px; background: #10b981; margin: 0 auto; border-radius: 2px;"></div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr; gap: 30px; margin-bottom: 40px;">
        <!-- Section 1: SDG 3 Alignment -->
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.1); padding: 30px; border-radius: 16px;">
            <div style="flex: 1;">
                <h4 style="margin-top:0; font-weight: 800; font-size: 1.25rem; letter-spacing: -0.02em;">SDG 3: THE WELL-BEING IMPERATIVE</h4>
                <p style="font-size: 0.95rem; line-height: 1.7; opacity: 0.8; margin-bottom: 15px;">
                    This observatory is specifically designed to support <b>UN SDG Target 3.d</b>: <i>"Strengthen the capacity for early warning, risk reduction and management of national and global health risks."</i>
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; background: rgba(128, 128, 128, 0.05); padding: 15px; border-radius: 10px;">
                    <div>
                        <span style="font-size: 0.7rem; font-weight: 800; color: #10b981; text-transform: uppercase;">Direct Health Impact</span>
                        <p style="font-size: 0.8rem; margin: 5px 0 0 0; opacity: 0.7;">Monitoring fatalities and injuries as primary indicators of regional health crises.</p>
                    </div>
                    <div>
                        <span style="font-size: 0.7rem; font-weight: 800; color: #10b981; text-transform: uppercase;">Infrastructure Risk</span>
                        <p style="font-size: 0.8rem; margin: 5px 0 0 0; opacity: 0.7;">Mapping conflict hotspots to identify vulnerable clinics and healthcare access points.</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Section 2: Forensic Mandate -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div style="background: rgba(128, 128, 128, 0.03); padding: 25px; border-radius: 16px; border: 1px solid rgba(128, 128, 128, 0.1);">
                <i class="fas fa-microscope" style="opacity: 0.5; font-size: 1.2rem; margin-bottom: 15px;"></i>
                <h5 style="margin-top: 0; font-weight: 800; font-size: 1rem;">VERIFIED FLOOR PROTOCOL</h5>
                <p style="font-size: 0.85rem; opacity: 0.6; line-height: 1.6; margin-bottom: 0;">We utilize a forensic verification threshold, recording only corroborated data to ensure humanitarian response is based on accurate, confirmed insights.</p>
            </div>
            <div style="background: rgba(128, 128, 128, 0.03); padding: 25px; border-radius: 16px; border: 1px solid rgba(128, 128, 128, 0.1);">
                <i class="fas fa-hand-holding-heart" style="opacity: 0.5; font-size: 1.2rem; margin-bottom: 15px;"></i>
                <h5 style="margin-top: 0; font-weight: 800; font-size: 1rem;">ETHICAL HUMANITARIANISM</h5>
                <p style="font-size: 0.85rem; opacity: 0.6; line-height: 1.6; margin-bottom: 0;">This data is for academic and humanitarian strategic planning. Use for tactical coordination is strictly prohibited to preserve 'Do No Harm' principles.</p>
            </div>
        </div>
        <!-- Section 3: Professional Disclaimer -->
        <div style="padding: 20px 30px; border-radius: 12px; border: 1px dashed rgba(128, 128, 128, 0.3); background: rgba(128, 128, 128, 0.02);">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                <i class="fas fa-circle-info" style="opacity: 0.4; font-size: 0.9rem;"></i>
                <h5 style="opacity: 0.7; margin: 0; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">Hackathon Submission & Disclaimer</h5>
            </div>
            <p style="font-size: 0.8rem; opacity: 0.5; line-height: 1.6; margin-bottom: 0;">
                Developed for the GNEC Hackathon 2026. This observatory transforms raw conflict logs into humanitarian insights to support SDG 3 objectives in crisis-affected regions of Myanmar.
            </p>
        </div>
    </div>
</div>
        """, unsafe_allow_html=True)

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
        "tabs": ["GEOSPATIAL", "TEMPORAL", "ACTORS", "STABILITY", "SDG 3: HEALTH IMPACT", "METHODOLOGY", "POLICY", "RECORDS"],
        "geo_intensity": "Incident Intensity (Density Mapping)",
        "geo_expansion": "Temporal Conflict Expansion (Animation)",
        "temp_freq": "Conflict Frequency and Impact Over Time",
        "actor_impact": "Fatality Impact by Actor Category",
        "actor_comp": "Engagement Composition (Event Types)",
        "actor_net": "ACTOR INTERACTION NETWORK (Conflict Dynamics)",
        "stab_title": "REGIONAL SEVERITY ASSESSMENT",
        "stab_desc": "The **Severity Index** is the ratio of fatalities to total conflict events. A higher score indicates areas where kinetic engagements are more lethal. Use this to distinguish between high-frequency low-impact areas and high-lethality conflict zones.",
        "health_title": "SDG 3: CONFLICT-INDUCED HEALTH IMPACTS",
        "health_desc": "Incidents impacting medical infrastructure, healthcare staff, and human well-being. This analysis uses an NLP engine to extract healthcare-related narratives (Hospital, Clinic, Medical, etc.) from event notes.",
        "records_title": "DATA RECORDS EXPLORER",
        "records_desc": "Filtered incident logs based on current parameters.",
        "tab_explanations": {
            "GEOSPATIAL": "Overlays general conflict density (red) with specific health-impacting incidents (green). The animation shows how conflict has expanded geographically over time.",
            "TEMPORAL": "Tracks the rhythm of conflict. Peaks in the line chart indicate surges in violence. The keyword chart uses NLP to identify common narrative themes.",
            "ACTORS": "Identifies the groups involved. The network map visualizes interactions between actors to reveal the underlying power dynamics of the conflict.",
            "STABILITY": "Ranks regions by lethality using the Severity Index (Fatalities ÷ Events). This distinguishes high-frequency areas from high-lethality 'Red Zones'.",
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
            "thresholds": "**Interpreting Scores:** A score > 1.0 indicates that, on average, every single conflict event in that region results in at least one death, signaling a high-intensity combat zone."
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
            "extraction": "**NLP Extraction:** This tab filters for incidents impacting direct health (hospitals, medical staff) and systemic well-being (sexual violence, arrests, abductions, and looting).",
            "impact": "**Humanitarian Disruption:** Use this to assess how kinetic engagements are degrading both physical health infrastructure and the broader social well-being of civilians."
        },
        "sdg3_logic": {
            "title": "Data Logic: Why 15,000+ SDG 3 Incidents?",
            "p1": "Users may notice that the number of **SDG 3 Incidents** is lower than the total **Fatalities**. This is statistically logical:",
            "item1": "**Metric Difference:** Fatalities represent a count of **individuals** lost, while SDG 3 Incidents represent a count of **specific events** (e.g., one hospital bombing, one mass arrest).",
            "item2": "**Strategic Focus:** While thousands die in remote jungle battles (Military vs. EAOs), this observatory only flags an event as an 'SDG 3 Incident' if it directly impacts civilian health infrastructure or systemic social well-being (e.g., arrests, looting, or healthcare disruption).",
            "item3": "**Humanitarian Collapse:** The ratio of ~15,000 humanitarian incidents to ~77,000 deaths illustrates a dual-crisis: a high-lethality conventional war occurring simultaneously with a systemic campaign against the social and medical foundations of the civilian population."
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
        }
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
        "tabs": ["ပထဝီဝင်အနေအထား", "အချိန်ကာလ", "ပါဝင်ပတ်သက်သူများ", "တည်ငြိမ်မှု", "ကျန်းမာရေးသက်ရောက်မှု (SDG 3)", "လုပ်ထုံးလုပ်နည်း", "မူဝါဒ", "မှတ်တမ်းများ"],
        "geo_intensity": "ဖြစ်ရပ်ပြင်းအား (သိပ်သည်းဆပြမြေပုံ)",
        "geo_expansion": "ပဋိပက္ခနယ်မြေကျယ်ပြန့်လာမှု (အချိန်နှင့်အမျှ)",
        "temp_freq": "ပဋိပက္ခအကြိမ်ရေနှင့် သက်ရောက်မှု (အချိန်နှင့်အမျှ)",
        "actor_impact": "အဖွဲ့အစည်းအလိုက် သေဆုံးမှုသက်ရောက်မှု",
        "actor_comp": "ဖြစ်ရပ်အမျိုးအစားအလိုက် ပါဝင်မှု",
        "actor_net": "အဖွဲ့အစည်းများအကြား အပြန်အလှန်ဆက်နွယ်မှု (ပဋိပက္ခလှုပ်ရှားမှုများ)",
        "stab_title": "ဒေသအလိုက် ပြင်းထန်မှုအကဲဖြတ်ခြင်း",
        "stab_desc": "**ပြင်းထန်မှုညွှန်းကိန်း** သည် သေဆုံးမှုနှင့် ဖြစ်ရပ်အရေအတွက် အချိုးဖြစ်သည်။ ဤညွှန်းကိန်းမြင့်မားခြင်းသည် ထိုဒေသရှိ ပဋိပက္ခများတွင် အသက်အန္တရာယ် ပိုမိုပြင်းထန်ကြောင်း ဖော်ပြသည်။",
        "health_title": "SDG 3: ပဋိပက္ခကြောင့် ကျန်းမာရေးအပေါ်သက်ရောက်မှုများ",
        "health_desc": "ဆေးရုံ၊ ဆေးခန်း၊ ကျန်းမာရေးဝန်ထမ်းများနှင့် လူမှုဘဝတည်ငြိမ်မှုအပေါ် ထိခိုက်စေသော ဖြစ်ရပ်များ။ ဤခွဲခြမ်းစိတ်ဖြာမှုသည် အဖြစ်အပျက်မှတ်တမ်းများမှ ကျန်းမာရေးဆိုင်ရာ အချက်အလက်များကို (NLP) နည်းပညာဖြင့် ထုတ်ယူဖော်ပြခြင်းဖြစ်သည်။",
        "records_title": "ဒေတာမှတ်တမ်းများ ရှာဖွေခြင်း",
        "records_desc": "ရွေးချယ်ထားသော ကန့်သတ်ချက်များအပေါ် အခြေခံသည့် ဖြစ်ရပ်မှတ်တမ်းများ",
        "tab_explanations": {
            "GEOSPATIAL": "ပဋိပက္ခပြင်းထန်မှု (အနီရောင်) နှင့် ကျန်းမာရေးထိခိုက်မှု (အစိမ်းရောင်) ကို ပေါင်းစပ်ပြသထားသည်။ အချိန်နှင့်အမျှ ပဋိပက္ခကျယ်ပြန့်လာမှုကိုလည်း ကြည့်ရှုနိုင်သည်။",
            "TEMPORAL": "ပဋိပက္ခဖြစ်ပွားမှုအရှိန်ကို ခြေရာခံသည်။ မြင်းကွေးဇယားရှိ အတက်အကျများသည် အကြမ်းဖက်မှု မြင့်တက်လာမှုကို ဖော်ပြပြီး စကားလုံးဇယားသည် အဓိကအကြောင်းအရာများကို NLP ဖြင့် ဖော်ပြသည်။",
            "ACTORS": "ပါဝင်ပတ်သက်သူများကို ခွဲခြားပြသသည်။ ကွန်ရက်မြေပုံသည် အဖွဲ့အစည်းများအကြား အပြန်အလှန်ဆက်နွယ်မှုနှင့် အားပြိုင်မှုများကို ဖော်ပြသည်။",
            "STABILITY": "ဒေသအလိုက် အသက်အန္တရာယ်ပြင်းထန်မှုကို တွက်ချက်ပြသသည်။ ၎င်းသည် ဖြစ်ရပ်အရေအတွက်ထက် သေဆုံးမှုနှုန်းမြင့်မားသည့် 'ပြင်းထန်ဇုန်' များကို ခွဲခြားသိမြင်စေသည်။",
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
            "extraction": "**NLP စနစ်ဖြင့် ထုတ်ယူခြင်း-** ဤနေရာတွင် တိုက်ရိုက်ကျန်းမာရေး (ဆေးရုံ၊ ကျန်းမာရေးဝန်ထမ်း) နှင့် အခြေခံလူမှုဘဝတည်ငြိမ်မှု (လိင်ပိုင်းဆိုင်ရာအကြမ်းဖက်မှု၊ ဖမ်းဆီးမှု၊ ပြန်ပေးဆွဲမှု နှင့် လုယက်မှု) ကို ထိခိုက်စေသောဖြစ်ရပ်များကို စစ်ထုတ်ပြသထားသည်။",
            "impact": "**လူသားချင်းစာနာမှုဆိုင်ရာ ထိခိုက်မှု-** တိုက်ရိုက်ပဋိပက္ခများကြောင့် ပြည်သူ့ကျန်းမာရေးအဆောက်အအုံများသာမက အရပ်သားများ၏ ဘေးကင်းလုံခြုံရေးနှင့် လူမှုဘဝတည်ငြိမ်မှု မည်သို့ပျက်စီးနေသည်ကို ဆန်းစစ်နိုင်သည်။"
        },
        "sdg3_logic": {
            "title": "ဒေတာဆိုင်ရာ ရှင်းလင်းချက်- SDG 3 ဖြစ်စဉ် ၁၅,၀၀၀ ကျော် ဖြစ်ပွားရခြင်း အကြောင်းရင်း",
            "p1": "စုစုပေါင်းသေဆုံးမှုအရေအတွက်ထက် **SDG 3 ဖြစ်စဉ်များ** က ပိုနည်းနေသည်ကို အသုံးပြုသူများ သတိပြုမိနိုင်ပါသည်။ ၎င်းမှာ အောက်ပါအချက်များကြောင့် ဖြစ်သည်-",
            "item1": "**တိုင်းတာပုံကွာခြားချက်-** သေဆုံးမှုမှာ **လူဦးရေ** ကို ရေတွက်ခြင်းဖြစ်ပြီး SDG 3 ဖြစ်စဉ်မှာ **ဖြစ်ရပ်** (ဥပမာ - ဆေးရုံဗုံးကြဲခံရမှု ၁ ကြိမ်၊ အစုလိုက်အပြုံလိုက် ဖမ်းဆီးမှု ၁ ကြိမ်) ကို ရေတွက်ခြင်းဖြစ်သည်။",
            "item2": "**မဟာဗျူဟာမြောက် အဓိကထားမှု-** တောတွင်းတိုက်ပွဲများတွင် လူထောင်ပေါင်းများစွာ သေဆုံးနိုင်သော်လည်း ဤစောင့်ကြည့်ရေးစနစ်သည် အရပ်သားကျန်းမာရေးနှင့် လူမှုဘဝတည်ငြိမ်မှုကို (ဥပမာ- ဖမ်းဆီးမှု၊ လုယက်မှု၊ ဆေးကုသမှုအဟန့်အတား) တိုက်ရိုက်ထိခိုက်မှသာ SDG 3 ဖြစ်စဉ်အဖြစ် သတ်မှတ်သည်။",
            "item3": "**လူသားချင်းစာနာမှုဆိုင်ရာ ပျက်သုဉ်းမှု-** သေဆုံးသူ ၇၇,၀၀၀ ကျော်နှင့် လူသားချင်းစာနာမှုဖြစ်စဉ် ၁၅,၀၀၀ ကျော်၏ အချိုးအစားမှာ ပြင်းထန်သောစစ်ပွဲနှင့်အတူ အရပ်သားများ၏ လူမှုဘဝနှင့် ကျန်းမာရေးစနစ်ကို စနစ်တကျဖျက်ဆီးနေသည့် အကျပ်အတည်းနှစ်ရပ်ကို တပြိုင်နက် ဖော်ပြနေခြင်းဖြစ်သည်။"
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
        }
    }
}

# --- Theme-Aware Professional CSS ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
        display_briefing_gate()
        
        st.markdown("<br>", unsafe_allow_html=True)
        elapsed = time.time() - st.session_state.start_time
        remaining = int(max(0, 5 - elapsed))
        
        _, b_col, _ = st.columns([1, 2, 1])
        with b_col:
            if remaining > 0:
                st.button(f"INITIALIZING SECURE PROTOCOLS ({remaining}S)", disabled=True, key="timer_btn", use_container_width=True)
                time.sleep(1)
                st.rerun()
            else:
                if st.button("AUTHORIZE SYSTEM ACCESS", type="primary", use_container_width=True, key="enter_btn"):
                    st.session_state.gate_passed = True
                    st.rerun()
    st.stop()

# --- Post-Gate CSS Reset ---
st.markdown("<style>[data-testid='stAppViewContainer'] { overflow: auto !important; height: auto !important; position: static !important; } [data-testid='stSidebar'] { display: block !important; } [data-testid='stHeader'] { display: flex !important; }</style>", unsafe_allow_html=True)

# --- Data Engine (SQL & CSV Fallback) ---
@st.cache_data
def load_data():
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
        st.warning(f"Database unavailable or empty, falling back to local files: {e}")

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
        except Exception as e:
            st.warning(f"KaggleHub Cloud fallback failed: {e}")
        
    if not files: return None, None
    
    latest_file = max(files, key=os.path.getmtime)
    file_mod_time = os.path.getmtime(latest_file)
    df = pd.read_csv(latest_file)
    df = df[df['country'] == 'Myanmar']
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df[df['event_date'] >= '2021-02-01']
    df['year_month'] = df['event_date'].dt.strftime('%Y-%m')
    
    # Format update_time for CSV fallback
    update_time = pd.to_datetime(file_mod_time, unit='s').strftime('%Y-%m-%d %H:%M')
    return df, update_time

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
    st.error("Data source missing. Ensure dataset is in /data or Kaggle input folder.")
else:
    # Central Color Map for all Actor Visualizations
    node_color_map = {
        "State Forces": "#ef4444", 
        "Pro-Junta Militia": "#fca5a5", # Lighter red
        "Resistance": "#3b82f6", 
        "EAOs": "#10b981", 
        "Civilians": "#94a3b8", 
        "Protesters": "#f59e0b", 
        "Rioters": "#d97706", # Darker orange
        "Unidentified": "#1e293b", # Very dark
        "Other Groups": "#475569"
    }

    df_raw['actor1_clean'] = df_raw['actor1'].apply(categorize_actor)
    df_raw['actor2_clean'] = df_raw['actor2'].apply(categorize_actor)
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
    st.markdown(f'<p class="sub-header">{L["sub"]} | DATA CURRENT AS OF: {latest_event_date}</p>', unsafe_allow_html=True)

    # --- Pre-calculations ---
    health_hits = extract_health_impacts(df)

    # --- Metrics ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.markdown(f'<div class="metric-card"><i class="fas fa-bullseye metric-icon"></i><div class="metric-content"><div class="metric-label">{L["events"]}</div><div class="metric-value">{len(df):,}</div></div></div>', unsafe_allow_html=True)
    with m_col2: st.markdown(f'<div class="metric-card"><i class="fas fa-skull metric-icon" style="color:#ef4444"></i><div class="metric-content"><div class="metric-label">{L["fatalities"]}</div><div class="metric-value">{int(df["fatalities"].sum()):,}</div></div></div>', unsafe_allow_html=True)

    # SDG 3 Specific Metric
    health_count = health_hits.sum()
    with m_col3: st.markdown(f'<div class="metric-card"><i class="fas fa-house-medical metric-icon" style="color:#10b981"></i><div class="metric-content"><div class="metric-label">SDG 3 Incidents</div><div class="metric-value">{health_count}</div></div></div>', unsafe_allow_html=True)

    with m_col4: st.markdown(f'<div class="metric-card"><i class="fas fa-users metric-icon"></i><div class="metric-content"><div class="metric-label">{L["active_groups"]}</div><div class="metric-value">{df["actor1"].nunique():,} Entities</div></div></div>', unsafe_allow_html=True)

    # --- Analysis Tabs ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(L["tabs"])

    plotly_layout = {"paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)", "font": {"color": "#94a3b8"}}

    with tab1:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['GEOSPATIAL']}")

        # --- Geospatial Interpretation Guide ---
        with st.expander(L["geo_guide"]["title"]):
            st.markdown(f"""
            *   {L["geo_guide"]["intensity"]}
            *   {L["geo_guide"]["expansion"]}
            *   {L["geo_guide"]["sdg3_overlay"]}
            """)

        col1, col2 = st.columns(2)
        with col1:
            st.caption("Humanitarian Conflict Overlay (Heatmap: Fatalities | Points: Health Impacts)")
            
            # 1. Base Layer: Density Heatmap of all fatalities
            fig_heat = px.density_mapbox(
                df, lat='latitude', lon='longitude', z='fatalities', radius=10,
                center=dict(lat=18.5, lon=96), zoom=5, 
                mapbox_style="carto-darkmatter", height=600,
                color_continuous_scale=["#1e293b", "#475569", "#ef4444"], # Grayscale to Red
                opacity=0.7
            )
            
            # 2. Overlay Layer: Scatter points for health-impacting incidents
            # We reuse the health_hits logic from before
            health_overlay = df[health_hits].copy()
            if not health_overlay.empty:
                fig_overlay = px.scatter_mapbox(
                    health_overlay, lat='latitude', lon='longitude',
                    color_discrete_sequence=["#10b981"], # Bright Green for Health
                    hover_name="location",
                    size_max=15
                )
                # Add the health points to the heatmap figure
                for trace in fig_overlay.data:
                    trace.name = "Health Impact"
                    trace.showlegend = True
                    fig_heat.add_trace(trace)

            fig_heat.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, 
                coloraxis_showscale=False,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)")
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        with col2:
            st.caption(L["geo_expansion"])
            df_anim = df.sort_values('event_date')
            fig_anim = px.scatter_mapbox(
                df_anim, 
                lat="latitude", 
                lon="longitude", 
                color="actor1_clean",
                size="fatalities",
                animation_frame="year_month",
                hover_name="location",
                color_discrete_map=node_color_map,
                hover_data={                    "event_date": "|%B %d, %Y", 
                    "event_type": True,
                    "actor1": True,
                    "actor2": True,
                    "fatalities": True,
                    "latitude": False,
                    "longitude": False,
                    "year_month": False
                },
                zoom=5, 
                height=600, 
                mapbox_style="carto-darkmatter"
            )
            fig_anim.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_anim, use_container_width=True)

    with tab2:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['TEMPORAL']}")

        # --- Temporal Interpretation Guide ---
        with st.expander(L["temp_guide"]["title"]):
            st.markdown(f"""
            *   {L["temp_guide"]["frequency"]}
            *   {L["temp_guide"]["keywords"]}
            """)

        st.subheader(L["temp_freq"])
        
        # Prepare monthly stats
        monthly_events = df.resample('ME', on='event_date').size().reset_index(name='event_count')
        monthly_fatalities = df.resample('ME', on='event_date')['fatalities'].sum().reset_index()
        monthly_combined = pd.merge(monthly_events, monthly_fatalities, on='event_date')
        
        fig_line = go.Figure()
        
        # Add Events Trace
        fig_line.add_trace(go.Scatter(
            x=monthly_combined['event_date'], 
            y=monthly_combined['event_count'],
            name="Conflict Incidents",
            mode='lines',
            line=dict(color='#94a3b8', width=2),
            hovertemplate="<b>%{x|%B %Y}</b><br>Incidents: %{y}<extra></extra>"
        ))
        
        # Add Fatalities Trace
        fig_line.add_trace(go.Scatter(
            x=monthly_combined['event_date'], 
            y=monthly_combined['fatalities'],
            name="Verified Fatalities",
            mode='lines',
            line=dict(color='#ef4444', width=2),
            hovertemplate="<b>%{x|%B %Y}</b><br>Fatalities: %{y}<extra></extra>"
        ))
        
        fig_line.update_layout(
            plotly_layout, 
            xaxis_title="", 
            yaxis_title="Volume",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        st.caption(L["keywords_title"])
        kw_df = extract_keywords(df['notes'])
        if not kw_df.empty:
            fig_kw = px.bar(kw_df, x='Frequency', y='Keyword', orientation='h', color='Frequency', color_continuous_scale="Greys")
            fig_kw.update_layout(plotly_layout, yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_kw, use_container_width=True)

    with tab3:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['ACTORS']}")
        c1, c2 = st.columns(2)
        with c1:
            st.caption(L["actor_impact"])
            st.info("Impact is calculated as the sum of fatalities in all events where the category participated (either as Actor 1 or Actor 2).")
            
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
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.caption(L["actor_comp"])
            fig_pie = px.sunburst(df, path=['event_type', 'sub_event_type'], values='fatalities', color_discrete_sequence=["#334155", "#475569", "#64748b", "#94a3b8"])
            fig_pie.update_layout(plotly_layout, margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.info(f"**{selected_lang} Guidance:** Use the dropdown to spotlight an actor. Edge thickness is weighted by total fatalities in those interactions.")
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

            fig_net = go.Figure(data=edge_traces + [node_trace],
                                layout=go.Layout(showlegend=False, hovermode='closest',
                                                 margin=dict(b=0, l=0, r=0, t=0),
                                                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                 yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                 paper_bgcolor='rgba(0,0,0,0)',
                                                 plot_bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_net, use_container_width=True)
        else:
            st.info("Insufficient interaction data for network mapping.")

    with tab4:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['STABILITY']}")
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
        fig_stab = px.bar(stability_df.reset_index(), x='admin1', y='Severity_Index', color='Severity_Index', color_continuous_scale="Reds")
        fig_stab.update_layout(plotly_layout)
        st.plotly_chart(fig_stab, use_container_width=True)

    with tab5:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['SDG 3: HEALTH IMPACT']}")
        st.subheader(L["health_title"])
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
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1:
                st.caption("Geospatial Distribution of Health-Impacting Incidents")
                fig_h_geo = px.scatter_mapbox(
                    health_df, 
                    lat="latitude", 
                    lon="longitude", 
                    color="event_type", 
                    size="fatalities", 
                    hover_name="location", 
                    hover_data={
                        "event_date": "|%B %d, %Y",
                        "admin1": True,
                        "actor1": True,
                        "fatalities": True,
                        "notes": False,
                        "latitude": False,
                        "longitude": False
                    }, 
                    zoom=5, 
                    height=500, 
                    mapbox_style="carto-darkmatter"
                )
                fig_h_geo.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig_h_geo, use_container_width=True)
            
            with h_col2:
                st.caption("Top Affected Regions (Medical Infrastructure)")
                h_stats = health_df.groupby('admin1').size().reset_index(name='count').sort_values('count', ascending=False)
                fig_h_bar = px.bar(h_stats, x='count', y='admin1', orientation='h', color='count', color_continuous_scale="Viridis")
                fig_h_bar.update_layout(plotly_layout, yaxis={'categoryorder':'total ascending'}, showlegend=False)
                st.plotly_chart(fig_h_bar, use_container_width=True)

            st.markdown("---")
            
            # --- Health Vulnerability Trend & Scorecard ---
            v_col1, v_col2 = st.columns([1, 1])
            with v_col1:
                st.caption("Temporal Trend: Health-Impacting Incidents")
                h_trend = health_df.set_index('event_date').resample('M').size().reset_index(name='count')
                fig_h_trend = px.area(h_trend, x='event_date', y='count', color_discrete_sequence=['#10b981'])
                fig_h_trend.update_layout(plotly_layout, xaxis_title="", yaxis_title="Events / Month")
                st.plotly_chart(fig_h_trend, use_container_width=True)
            
            with v_col2:
                st.caption("Regional Health Vulnerability Scorecard")
                # Score = (Health Incidents * 0.7) + (Fatalities * 0.3)
                v_score = health_df.groupby('admin1').agg({'event_id_cnty': 'count', 'fatalities': 'sum'}).rename(columns={'event_id_cnty': 'health_events'})
                v_score['Score'] = ((v_score['health_events'] * 0.7) + (v_score['fatalities'] * 0.3)).round(1)
                v_score = v_score.sort_values('Score', ascending=False).head(5)
                st.dataframe(v_score, use_container_width=True)

            st.markdown("---")
            
            # --- Humanitarian Spotlight Explorer ---
            st.markdown("### <i class='fas fa-magnifying-glass-location' style='color:#10b981'></i> HUMANITARIAN SPOTLIGHT EXPLORER", unsafe_allow_html=True)
            st.caption("Select an incident from the list to reveal the full verified forensic narrative and health impact details.")
            
            # Prepare options for selection
            health_df['display_name'] = health_df['event_date'].dt.strftime('%Y-%m-%d') + " | " + health_df['location'] + " (" + health_df['event_type'] + ")"
            selected_incident_name = st.selectbox("Search Incident Log", health_df['display_name'].tolist())
            
            selected_row = health_df[health_df['display_name'] == selected_incident_name].iloc[0]
            
            # Display the Spotlight Card
            st.markdown(f"""
            <div class="spotlight-card">
                <div class="spotlight-header">
                    <div class="spotlight-title">{selected_row['location']} Engagement</div>
                    <div class="spotlight-meta">{selected_row['event_date'].strftime('%B %d, %Y')} | {selected_row['admin1']} Region</div>
                </div>
                <div class="spotlight-note">
                    "{selected_row['notes']}"
                </div>
                <div class="spotlight-grid">
                    <div class="spotlight-stat">
                        <div class="spotlight-stat-label">Primary Actor</div>
                        <div class="spotlight-stat-value">{selected_row['actor1']}</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="spotlight-stat-label">Secondary Actor</div>
                        <div class="spotlight-stat-value">{selected_row['actor2'] if pd.notna(selected_row['actor2']) else 'None Reported'}</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="spotlight-stat-label">Event Classification</div>
                        <div class="spotlight-stat-value">{selected_row['event_type']}</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="spotlight-stat-label">Fatalities</div>
                        <div class="spotlight-stat-value" style="color:#ef4444">{int(selected_row['fatalities'])} Verified</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("View Full Filtered Health Records (Tabular)"):
                st.dataframe(health_df[['event_date', 'location', 'notes']].sort_values('event_date', ascending=False), use_container_width=True)
        else:
            st.info("No medical-impact incidents detected in current filtered data.")

    with tab6:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['METHODOLOGY']}")

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
        ### 1. Big Data Architecture & ETL Pipeline
        This observatory utilizes a modern data engineering pipeline designed to handle the Volume, Velocity, and Variety of conflict logs. The system employs a hybrid ingestion protocol (Local + Cloud):
        - **Extraction:** The framework monitors three primary sources:
            1. **Local CSV/DB:** High-performance local access for offline research.
            2. **Kaggle Input:** Automated detection for Kaggle Notebook environments.
            3. **Kaggle Cloud (kagglehub):** Dynamic remote ingestion from the `acled-dataset-for-myanmar` repository for cloud-native deployment.
        - **Transformation:** Raw logs are processed using Python (Pandas/NumPy). This includes cleaning non-standard date formats, filtering by sovereign boundaries (Myanmar), and isolating the post-coup temporal scope (Post-Feb 1, 2021).
        - **Ingestion:** Data is optimized for real-time visualization by pre-calculating monthly aggregates and administrative level intensities.

        ### 2. Semantic Actor Normalization Protocol
        Conflict dynamics in Myanmar are characterized by extreme fragmentation, with hundreds of localized resistance groups and ethnic armed organizations (EAOs). To perform meaningful spatiotemporal analysis, this framework applies a Semantic Clustering Logic:
        - **State Forces:** Aggregates all reports involving the Myanmar Military (Tatmadaw) and Police.
        - **Resistance:** Clusters hundreds of localized 'People's Defence Forces' (PDFs) and Local Defense Forces (LDFs).
        - **EAOs:** Categorizes long-standing Ethnic Armed Organizations (e.g., KNU, KIA, AA) based on historical acronyms and geographic presence.
        - **Civilians & Protesters:** Isolated to track the humanitarian impact and non-kinetic resistance movements.

        ### 3. Spatiotemporal Analytical Models
        The dashboard utilizes two primary models for stability assessment:
        - **Intensity Mapping:** Using Gaussian kernels to calculate incident density, highlighting "hotzones" where kinetic engagements are most concentrated.
        - **Temporal Resampling:** Using Month End (ME) intervals to smooth daily reporting noise and reveal systemic shifts in conflict velocity.

        ### 4. Analytical Limitations & Considerations
        This framework is designed for strategic humanitarian analysis, and users should be aware of the following data nuances:
        - **Geospatial Centroiding:** Incident coordinates often represent the center of a township or village ('centroid'), not a precise tactical location. The maps therefore indicate **regional clusters of risk** rather than exact GPS points.
        - **NLP Keyword Logic:** The SDG 3 engine flags events by matching keywords (e.g., "hospital," "clinic"). It reliably identifies "Health-Proximity Incidents" but does not distinguish context (e.g., "hospital hit" vs. "security near hospital").
        - **Reporting Lag:** Data for the most recent 7-14 days may be incomplete pending source verification. A downward trend in the latest period often reflects this **verification delay**, not a definitive decrease in conflict.
        - **Severity Index Nuance:** The Severity Index is sensitive to low event counts. A region with one event and five fatalities will rank higher than a region with 20 events and nine fatalities. It is a measure of **lethality, not necessarily overall stability.**
        """)

    with tab7:
        st.info(f"**{selected_lang} Guidance:** {L['tab_explanations']['POLICY']}")

        # --- Policy Interpretation Guide ---
        with st.expander(L["policy_guide"]["title"]):
            st.markdown(f"""
            *   {L["policy_guide"]["neutrality"]}
            *   {L["policy_guide"]["do_no_harm"]}
            """)

        st.markdown('<p class="main-header">ANALYTICAL POLICY & ETHICAL FRAMEWORK</p>', unsafe_allow_html=True)
        st.markdown("""
        ### 1. Statement of Institutional Neutrality
        The Myanmar Conflict Observatory is an independent, non-partisan research project. It is not affiliated with, funded by, or coordinated with any political party, rebel administration, or state security apparatus. Our mission is strictly academic: to provide a transparent, data-driven framework for assessing regional stability and humanitarian impact.

        ### 2. The 'Fatality Gap' & Data Veracity Protocol
        - **Conservative Verification (ACLED):** This framework utilizes ACLED data, which prioritizes a high verification threshold. 
        - **Observation Protocol:** We treat the figures presented here as a Verified Floor—the minimum confirmed human cost of the conflict. In regions subject to internet blackouts, real figures are likely significantly higher than reported.

        ### 3. The 'Do No Harm' Ethical Mandate
        - **Strategic vs. Tactical Utility:** Data is presented in aggregate form and delayed by source reporting cycles. This observatory is strictly intended for strategic research. 
        - **Protection of Local Reporters:** All coordinates and narrative notes are handled according to established safety protocols to prevent the identification of local informants.

        ### 4. Comprehensive Disclaimer of Liability
        - **Data Integrity:** While we employ rigorous Big Data engineering techniques, the authors make no guarantees regarding the absolute accuracy or completeness of the source material.
        - **Usage Risk:** No party involved in the development of this observatory shall be held liable for any damages resulting from the use or interpretation of these visualizations.
        """)


