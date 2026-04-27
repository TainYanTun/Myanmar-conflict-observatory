"""
generate_actor_network.py
Generates a clean, publication-quality Actor Interaction Network PNG
for the Myanmar Conflict Observatory research paper.

Usage:
    python scripts/generate_actor_network.py

Output:
    research/assets/actor_network.png  (3x high-res, ~4500px wide)
"""

import os
import sys
import math
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_PATH = os.path.join(ROOT, "research", "assets", "actor_network.png")

# ---------------------------------------------------------------------------
# Actor categorization (mirrors app.py)
# ---------------------------------------------------------------------------
def categorize_actor(actor_name):
    if pd.isna(actor_name):
        return "Unidentified"
    name = str(actor_name).lower()
    if any(x in name for x in [
        "military forces of myanmar", "police forces of myanmar",
        "state administration council", "border guard force",
        "people's militia force"
    ]):
        return "State Forces"
    elif any(x in name for x in [
        "pyu saw htee", "thway thauk", "blood comrades",
        "swan arr shin", "pro-military"
    ]):
        return "Pro-Junta Militia"

    resistance_keywords = [
        "pdf", "people's defense force", "local defense force", "kndf",
        "karenni nationalities defense force", "chinland defense force", "cdf",
        "unidentified anti-coup armed group", "guerrilla", "revolution",
        "defense force", "resistance", "pafd", "dragon army",
        "chindwin attack force", "underground warriors", "young force",
        "leopard army", "brave heart", "commando", "vanguard",
        "liberation army", "freedom force", "federal army", "tiger force",
        "truth army", "defence force", "militia", "security force",
    ]
    if any(x in name for x in resistance_keywords):
        return "Resistance"

    eao_keywords = [
        "knu", "knla", "kndo", "kia", "kio", "tnla", "pslf", "mndaa",
        "aa ", "ula", "rcss", "ssa", "knpp", "cnp", "sspp", "pnlo",
        "brotherhood alliance", "northern alliance", "three brotherhood",
        "absdf", "dkba", "kachin", "karen", "shan state", "arakan",
        "mon state", "nmsp", "chin brotherhood", "rohingya", "arsa",
        "pa-oh", "ta'ang", "palaung", "kokang", "wa state", "uwsa",
        "mon national", "naga", "nscn",
    ]
    if any(x in name for x in eao_keywords):
        return "EAOs"

    if "protesters" in name:
        return "Protesters"
    elif "rioters" in name:
        return "Rioters"
    elif "civilians" in name:
        return "Civilians"
    if "unidentified" in name:
        return "Unidentified"
    return "Other Groups"


# ---------------------------------------------------------------------------
# Professional academic color palette
# Based on ColorBrewer 'Set1' + 'Dark2' qualitative schemes —
# optimised for print, colorblind safety, and grayscale reproduction.
# Ref: Brewer, C.A. (2003). ColorBrewer in Print. Cartography.
# ---------------------------------------------------------------------------
NODE_COLORS = {
    "State Forces":      "#2166ac",   # CB Blue      — authoritative, dominant
    "Resistance":        "#1a9641",   # CB Green     — opposition force
    "EAOs":              "#4dac26",   # CB Lt. Green — ethnic armed orgs
    "Pro-Junta Militia": "#d73027",   # CB Red       — high lethality proxy
    "Civilians":         "#f46d43",   # CB Orange    — civilian exposure
    "Protesters":        "#756bb1",   # CB Purple    — civil society
    "Rioters":           "#b2abd2",   # CB Lt. Purple — minor civil unrest
    "Unidentified":      "#969696",   # Neutral grey
    "Other Groups":      "#bdbdbd",   # Light grey
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_data():
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not csv_files:
        sys.exit(f"[ERROR] No CSV files found in {DATA_DIR}")
    csv_files.sort(key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)), reverse=True)
    path = os.path.join(DATA_DIR, csv_files[0])
    print(f"[INFO] Loading: {path}")
    df = pd.read_csv(path, low_memory=False)
    if "country" in df.columns:
        df = df[df["country"] == "Myanmar"]
    df["event_date"] = pd.to_datetime(df["event_date"])
    df = df[df["event_date"] >= "2021-02-01"]
    return df


# ---------------------------------------------------------------------------
# Build clean graph
# ---------------------------------------------------------------------------
def build_graph(df, min_interactions=5, exclude=None):
    """
    Build an undirected weighted graph from actor interactions.
    min_interactions: minimum number of co-events to draw an edge.
    exclude: set of actor categories to drop entirely.
    """
    if exclude is None:
        exclude = {"Unidentified", "Other Groups"}

    df["a1"] = df["actor1"].apply(categorize_actor)
    df["a2"] = df["actor2"].apply(categorize_actor)

    interactions = df[
        (df["a1"] != df["a2"]) &
        (~df["a1"].isin(exclude)) &
        (~df["a2"].isin(exclude))
    ].copy()

    adj = interactions.groupby(["a1", "a2"]).agg(
        interaction_count=("event_id_cnty", "count"),
        total_fatalities=("fatalities", "sum")
    ).reset_index()

    # Normalise direction: keep (min, max) pairs to deduplicate
    adj["_key"] = adj.apply(lambda r: tuple(sorted([r["a1"], r["a2"]])), axis=1)
    adj = adj.groupby("_key").agg(
        interaction_count=("interaction_count", "sum"),
        total_fatalities=("total_fatalities", "sum")
    ).reset_index()
    adj[["a1", "a2"]] = pd.DataFrame(adj["_key"].tolist(), index=adj.index)
    adj = adj[adj["interaction_count"] >= min_interactions]

    G = nx.Graph()
    for _, row in adj.iterrows():
        G.add_edge(
            row["a1"], row["a2"],
            weight=row["interaction_count"],
            fatalities=row["total_fatalities"]
        )

    return G, adj


