import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

# --- Page Configuration ---
st.set_page_config(
    page_title="Myanmar Conflict Observatory",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme-Aware Minimalist CSS ---
st.markdown("""
    <style>
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 24px;
        border-radius: 4px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-color);
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-color);
    }
    .main-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 0.875rem;
        color: var(--text-color);
        opacity: 0.6;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #ef4444;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Data Engine ---
@st.cache_data
def load_data():
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir): return None, None
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not files: return None, None
    
    latest_file = max(files, key=os.path.getmtime)
    file_mod_time = os.path.getmtime(latest_file)
    
    df = pd.read_csv(latest_file)
    df = df[df['country'] == 'Myanmar']
    df['event_date'] = pd.to_datetime(df['event_date'])
    df = df[df['event_date'] >= '2021-02-01']
    df['year_month'] = df['event_date'].dt.strftime('%Y-%m')
    
    return df, file_mod_time

def categorize_actor(actor_name):
    if pd.isna(actor_name): return "Unidentified"
    name = str(actor_name).lower()
    if 'military forces of myanmar' in name or 'police forces of myanmar' in name:
        return 'State Forces'
    elif 'pdf' in name or "people's defence force" in name or 'local defense force' in name:
        return 'Resistance'
    elif 'protesters' in name:
        return 'Protesters'
    elif 'civilians' in name:
        return 'Civilians'
    elif any(eao in name for eao in ['knu', 'kia', 'tnla', 'mndaa', 'rcss', 'knpp', 'cnp', 'aa ']):
        return 'EAOs'
    else:
        return 'Other Groups'

df_raw, mod_timestamp = load_data()

if df_raw is None:
    st.error("Data source error: Ensure dataset is in /data directory.")
else:
    df_raw['actor1_clean'] = df_raw['actor1'].apply(categorize_actor)
    latest_event_date = df_raw['event_date'].max().strftime('%B %d, %Y')
    update_time = pd.to_datetime(mod_timestamp, unit='s').strftime('%Y-%m-%d %H:%M')

    # --- Navigation ---
    with st.sidebar:
        st.markdown("### Parameters")
        min_date, max_date = df_raw['event_date'].min().date(), df_raw['event_date'].max().date()
        date_range = st.date_input("Analysis Period", [min_date, max_date])
        
        regions = ["All Regions"] + sorted(list(df_raw['admin1'].unique()))
        selected_region = st.selectbox("Focus Area", regions)
        
        st.markdown("---")
        st.markdown("### Data Currency")
        st.markdown(f"**Latest Event:**  \n{latest_event_date}")
        st.markdown(f"**Source Updated:**  \n{update_time}")
        
        st.markdown("---")
        st.caption("Myanmar Conflict Observatory v1.0")
        st.caption("Data Source: ACLED Project")

    # --- Filtering ---
    df = df_raw.copy()
    if len(date_range) == 2:
        df = df[(df['event_date'].dt.date >= date_range[0]) & (df['event_date'].dt.date <= date_range[1])]
    if selected_region != "All Regions":
        df = df[df['admin1'] == selected_region]

    # --- Main Interface ---
    st.markdown('<p class="main-header">Myanmar Conflict Observatory</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Post-Coup Analytical Framework | Data current as of: {latest_event_date}</p>', unsafe_allow_html=True)

    # --- Metrics ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Events</div><div class="metric-value">{len(df):,}</div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Reported Fatalities</div><div class="metric-value">{int(df["fatalities"].sum()):,}</div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Townships Affected</div><div class="metric-value">{df["admin2"].nunique()}</div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Active Groups</div><div class="metric-value">{df["actor1"].nunique()}</div></div>', unsafe_allow_html=True)

    # --- Analysis Tabs ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Geospatial Analysis", "Temporal Stability", "Actor Dynamics", "Data Records"])

    plotly_layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "gray"}
    }

    with tab1:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.caption("Incident Intensity (Density)")
            fig_heat = px.density_mapbox(
                df, lat='latitude', lon='longitude', z='fatalities', 
                radius=8, center=dict(lat=18.5, lon=96), zoom=5,
                mapbox_style="carto-darkmatter", height=600,
                color_continuous_scale=["#334155", "#ef4444"]
            )
            fig_heat.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_m2:
            st.caption("Temporal Conflict Spread")
            df_anim = df.sort_values('event_date')
            fig_anim = px.scatter_mapbox(
                df_anim, lat="latitude", lon="longitude", color="actor1_clean",
                size="fatalities", animation_frame="year_month",
                zoom=5, height=600, mapbox_style="carto-darkmatter",
                color_discrete_map={
                    "State Forces": "#ef4444", 
                    "Resistance": "#3b82f6",
                    "EAOs": "#10b981",
                    "Civilians": "#94a3b8",
                    "Protesters": "#f59e0b",
                    "Other Groups": "#475569"
                }
            )
            fig_anim.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_anim, use_container_width=True)

    with tab2:
        st.caption("Conflict Frequency and Impact Over Time")
        monthly = df.resample('ME', on='event_date').size().reset_index(name='count')
        monthly_fat = df.resample('ME', on='event_date')['fatalities'].sum().reset_index()
        fig_line = px.line(monthly, x='event_date', y='count', color_discrete_sequence=["#94a3b8"])
        fig_line.add_scatter(x=monthly_fat['event_date'], y=monthly_fat['fatalities'], 
                            name="Fatalities", mode='lines', line=dict(color='#ef4444', width=1))
        fig_line.update_layout(plotly_layout, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Fatalities by Group Category")
            actor_stats = df.groupby('actor1_clean')['fatalities'].sum().reset_index().sort_values('fatalities')
            fig_bar = px.bar(actor_stats, x='fatalities', y='actor1_clean', 
                            orientation='h', color_discrete_sequence=["#ef4444"])
            fig_bar.update_layout(plotly_layout, xaxis_title="Reported Fatalities", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.caption("Event Type Distribution")
            fig_pie = px.sunburst(df, path=['event_type', 'sub_event_type'], values='fatalities',
                                 color_discrete_sequence=["#334155", "#475569", "#64748b", "#94a3b8"])
            fig_pie.update_layout(plotly_layout, margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab4:
        st.caption("Complete Incident Records")
        st.dataframe(df[['event_date', 'event_type', 'actor1', 'actor2', 'admin1', 'location', 'fatalities', 'notes']],
                    use_container_width=True, height=600)
