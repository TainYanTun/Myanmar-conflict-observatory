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
from datetime import datetime
from dotenv import load_dotenv
from src.processing import categorize_actor, extract_keywords, extract_health_impacts

load_dotenv()
DB_URL = os.getenv("DB_URL")

def display_briefing_gate(L):
    st.markdown(f"""
<div style="padding: 50px; border-radius: 24px; background: rgba(128, 128, 128, 0.02); border: 1px solid rgba(128, 128, 128, 0.2); backdrop-filter: blur(20px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); font-family: 'Inter', sans-serif;">
    <div style="text-align: center; margin-bottom: 40px;">
        <div style="display: inline-block; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 6px 16px; border-radius: 99px; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 20px; border: 1px solid rgba(10, 185, 129, 0.2);">{L['gate_sdg3_focus']}</div>
        <h1 style="font-weight: 900; letter-spacing: -0.05em; margin-bottom: 10px; font-size: 3rem;">{L['gate_title']}</h1>
    </div>
</div>
        """, unsafe_allow_html=True)

st.set_page_config(page_title="Myanmar Conflict Observatory", layout="wide")

LANG_DICT = {
    "English": {
        "title": "MYANMAR CONFLICT OBSERVATORY",
        "sub": "ANALYTICAL FRAMEWORK FOR STABILITY ASSESSMENT",
        "events": "Total Events",
        "fatalities": "Fatalities (Verified)",
        "params": "PARAMETERS",
        "period": "Analysis Period",
        "area": "Focus Area",
        "currency": "DATA CURRENCY",
        "latest": "Latest Event",
        "update": "System Update",
        "keywords_title": "Top Narrative Keywords",
        "tabs": ["GEOSPATIAL", "TEMPORAL", "ACTORS", "STABILITY", "SDG 3: HEALTH IMPACT", "METHODOLOGY", "POLICY", "RECORDS"],
        "temp_freq": "Conflict Frequency and Impact Over Time",
        "actor_impact": "Fatality Impact by Actor Category",
        "actor_comp": "Engagement Composition (Event Types)",
        "actor_net": "ACTOR INTERACTION NETWORK",
        "stab_title": "REGIONAL SEVERITY ASSESSMENT",
        "stab_desc": "The **Severity Index** is the ratio of fatalities to total conflict events.",
        "health_title": "SDG 3: HEALTH IMPACTS",
        "health_desc": "Incidents impacting medical infrastructure.",
        "records_title": "DATA RECORDS",
        "records_desc": "Filtered logs.",
        "gate_title": "HUMANITARIAN MISSION BRIEFING",
        "gate_sub": "Crisis Monitoring",
        "gate_sdg3_focus": "SDG 3 FOCUS",
        "tab_explanations": {
            "GEOSPATIAL": "Heatmap of conflict density.",
            "TEMPORAL": "Conflict rhythms.",
            "ACTORS": "Network of groups.",
            "STABILITY": "Severity index.",
            "SDG 3: HEALTH IMPACT": "Healthcare incidents.",
            "METHODOLOGY": "Tech stack.",
            "POLICY": "Ethics.",
            "RECORDS": "Raw logs."
        }
    }
}
L = LANG_DICT["English"]
high_res_config = {'toImageButtonOptions': {'format': 'png', 'scale': 3}}
plotly_layout = {"paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)", "font": {"color": "#94a3b8"}}

# Simplified data load and UI logic for demonstration
# ... (Assuming df is loaded correctly via your load_data() function)
# I am providing the structure you requested for the tabs

df, update_time = load_data()
if df is not None:
    health_hits = extract_health_impacts(df)
    
    st.markdown(f'<p class="main-header">{L["title"]}</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(L["tabs"])
    
    with tabs[0]: # GEOSPATIAL
        st.subheader("Geospatial Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.density_mapbox(df, lat='latitude', lon='longitude', z='fatalities', zoom=5, mapbox_style="carto-darkmatter"), width=1000, config=high_res_config)
        with col2:
            st.plotly_chart(px.scatter_mapbox(df, lat='latitude', lon='longitude', zoom=5, mapbox_style="carto-darkmatter"), width=1000, config=high_res_config)

    with tabs[1]: # TEMPORAL
        st.subheader("Temporal Trends")
        st.plotly_chart(go.Figure(data=[go.Scatter(x=df.groupby('event_date').size().index, y=df.groupby('event_date').size().values)]), width=1000, config=high_res_config)

    with tabs[2]: # ACTORS
        st.subheader("Actor Interactions")
        # Actor impact chart
        actor_stats = pd.concat([df.groupby('actor1_clean')['fatalities'].sum().reset_index().rename(columns={'actor1_clean': 'actor'}), df.groupby('actor2_clean')['fatalities'].sum().reset_index().rename(columns={'actor2_clean': 'actor'})]).groupby('actor')['fatalities'].sum().reset_index()
        fig_bar = px.bar(actor_stats, x='fatalities', y='actor', orientation='h')
        st.plotly_chart(fig_bar, width=1000, config=high_res_config)

    with tabs[3]: # STABILITY
        st.subheader("Regional Risk Matrix")
        risk_matrix = df.groupby('admin1').agg({'event_id_cnty': 'count','fatalities': 'sum'}).rename(columns={'event_id_cnty': 'Frequency'})
        risk_matrix['Lethality'] = (risk_matrix['fatalities'] / risk_matrix['Frequency']).round(2)
        fig_matrix = px.scatter(risk_matrix.reset_index(), x='Frequency', y='Lethality', text='admin1', size='fatalities', color='Lethality')
        st.plotly_chart(fig_matrix, width=1000, config=high_res_config)

    with tabs[4]: # SDG 3
        st.subheader("SDG 3 Health Impact")

    with tabs[5]: # METHODOLOGY
        st.markdown("## Methodology")

    with tabs[6]: # POLICY
        st.markdown("## Policy")

    with tabs[7]: # RECORDS
        st.dataframe(df, width=1000)