# ---------------------------------------------------------------------------
# Layout: shell / circular with manual tier assignment
# ---------------------------------------------------------------------------
def compute_layout(G):
    """
    Use a shell layout for clear, evenly-spaced nodes.
    Central hub (most connected) in the middle, others on an outer ring.
    """
    degrees = dict(G.degree(weight="weight"))
    sorted_nodes = sorted(degrees, key=degrees.get, reverse=True)

    if len(sorted_nodes) == 0:
        return {}

    # Center: top-1 node (State Forces is typically the hub)
    center_node = sorted_nodes[0]
    outer_nodes = [n for n in sorted_nodes if n != center_node]

    # Arrange outer nodes in a circle, sorted by degree descending
    pos = {}
    pos[center_node] = (0.0, 0.0)

    n = len(outer_nodes)
    radius = 1.0
    for i, node in enumerate(outer_nodes):
        angle = 2 * math.pi * i / n - math.pi / 2  # start from top
        pos[node] = (radius * math.cos(angle), radius * math.sin(angle))

    return pos


# ---------------------------------------------------------------------------
# Build Plotly figure
# ---------------------------------------------------------------------------
def build_figure(G, adj, pos):
    max_fat = adj["total_fatalities"].max() or 1
    max_cnt = adj["interaction_count"].max() or 1

    # ---- Edge traces (one trace per edge for individual width) ----
    edge_traces = []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        fatalities = data.get("fatalities", 0)
        count      = data.get("weight", 1)

        # Width: 0.8–7 range — restrained, journal-appropriate
        width = 0.8 + (fatalities / max_fat) * 6.2

        # Color: light steel-grey (low lethality) → dark crimson (high lethality)
        # Based on ColorBrewer RdGy diverging — safe for grayscale printing
        intensity = fatalities / max_fat
        r = int(153 + intensity * (178 - 153))
        g = int(153 + intensity * (24  - 153))
        b = int(153 + intensity * (43  - 153))
        alpha = 0.35 + intensity * 0.55   # low-lethality edges are faint
        color = f"rgba({r},{g},{b},{alpha:.2f})"

        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(width=width, color=color),
            hoverinfo="text",
            hovertext=(
                f"<b>{u}</b> ↔ <b>{v}</b><br>"
                f"Engagements: {count:,}<br>"
                f"Fatalities: {int(fatalities):,}"
            ),
            showlegend=False
        ))

    # ---- Node trace ----
    degrees = dict(G.degree(weight="weight"))
    max_deg = max(degrees.values()) if degrees else 1

    node_x, node_y, node_colors, node_sizes, node_labels, node_hover = [], [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        deg   = degrees.get(node, 1)
        color = NODE_COLORS.get(node, "#64748b")

        node_x.append(x)
        node_y.append(y)
        node_colors.append(color)
        # Size range 28–72
        node_sizes.append(28 + (deg / max_deg) * 44)
        node_labels.append(node)
        node_hover.append(
            f"<b>{node}</b><br>"
            f"Weighted Degree: {int(deg):,}<br>"
            f"Connections: {G.degree(node)}"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_labels,
        textposition="top center",
        textfont=dict(
            family="Arial, Helvetica, sans-serif",
            size=12,
            color="#1a1a1a"
        ),
        hoverinfo="text",
        hovertext=node_hover,
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(color="white", width=2.5),  # clean white ring = journal standard
            opacity=0.92
        ),
        showlegend=False
    )

    # ---- Legend annotation swatches ----
    legend_items = [
        ("State Forces",      NODE_COLORS["State Forces"]),
        ("Resistance",        NODE_COLORS["Resistance"]),
        ("EAOs",              NODE_COLORS["EAOs"]),
        ("Pro-Junta Militia", NODE_COLORS["Pro-Junta Militia"]),
        ("Civilians",         NODE_COLORS["Civilians"]),
        ("Protesters",        NODE_COLORS["Protesters"]),
        ("Rioters",           NODE_COLORS["Rioters"]),
    ]
    legend_traces = []
    for label, color in legend_items:
        legend_traces.append(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(
                size=11,
                color=color,
                symbol="circle",
                line=dict(color="white", width=1.5)
            ),
            name=label,
            showlegend=True
        ))

    fig = go.Figure(data=edge_traces + [node_trace] + legend_traces)

    # ---- Layout ----
    fig.update_layout(
        # No title: LaTeX caption handles the figure description
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, Helvetica, sans-serif", color="#1a1a1a", size=11),
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0.5, y=-0.04,
            xanchor="center", yanchor="top",
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            font=dict(size=11, color="#1a1a1a"),
            traceorder="normal",
            itemsizing="constant"
        ),
        hovermode="closest",
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-1.35, 1.35], showline=False
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-1.35, 1.35], showline=False
        ),
        margin=dict(l=10, r=10, t=20, b=90),
        height=900,
        width=900,
    )

    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    df = load_data()
    G, adj = build_graph(df, min_interactions=5)

    if len(G.nodes()) == 0:
        sys.exit("[ERROR] Graph has no nodes. Check min_interactions threshold.")

    print(f"[INFO] Graph: {len(G.nodes())} nodes, {len(G.edges())} edges")
    pos = compute_layout(G)
    fig = build_figure(G, adj, pos)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.write_image(OUTPUT_PATH, scale=3, width=900, height=900)
    print(f"[✓] Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
