"""
HICE Detection Framework — Research Dashboard
FastAPI backend with server-rendered HTML + Plotly.js frontend.
Data sourced from Supabase PostgreSQL with CSV fallback.
"""
import os, glob, json, re, pathlib
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import plotly
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine, text

from src.processing import (
    extract_health_impacts,
    classify_hice_type,
    categorize_actor,
    extract_keywords,
    clean_conflict_data,
)
from src.hice_detector import (
    HEALTH_TERMS, TARGETING_PATTERN, ACTION_PHRASES,
    SOFT_HEALTH_PATTERN, HEALTH_INFRA, ATTACK_TERMS,
    PROXIMITY_WINDOW,
    ENUMERATION_FP_PATTERN, ENUMERATION_FP_NEGATIVE,
    HOSPITAL_BYSTANDER_PATTERN, HOSPITAL_BYSTANDER_NEGATIVE,
)

HERE = pathlib.Path(__file__).parent

app = FastAPI(title="HICE Detection Framework")
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")
templates = Jinja2Templates(directory=str(HERE / "templates"))

HICE_COLORS = {
    "infrastructure_damage": "#2563eb",
    "access_disruption": "#7c3aed",
    "personnel_targeting": "#dc2626",
    "humanitarian_disruption": "#64748b",
    "systemic_attack": "#0891b2",
}
HICE_LABELS = {
    "infrastructure_damage": "Infrastructure Damage",
    "access_disruption": "Access Disruption",
    "personnel_targeting": "Personnel Targeting",
    "humanitarian_disruption": "Humanitarian Disruption",
    "systemic_attack": "Systemic Attack",
}


