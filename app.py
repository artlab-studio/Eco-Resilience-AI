import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import contextily as ctx
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide", page_title="Eco-Resilience AI Platform")

# -------------------------------------------------
# STYLING
# -------------------------------------------------
st.markdown("""
<style>
body {font-family: 'Segoe UI', sans-serif;}
.block-container {padding-top: 1rem;}
.card {
    background-color: rgba(255,255,255,0.85);
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATA
# -------------------------------------------------
data = [
    ["Ambago",12656,13634,15523,1.58,8.9430,125.5340],
    ["Ampayon",12720,13820,13872,1.76,8.9700,125.5600],
    ["Baan KM 3",11308,14539,15066,5.43,8.9570,125.5320],
    ["Doongan",13728,13814,14591,0.13,8.9420,125.5510],
    ["Libertad",21703,25296,24880,3.28,8.9500,125.5170],
    ["Obrero (Barangay 18)",9774,8643,8505,-2.56,8.9490,125.5430],
    ["San Vicente",16187,19500,20369,4.00,8.9640,125.5400],
]

df = pd.DataFrame(data, columns=[
    "Barangay","Pop2015","Pop2020","Pop2024","Growth","Lat","Lon"
])

df["Change"] = df["Pop2024"] - df["Pop2020"]

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("Controls")

selected = st.sidebar.selectbox("Select Barangay", df["Barangay"])
theme = st.sidebar.selectbox("Map Theme",[
    "Population Map","Flood Hazard","Landslide","Topographic","Integrated Risk"
])

focus = st.sidebar.selectbox("Planning Focus",[
    "Integrated","DRRM","Circular Economy"
])

basemap = st.sidebar.selectbox("Basemap",[
    "OpenStreetMap","CartoDB positron","CartoDB Voyager"
])

st.sidebar.info("Prototype academic platform only.")

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard","Population","Map","AI Assessment","Map Generator"
])

# -------------------------------------------------
# TAB 1
# -------------------------------------------------
with tab1:
    st.title("Eco-Resilience AI Platform")
    st.markdown("Planning & Research Support System for Butuan City")

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Population 2020","372,910")
    col2.metric("Population 2024","385,530")
    col3.metric("Land Area","816.62 km²")
    col4.metric("Barangays","86")

# -------------------------------------------------
# TAB 2
# -------------------------------------------------
with tab2:
    st.subheader("Population Profile")

    st.dataframe(df)

    chart = alt.Chart(df).mark_bar().encode(
        x="Barangay",
        y="Pop2024"
    )
    st.altair_chart(chart, use_container_width=True)

# -------------------------------------------------
# TAB 3 MAP
# -------------------------------------------------
with tab3:
    st.subheader("Interactive Map")

    m = folium.Map(location=[8.95,125.53], zoom_start=13)

    for _,r in df.iterrows():
        folium.CircleMarker(
            location=[r["Lat"],r["Lon"]],
            radius=5 + (r["Pop2024"]/5000),
            popup=r["Barangay"],
            color="green"
        ).add_to(m)

    st_folium(m, width=900, height=500)

    st.warning("Barangay locations are approximate reference points only.")

# -------------------------------------------------
# TAB 4 AI
# -------------------------------------------------
with tab4:
    st.subheader("AI Assessment")

    f = st.selectbox("Flood",["Low","Moderate","High"])
    w = st.selectbox("Waste",["Good","Fair","Poor"])
    d = st.selectbox("Drainage",["Good","Fair","Poor"])
    p = st.selectbox("Population",["Low","Moderate","High"])

    score_map = {"Low":1,"Moderate":2,"High":3,"Good":1,"Fair":2,"Poor":3}
    score = score_map[f] + score_map[w] + score_map[d] + score_map[p]

    if score >= 10:
        level = "HIGH"
    elif score >=7:
        level = "MODERATE"
    else:
        level = "LOW"

    st.metric("Risk Score", score)
    st.metric("Risk Level", level)

# -------------------------------------------------
# MAP GENERATOR
# -------------------------------------------------
def generate_map(selected_row):

    fig, ax = plt.subplots(figsize=(11.7,8.3))  # A4 landscape

    ax.scatter(df["Lon"], df["Lat"], color="gray", s=20)
    ax.scatter(selected_row["Lon"], selected_row["Lat"], color="red", s=100)

    ax.set_title("Eco-Resilience AI Platform Map")

    # SIDE PANEL TEXT
    ax.text(1.02,0.9,"DATA SOURCES", transform=ax.transAxes, fontsize=8, fontweight="bold")
    ax.text(1.02,0.85,"NAMRIA | MGB | Project NOAH | DENR | PSA", transform=ax.transAxes, fontsize=7)
    ax.text(1.02,0.8,"(Prototype Use Only)", transform=ax.transAxes, fontsize=6, fontstyle="italic")

    return fig

# -------------------------------------------------
# TAB 5
# -------------------------------------------------
with tab5:
    st.subheader("Thesis Map Generator")

    row = df[df["Barangay"]==selected].iloc[0]

    fig = generate_map(row)
    st.pyplot(fig)

    st.download_button("Download Map","",file_name="map.png")

    st.caption("Source: NAMRIA | MGB | Project NOAH | DENR | PSA")
