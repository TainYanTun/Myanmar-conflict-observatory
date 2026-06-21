"""
Pre-compute all dashboard data once and save to JSON.
Run locally after data updates; dashboard loads from the JSON for fast startup.
"""
import json, glob, pathlib, os, sys
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from src.processing import (
    extract_health_impacts,
    classify_hice_type,
    categorize_actor,
    extract_keywords,
    clean_conflict_data,
)

HERE = pathlib.Path(__file__).parent.parent

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


def load_data():
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
            return df, f
        except Exception:
            continue
    return None


def compute_overview(hice_df, total_hice):
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


def compute_geo(hice_df):
    if hice_df.empty:
        return []
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
    return records


def compute_temporal(hice_df):
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


def compute_risk(hice_df):
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


def compute_records(hice_df):
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


def main():
    result = load_data()
    if result is None:
        print("ERROR: No CSV data found.")
        sys.exit(1)
    df, source = result
    print(f"Loaded {len(df)} rows from {source}")

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
    print(f"HICE incidents: {total_hice} / {total_events} total events")

    overview = compute_overview(hice_df, total_hice)
    geo = compute_geo(hice_df)
    temporal = compute_temporal(hice_df)
    risk = compute_risk(hice_df)
    records = compute_records(hice_df)

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

    data = {
        "meta": {
            "total_events": total_events,
            "total_hice": total_hice,
            "date_min": date_min.strftime("%Y-%m-%d"),
            "date_max": date_max.strftime("%Y-%m-%d"),
        },
        "overview": {
            "pie": overview[0],
            "kw": overview[1],
            "actor": overview[2],
            "evt": overview[3],
        },
        "geo": geo,
        "temporal": {
            "trend": temporal[0],
            "cat": temporal[1],
            "cum": temporal[2],
        },
        "risk": {
            "severity": risk[0],
            "matrix": risk[1],
            "vuln": risk[2],
            "table": risk[3],
        },
        "records": records,
        "categories": category_breakdown,
    }

    out_path = HERE / "dashboard_data.json"
    with open(out_path, "w") as f:
        json.dump(data, f, cls=NumpyEncoder)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"Saved dashboard data ({size_mb:.2f} MB) to {out_path}")


if __name__ == "__main__":
    main()