def fig_to_json(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


# ── Load & process data once at startup ──────────────────────────────
def load_data_from_supabase():
    """Try loading data from Supabase PostgreSQL via DB_URL env var."""
    db_url = os.environ.get("DB_URL")
    if not db_url:
        return None
    table = os.environ.get("DB_TABLE", "conflict_events")
    try:
        engine = create_engine(db_url, connect_args={"sslmode": "require"})
        with engine.connect() as conn:
            df = pd.read_sql(text(f"SELECT * FROM {table}"), conn)
        if df.empty:
            return None
        df = clean_conflict_data(df)
        return df
    except Exception as e:
        print(f"Supabase connection failed: {e}")
        return None


def load_data():
    df = load_data_from_supabase()
    if df is not None:
        return df
    paths = [
        HERE / "data",
        HERE / "notebooks" / "data",
    ]
    files = []
    for p in paths:
        files.extend(glob.glob(str(p / "*.csv")))
    if not files:
        return None
    preferred = [f for f in files if os.path.basename(f) == "myanmar_conflict_clean.csv"]
    if preferred:
        files = preferred
    else:
        files.sort(key=os.path.getmtime, reverse=True)
    for f in files:
        try:
            df = pd.read_csv(f)
            df = clean_conflict_data(df)
            return df
        except Exception:
            continue
    return None


df = load_data()
if df is None:
    raise RuntimeError(
        "No conflict data found. Set DB_URL for Supabase PostgreSQL or place a cleaned ACLED CSV in data/"
    )

hice_mask = extract_health_impacts(df)
df["is_hice"] = hice_mask
df["hice_type"] = "none"
if hice_mask.any():
    hice_idx = df[hice_mask].index
    df.loc[hice_idx, "hice_type"] = classify_hice_type(df.loc[hice_idx])

hice_df = df[hice_mask].copy()
total_events = len(df)
total_hice = len(hice_df)
date_min = df["event_date"].min()
date_max = df["event_date"].max()


# ── Pre-compute all chart data ───────────────────────────────────────
def compute_overview():
    if hice_df.empty:
        return None, None, None, None

    cat_counts = hice_df["hice_type"].value_counts()
    fig_pie = go.Figure(
        go.Pie(
            labels=[HICE_LABELS.get(c, c) for c in cat_counts.index],
            values=cat_counts.values,
            marker=dict(colors=[HICE_COLORS.get(c, "#6b7280") for c in cat_counts.index]),
            hole=0.45,
            textposition="outside",
            textinfo="percent+label",
            hovertemplate="%{label}<br>%{value} incidents (%{percent})<extra></extra>",
        )
    )
    fig_pie.update_layout(
        title=dict(text="HICE Classification", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=400,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        legend=dict(orientation="h", y=-0.1),
        annotations=[dict(text=str(total_hice), x=0.5, y=0.5, font_size=28, font_color="#1f2937", showarrow=False)],
    )

    kw = extract_keywords(hice_df["notes"], top_n=12)
    fig_kw = None
    if not kw.empty:
        fig_kw = px.bar(
            kw, x="Frequency", y="Keyword", orientation="h",
            color_discrete_sequence=["#2563eb"],
        )
        fig_kw.update_layout(
            title=dict(text="Top Narrative Keywords", font=dict(size=15, weight=600, color="#1f2937"), x=0),
            height=400,
            margin=dict(t=50, b=20, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
            yaxis=dict(categoryorder="total ascending", showgrid=False),
            xaxis=dict(showgrid=False),
        )

    actor_counts = hice_df["actor1"].apply(categorize_actor).value_counts()
    fig_actor = px.bar(
        x=actor_counts.values, y=actor_counts.index, orientation="h",
        color=actor_counts.index,
        color_discrete_map={
            "State Forces": "#2563eb", "Pro-Junta Militia": "#dc2626",
            "Resistance": "#059669", "EAOs": "#7c3aed",
            "Civilians": "#d97706", "Protesters": "#0891b2",
            "Rioters": "#ea580c", "Unidentified": "#9ca3af",
            "Other Groups": "#64748b",
        },
    )
    fig_actor.update_layout(
        title=dict(text="Primary Actor Categories", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=350,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )

    evt_counts = hice_df["event_type"].value_counts()
    fig_evt = px.bar(
        x=evt_counts.values, y=evt_counts.index, orientation="h",
        color_discrete_sequence=["#2563eb"],
    )
    fig_evt.update_layout(
        title=dict(text="Event Type Breakdown", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=350,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )

    return fig_to_json(fig_pie), fig_to_json(fig_kw) if fig_kw else None, fig_to_json(fig_actor), fig_to_json(fig_evt)


def compute_geo():
    if hice_df.empty:
        return "[]"
    records = []
    for _, row in hice_df.iterrows():
        records.append({
            "lat": row["latitude"],
            "lon": row["longitude"],
            "type": HICE_LABELS.get(row["hice_type"], row["hice_type"]),
            "type_key": row["hice_type"],
            "location": row["location"],
            "date": row["event_date"].strftime("%b %d, %Y"),
            "region": row["admin1"],
            "actor": row["actor1"],
            "fatalities": int(row["fatalities"]),
            "notes": str(row["notes"])[:200],
        })
    return json.dumps(records)


def compute_temporal():
    if hice_df.empty:
        return None, None, None

    trend = hice_df.set_index("event_date").resample("ME").size().reset_index(name="count")
    fig_trend = go.Figure(
        go.Scatter(
            x=trend["event_date"], y=trend["count"],
            mode="lines+markers",
            line=dict(color="#2563eb", width=2.5),
            marker=dict(size=5, color="#2563eb"),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.06)",
            hovertemplate="<b>%{x|%B %Y}</b><br>Incidents: %{y}<extra></extra>",
        )
    )
    fig_trend.update_layout(
        title=dict(text="Healthcare Interference Incidents (Monthly)", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=400,
        margin=dict(t=50, b=30, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title="Incidents",
    )

    cat_trend = hice_df.set_index("event_date").groupby("hice_type").resample("ME").size().reset_index(name="count")
    fig_cat = px.line(
        cat_trend, x="event_date", y="count", color="hice_type",
        color_discrete_map=HICE_COLORS, line_shape="linear",
    )
    fig_cat.update_layout(
        title=dict(text="Monthly Incidents by Category", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=350,
        margin=dict(t=50, b=30, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title="Incidents",
    )
    fig_cat.update_traces(opacity=0.8)

    cum = hice_df.sort_values("event_date").copy()
    cum["cumulative"] = range(1, len(cum) + 1)
    fig_cum = px.area(cum, x="event_date", y="cumulative", color_discrete_sequence=["#2563eb"])
    fig_cum.update_layout(
        title=dict(text="Cumulative HICE Incidents", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=300,
        margin=dict(t=40, b=20, l=50, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Cumulative",
    )
    fig_cum.update_traces(line=dict(width=2))

    return fig_to_json(fig_trend), fig_to_json(fig_cat), fig_to_json(fig_cum)


def compute_risk():
    if hice_df.empty:
        return None, None, None, []

    severity = hice_df.groupby("admin1").agg(
        events=("event_id_cnty", "count"),
        fatalities=("fatalities", "sum"),
    ).reset_index()
    severity["Severity_Index"] = (severity["fatalities"] / severity["events"]).round(2)
    severity = severity.sort_values("Severity_Index", ascending=False)

    fig_sev = px.bar(
        severity.head(15),
        x="Severity_Index", y="admin1", orientation="h",
        color="Severity_Index", color_continuous_scale="Reds",
    )
    fig_sev.update_layout(
        title=dict(text="Regional Severity Index (Fatalities / Event)", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=400,
        margin=dict(t=50, b=20, l=20, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        coloraxis_showscale=False,
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
    )

    risk = hice_df.groupby("admin1").agg(
        Frequency=("event_id_cnty", "count"),
        fatalities=("fatalities", "sum"),
    )
    risk["Lethality"] = (risk["fatalities"] / risk["Frequency"]).round(2)
    risk = risk.reset_index()

    avg_l = risk["Lethality"].mean()
    fig_matrix = px.scatter(
        risk, x="Frequency", y="Lethality",
        text="admin1", size="fatalities",
        color="Lethality", color_continuous_scale="Reds",
        size_max=28,
    )
    fig_matrix.update_traces(textposition="top center", textfont=dict(size=9))
    fig_matrix.add_hline(
        y=avg_l, line_dash="dash", line_color="#6b7280",
        annotation_text=f"Mean ({avg_l:.2f})", annotation_font_size=10,
    )
    fig_matrix.update_layout(
        title=dict(text="Risk Matrix: Frequency vs. Lethality", font=dict(size=15, weight=600, color="#1f2937"), x=0),
        height=400,
        margin=dict(t=50, b=30, l=50, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        xaxis_title="Event Frequency",
        yaxis_title="Lethality (Fatalities per Event)",
    )

    W = {
        "personnel_targeting": 1.0,
        "systemic_attack": 0.9,
        "infrastructure_damage": 0.6,
        "access_disruption": 0.5,
        "humanitarian_disruption": 0.3,
    }
    local_df = hice_df.copy()
    local_df["hice_weight"] = local_df["hice_type"].map(W).fillna(0.3)
    local_df["event_impact"] = local_df["hice_weight"] * (1 + np.log1p(local_df["fatalities"].clip(lower=0)))

    vuln = local_df.groupby("admin1").agg(
        HICE=("event_id_cnty", "count"),
        fatalities=("fatalities", "sum"),
        Score=("event_impact", "sum"),
        PersonnelTargeting=("hice_type", lambda s: (s == "personnel_targeting").sum()),
    ).reset_index()
    vuln["Score"] = vuln["Score"].round(1)
    vuln["PctPersonnel"] = (vuln["PersonnelTargeting"] / vuln["HICE"] * 100).round(0).astype(int)
    vuln = vuln.sort_values("Score", ascending=False)
    vuln["Rank"] = range(1, len(vuln) + 1)

    fig_vuln = px.bar(
        vuln, x="Score", y="admin1", orientation="h",
        color="PctPersonnel", color_continuous_scale="Reds",
    )
    fig_vuln.update_layout(
        title=dict(
            text="Healthcare Vulnerability Score (weighted by HICE type)",
            font=dict(size=15, weight=600, color="#1f2937"), x=0,
        ),
        height=420,
        margin=dict(t=50, b=20, l=20, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
        coloraxis_showscale=False,
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
    )
    fig_vuln.update_traces(
        hovertemplate="<b>%{y}</b><br>Score: %{x}<br>Personnel targeting: %{marker.color:.0f}%<extra></extra>"
    )

    vuln_table = []
    for _, row in vuln.iterrows():
        vuln_table.append({
            "rank": int(row["Rank"]),
            "region": row["admin1"],
            "hice": int(row["HICE"]),
            "fatalities": int(row["fatalities"]),
            "score": row["Score"],
            "pct_personnel": int(row["PctPersonnel"]),
        })

    return fig_to_json(fig_sev), fig_to_json(fig_matrix), fig_to_json(fig_vuln), vuln_table


def compute_records():
    if hice_df.empty:
        return []
    records = []
    for _, row in hice_df.sort_values("event_date", ascending=False).iterrows():
        records.append({
            "date": row["event_date"].strftime("%Y-%m-%d"),
            "type": HICE_LABELS.get(row["hice_type"], row["hice_type"]),
            "type_key": row["hice_type"],
            "region": row["admin1"],
            "location": row["location"],
            "actor": str(row["actor1"]),
            "fatalities": int(row["fatalities"]),
            "notes": str(row["notes"]),
            "event_type": str(row["event_type"]),
            "actor2": str(row["actor2"]) if pd.notna(row.get("actor2")) else None,
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"]),
        })
    return records


overview_data = compute_overview()
geo_data = compute_geo()
temporal_data = compute_temporal()
risk_data = compute_risk()
records_data = compute_records()

category_breakdown = {}
if not hice_df.empty:
    for cat in ["infrastructure_damage", "access_disruption", "personnel_targeting", "humanitarian_disruption", "systemic_attack"]:
        count = (hice_df["hice_type"] == cat).sum()
        category_breakdown[cat] = {
            "count": count,
            "label": HICE_LABELS.get(cat, cat),
            "color": HICE_COLORS.get(cat, "#6b7280"),
            "pct": round(count / max(total_hice, 1) * 100, 1),
        }


# ── Pipeline Simulator ──────────────────────────────────────────────────

def find_matches(regex_list: list[str], text: str) -> list[dict]:
    """Find all matches for a list of regex patterns. Returns [{pattern, start, end, match_text}, ...]."""
    results = []
    for pat in regex_list:
        for m in re.finditer(pat, text):
            results.append({
                "pattern": pat,
                "start": m.start(),
                "end": m.end(),
                "match_text": m.group(),
            })
    return results


def find_proximity_matches(text: str, health_regex: str, attack_regex: str, window: int) -> list[dict]:
    """Find bidirectional proximity matches."""
    results = []
    # health near attack
    pat1 = rf'({health_regex}.{{0,{window}}}{attack_regex})'
    for m in re.finditer(pat1, text):
        results.append({
            "pattern": "health_near_attack",
            "start": m.start(), "end": m.end(),
            "match_text": m.group(),
        })
    # attack near health
    pat2 = rf'({attack_regex}.{{0,{window}}}{health_regex})'
    for m in re.finditer(pat2, text):
        results.append({
            "pattern": "attack_near_health",
            "start": m.start(), "end": m.end(),
            "match_text": m.group(),
        })
    return results


def simulate_pipeline(text: str) -> dict:
    """Run a single narrative through the full HICE detection pipeline and return step-by-step results."""
    lower = text.lower().strip()
    if not lower:
        return {"error": "No text provided"}

    steps = []

    # Layer 1: Structural Gate (kinetic event + armed actor)
    kinetic_pattern = r'\b(attack(ed|ing)?|shell(ed|ing)?|bomb(ed|ing)?|raid(ed|ing)?|assault(ed|ing)?|fired?\s+(upon|on|at)|clash(ed|ing)?|fought?|fighting|gunfire|shoot(ing)?|shot|explosion|airstrike|artillery|mortar|rocket|grenade)\b'
    actor_pattern = r'\b(military|soldier(s)?|junta|tatmadaw|armed\s+forces|police|security\s+forces|rebels?|resistance|militia|armed\s+group|army|troops|gunmen)\b'
    kinetic_matches = find_matches([kinetic_pattern], lower)
    actor_matches = find_matches([actor_pattern], lower)
    structural_pass = len(kinetic_matches) > 0 and len(actor_matches) > 0
    steps.append({
        "id": "structural_gate",
        "label": "Structural Gate (Layer 1)",
        "desc": "Kinetic conflict event with identified armed actor",
        "passed": structural_pass,
        "matches": kinetic_matches + actor_matches,
        "subchecks": [
            {"label": "Kinetic event language (attack, shell, raid, etc.)", "passed": len(kinetic_matches) > 0},
            {"label": "Armed actor identified (military, police, militia, etc.)", "passed": len(actor_matches) > 0},
        ],
    })

    # Layer 2: Health mask
    health_matches = find_matches(HEALTH_TERMS, lower)
    steps.append({
        "id": "health_mask",
        "label": "Health Keyword Detection",
        "desc": "Mentions health infrastructure, personnel, or organisations",
        "passed": len(health_matches) > 0,
        "matches": health_matches,
    })

    # Step 2: Targeting mask
    targeting_matches = find_matches([TARGETING_PATTERN], lower)
    steps.append({
        "id": "targeting_mask",
        "label": "Targeting Language",
        "desc": "Explicit targeting verbs (targeted, fired upon, raided, etc.)",
        "passed": len(targeting_matches) > 0,
        "matches": targeting_matches,
    })

    # Step 3: Phrase mask
    phrase_matches = find_matches(ACTION_PHRASES, lower)
    steps.append({
        "id": "phrase_mask",
        "label": "Action Phrases",
        "desc": "Passive-voice hostile action phrases (was destroyed, came under fire, etc.)",
        "passed": len(phrase_matches) > 0,
        "matches": phrase_matches,
    })

    # Step 4: Soft health mask
    soft_matches = find_matches([SOFT_HEALTH_PATTERN], lower)
    steps.append({
        "id": "soft_health",
        "label": "Soft Health-Casualty Coupling",
        "desc": "Casualty language near health personnel",
        "passed": len(soft_matches) > 0,
        "matches": soft_matches,
    })

    # Step 5: Proximity mask
    proximity_matches = find_proximity_matches(lower, HEALTH_INFRA, ATTACK_TERMS, PROXIMITY_WINDOW)
    steps.append({
        "id": "proximity",
        "label": "Bidirectional Proximity Coupling",
        "desc": f"Health term and attack verb co-occur within {PROXIMITY_WINDOW} characters",
        "passed": len(proximity_matches) > 0,
        "matches": proximity_matches,
    })

    # Step 6: Bystander disambiguation
    enum_fp_matches = find_matches([ENUMERATION_FP_PATTERN], lower)
    enum_neg_matches = find_matches([ENUMERATION_FP_NEGATIVE], lower)
    hospital_bystander_matches = find_matches([HOSPITAL_BYSTANDER_PATTERN], lower)
    hospital_bystander_neg_matches = find_matches([HOSPITAL_BYSTANDER_NEGATIVE], lower)

    enumeration_bystander = len(enum_fp_matches) > 0 and len(enum_neg_matches) == 0
    hospital_bystander = len(hospital_bystander_matches) > 0 and len(hospital_bystander_neg_matches) == 0
    bystander_flagged = enumeration_bystander or hospital_bystander

    steps.append({
        "id": "bystander",
        "label": "Bystander Disambiguation (F1–F4)",
        "desc": "Excludes false positives where health terms are background context",
        "passed": not bystander_flagged,
        "matches": enum_fp_matches + hospital_bystander_matches,
        "bystander_flagged": bystander_flagged,
        "subchecks": [
            {
                "label": "F1/F4 — Enumeration FP",
                "pattern": "civilian casualty list with health terms but no attack",
                "passed": not (len(enum_fp_matches) > 0 and len(enum_neg_matches) == 0),
                "matched": len(enum_fp_matches) > 0 and len(enum_neg_matches) == 0,
            },
            {
                "label": "F3 — Spatial-only Proximity",
                "pattern": "taken/sent to hospital as location, not attack target",
                "passed": not (len(hospital_bystander_matches) > 0 and len(hospital_bystander_neg_matches) == 0),
                "matched": len(hospital_bystander_matches) > 0 and len(hospital_bystander_neg_matches) == 0,
            },
        ],
    })

    # Step 7: Coupling
    proximity_ok = len(proximity_matches) > 0
    phrase_ok = len(phrase_matches) > 0
    soft_ok = len(soft_matches) > 0
    targeting_ok = len(targeting_matches) > 0
    coupling = (proximity_ok or phrase_ok or soft_ok or targeting_ok) and not bystander_flagged

    steps.append({
        "id": "coupling",
        "label": "Event Coupling Decision",
        "desc": "Hostile signal present AND not excluded by bystander rules",
        "passed": coupling,
        "subchecks": [
            {"label": "Any signal (proximity / phrase / soft / targeting)", "passed": proximity_ok or phrase_ok or soft_ok or targeting_ok},
            {"label": "Not excluded by bystander", "passed": not bystander_flagged},
        ],
    })

    # Final decision
    health_ok = len(health_matches) > 0
    is_hice = (health_ok or proximity_ok) and coupling

    # Classification
    if is_hice:
        from src.hice_detector import classify_hice_type as classify_series_fn
        dummy_series = pd.Series([lower])
        hice_type_arr = classify_series_fn(dummy_series)
        hice_type = str(hice_type_arr[0])
        hice_label = HICE_LABELS.get(hice_type, hice_type)
        hice_color = HICE_COLORS.get(hice_type, "#6b7280")
    else:
        hice_type = None
        hice_label = None
        hice_color = None

    # Build highlighted text with spans for each match type
    highlight_spans = {}
    for step_id, color in [
        ("structural_gate", "#4f46e5"),
        ("health_mask", "#2563eb"),
        ("targeting_mask", "#dc2626"),
        ("phrase_mask", "#7c3aed"),
        ("soft_health", "#059669"),
        ("proximity", "#0891b2"),
        ("bystander", "#d97706"),
    ]:
        for s in steps:
            if s["id"] == step_id:
                for m in s.get("matches", []):
                    key = (m["start"], m["end"])
                    if key not in highlight_spans:
                        highlight_spans[key] = []
                    highlight_spans[key].append({"step_id": step_id, "color": color, "label": s["label"]})

    return {
        "text": text,
        "text_lower": lower,
        "steps": steps,
        "coupling": coupling,
        "bystander_flagged": bystander_flagged,
        "is_hice": is_hice,
        "hice_type": hice_type,
        "hice_label": hice_label,
        "hice_color": hice_color,
        "highlight_spans": {f"{k[0]}:{k[1]}": v for k, v in highlight_spans.items()},
    }


# ── Routes ────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    top_cat = max(category_breakdown, key=lambda c: category_breakdown[c]["count"]) if category_breakdown else None
    regions_affected = hice_df["admin1"].nunique() if not hice_df.empty else 0
    total_fatalities = int(hice_df["fatalities"].sum()) if not hice_df.empty else 0
    fatal_pct = round(total_hice / max(total_events, 1) * 100, 1)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_events": total_events,
        "total_hice": total_hice,
        "fatal_pct": fatal_pct,
        "top_cat": category_breakdown.get(top_cat) if top_cat else None,
        "regions_affected": regions_affected,
        "total_fatalities": total_fatalities,
        "date_min": date_min.strftime("%Y-%m-%d"),
        "date_max": date_max.strftime("%Y-%m-%d"),
        "categories": category_breakdown,
        "overview_pie": overview_data[0],
        "overview_kw": overview_data[1],
        "overview_actor": overview_data[2],
        "overview_evt": overview_data[3],
        "geo_data": geo_data,
        "temporal_trend": temporal_data[0],
        "temporal_cat": temporal_data[1],
        "temporal_cum": temporal_data[2],
        "risk_severity": risk_data[0],
        "risk_matrix": risk_data[1],
        "risk_vuln": risk_data[2],
        "risk_table": risk_data[3],
        "records": json.dumps(records_data),
        "hice_colors": json.dumps(HICE_COLORS),
        "hice_labels": json.dumps(HICE_LABELS),
    })


@app.post("/simulate")
async def simulate(request: Request):
    body = await request.json()
    text = body.get("text", "")
    result = simulate_pipeline(text)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
