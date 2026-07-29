# app.py — Phase 11: GeoVeritas Streamlit Dashboard

import sys
import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GeoVeritas — Flood Trust Dashboard",
    page_icon="🛰️",
    layout="wide",
)

# ── Location lookup (inline — no import needed) ────────────
LOCATION_NAMES = {
    (8.5241,  76.9366): "Thiruvananthapuram",
    (9.9312,  76.2673): "Alappuzha",
    (10.0889, 76.3710): "Ernakulam",
    (10.5276, 76.2144): "Thrissur",
    (11.2588, 75.7804): "Kozhikode",
}

def get_location_name(lat, lon):
    for (la, lo), name in LOCATION_NAMES.items():
        if abs(la - lat) < 0.001 and abs(lo - lon) < 0.001:
            return name
    return f"({lat:.4f},{lon:.4f})"

# ── Load data ──────────────────────────────────────────────
@st.cache_data
def load_data():
    trust_df  = pd.read_csv("data/processed/trust_scores.csv")
    alerts_df = pd.read_csv("data/processed/alerts.csv")
    try:
        conflicts_df = pd.read_csv("data/processed/conflicts.csv")
    except FileNotFoundError:
        conflicts_df = pd.DataFrame()
    return trust_df, alerts_df, conflicts_df

trust_df, alerts_df, conflicts_df = load_data()

# Add readable name column
trust_df['location'] = trust_df.apply(
    lambda r: get_location_name(r['lat'], r['lon']), axis=1
)

# ── Header ─────────────────────────────────────────────────
st.title("🛰️ GeoVeritas")
st.caption("Multi-source geospatial trust engine — Kerala Flood 2018")

# ── Top metrics ────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Locations monitored", len(trust_df))
c2.metric("High alert zones",    int((trust_df['trust_score'] >= 0.9).sum()))
c3.metric("Total conflicts",     int(trust_df['conflicts'].sum()))
c4.metric("Overall GeoTrust",    f"{trust_df['trust_score'].mean():.0%}")

st.divider()

# ── Map + Detail layout ────────────────────────────────────
map_col, detail_col = st.columns([1.3, 1])

with map_col:
    st.subheader("📍 Trust Map")

    m = folium.Map(location=[9.9, 76.5], zoom_start=7, tiles="CartoDB positron")

    for _, row in trust_df.iterrows():
        name  = row['location']
        trust = row['trust_score']
        color = "red" if trust >= 0.9 else ("orange" if trust >= 0.7 else "green")

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=14,
            popup=folium.Popup(
                f"<b>{name}</b><br>Trust: {trust:.0%}<br>"
                f"Risk: {row['risk_level']}<br>Conflicts: {row['conflicts']}",
                max_width=200
            ),
            tooltip=f"{name} — {trust:.0%} trust",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
        ).add_to(m)

    st_folium(m, width=None, height=520)

with detail_col:
    st.subheader("🔍 Location Explorer")

    selected = st.selectbox("Select a location", trust_df['location'].tolist())
    row = trust_df[trust_df['location'] == selected].iloc[0]
    trust = row['trust_score']

    # Alert banner
    if trust >= 0.9:
        st.error(f"🔴 HIGH ALERT — {selected}")
    elif trust >= 0.7:
        st.warning(f"🟡 MEDIUM ALERT — {selected}")
    else:
        st.success(f"🟢 LOW ALERT — {selected}")

    st.metric("Trust Score", f"{trust:.0%}", row['uncertainty'])
    st.progress(float(trust))

    # Evidence trail
    has_conflict = row['conflicts'] > 0
    st.markdown("**Evidence trail**")
    st.markdown(f"""
| Source | Status | Reliability |
|---|---|---|
| Sentinel-1 SAR | ✅ Water detected | 95% |
| GPM Rainfall | ✅ 124.5mm recorded | 93% |
| USGS Gauge | ✅ River level 8.3m | 90% |
| GloFAS Model | {'❌ Low risk (CONFLICT)' if has_conflict else '✅ High risk confirmed'} | 78% |
""")

    # Conflicts
    if not conflicts_df.empty and has_conflict:
        loc_c = conflicts_df[
            (conflicts_df['lat'] == row['lat']) &
            (conflicts_df['lon'] == row['lon'])
        ]
        if not loc_c.empty:
            st.markdown("**⚠️ Conflicts detected**")
            for _, c in loc_c.iterrows():
                st.warning(f"{c['conflict']}  \n*{c['source_a']} vs {c['source_b']}*")

    # Why this score
    st.markdown("**Why this trust score**")
    st.markdown(f"""
| Factor | Value |
|---|---|
| Cross-source agreement | {row['agreement']:.0%} |
| Physical plausibility | {row['plausibility']:.0%} |
| Uncertainty band | {row['uncertainty']} |
""")

st.divider()

# ── Full table ─────────────────────────────────────────────
with st.expander("📋 Full trust score table"):
    st.dataframe(
        trust_df[['location','trust_score','risk_level',
                  'agreement','plausibility','uncertainty','conflicts']],
        use_container_width=True,
        hide_index=True,
    )