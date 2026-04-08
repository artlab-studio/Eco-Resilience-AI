import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import contextily as cx
from datetime import datetime

# ==========================================
# 1. UI THEME ENGINE
# ==========================================
st.set_page_config(page_title="Eco-Resilience AI | Butuan", page_icon="📐", layout="wide")

def apply_theme():
    st.markdown("""
        <style>
        .eng-header {
            background-color: #002B36;
            color: white;
            padding: 2rem;
            border-left: 10px solid #2AA198;
            border-radius: 0 10px 10px 0;
            margin-bottom: 2rem;
        }
        div.stButton > button {
            background-color: #2AA198;
            color: white;
            font-weight: 600;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def get_data():
    city_meta = {"Project": "Eco-Resilience AI Platform", "Agency": "Butuan Planning & Research", "Datum": "PRS92 / WGS 84"}
    data = [
        {"name": "Ambago", "p24": 15523, "lat": 8.9430, "lon": 125.5340, "risk": "High", "zone": "R-2"},
        {"name": "Ampayon", "p24": 13872, "lat": 8.9700, "lon": 125.5600, "risk": "Moderate", "zone": "INST"},
        {"name": "Baan KM 3", "p24": 15066, "lat": 8.9570, "lon": 125.5320, "risk": "High", "zone": "C-2"},
        {"name": "Doongan", "p24": 14591, "lat": 8.9420, "lon": 125.5510, "risk": "High", "zone": "R-1"},
        {"name": "Libertad", "p24": 24880, "lat": 8.9500, "lon": 125.5170, "risk": "Low", "zone": "C-3"},
        {"name": "Obrero", "p24": 8505, "lat": 8.9490, "lon": 125.5430, "risk": "Moderate", "zone": "IND-1"},
        {"name": "San Vicente", "p24": 20369, "lat": 8.9640, "lon": 125.5400, "risk": "Moderate", "zone": "R-2"}
    ]
    return city_meta, pd.DataFrame(data)

# ==========================================
# 3. PROFESSIONAL MAP PLATE GENERATOR
# ==========================================
def generate_formal_plate(bgy_data, map_type, city_meta):
    # Create figure with two main sections (Map and Sidebar)
    fig = plt.figure(figsize=(16, 10), constrained_layout=True)
    gs = gridspec.GridSpec(1, 2, width_ratios=[3.5, 1], figure=fig)
    
    # Left Section: The Map
    ax_map = fig.add_subplot(gs[0])
    ax_map.scatter(bgy_data['lon'], bgy_data['lat'], c='red', s=300, marker='X', edgecolors='white', zorder=5)
    
    try:
        cx.add_basemap(ax_map, crs='EPSG:4326', source=cx.providers.Esri.WorldImagery)
    except:
        ax_map.set_facecolor('#d1d1d1')
    
    ax_map.set_axis_off()
    
    # Right Section: Technical Sidebar (The "Bohol" Reference Layout)
    ax_side = fig.add_subplot(gs[1])
    ax_side.set_axis_off()
    
    # Formal Lines
    ax_side.axvline(x=0, color='black', lw=2)
    ax_side.axhline(y=1, color='black', lw=2)
    ax_side.axhline(y=0, color='black', lw=2)

    # Sidebar Content (Wordings)
    y_ptr = 0.95
    ax_side.text(0.05, y_ptr, "REPUBLIC OF THE PHILIPPINES", fontsize=9, fontweight='bold')
    y_ptr -= 0.03
    ax_side.text(0.05, y_ptr, "CITY GOVERNMENT OF BUTUAN", fontsize=8)
    y_ptr -= 0.08
    ax_side.text(0.05, y_ptr, "PROJECT NAME:", fontsize=7, fontweight='bold', color='gray')
    y_ptr -= 0.03
    ax_side.text(0.05, y_ptr, f"{city_meta['Project'].upper()}", fontsize=11, fontweight='bold', color='#002B36')
    
    y_ptr -= 0.10
    ax_side.text(0.05, y_ptr, "MAP TITLE:", fontsize=7, fontweight='bold', color='gray')
    y_ptr -= 0.04
    ax_side.text(0.05, y_ptr, f"{map_type.upper()}", fontsize=10, fontweight='bold', color='#d32f2f')
    
    y_ptr -= 0.10
    ax_side.text(0.05, y_ptr, "LOCATION:", fontsize=7, fontweight='bold', color='gray')
    y_ptr -= 0.03
    ax_side.text(0.05, y_ptr, f"BARANGAY {bgy_data['name'].upper()}", fontsize=9)
    
    y_ptr -= 0.15
    ax_side.text(0.05, y_ptr, "LEGEND:", fontsize=8, fontweight='bold')
    ax_side.scatter(0.1, y_ptr-0.03, c='red', s=100, marker='X')
    ax_side.text(0.2, y_ptr-0.04, "Site Centroid", fontsize=8)
    
    y_ptr -= 0.25
    ax_side.text(0.05, y_ptr, "TECHNICAL NOTES:", fontsize=7, fontweight='bold')
    y_ptr -= 0.03
    ax_side.text(0.05, y_ptr, f"Datum: {city_meta['Datum']}\nSource: LiDAR (LIPAD 2017)\nScale: Not to Scale", fontsize=6, linespacing=1.8)
    
    y_ptr -= 0.15
    ax_side.text(0.05, y_ptr, f"DATE: {datetime.now().strftime('%B %Y')}", fontsize=7, fontweight='bold')

    # North Arrow on Map
    ax_map.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    xycoords='axes fraction', ha='center', fontsize=20, fontweight='bold')

    return fig

# ==========================================
# 4. APP INTERFACE
# ==========================================
def main():
    apply_theme()
    city_meta, df = get_data()

    st.markdown("""<div class="eng-header"><h1>Eco-Resilience AI: Professional Planner</h1><p>Butuan City Integrated Technical Portal</p></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 PROJECT SETUP")
        target_bgy = st.selectbox("Select Barangay", df['name'].tolist())
        map_view = st.radio("Framework", ["LiDAR Flood Hazard", "Zoning Classification", "Topographic Map"])
        st.markdown("---")
        st.button("💾 Download Presentation Plate")

    bgy_data = df[df['name'] == target_bgy].iloc[0]
    t1, t2 = st.tabs(["📊 Analytics", "🗺️ GIS & Formal Plate"])

    with t1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Pop 2024", f"{bgy_data['p24']:,}")
        c2.metric("LiDAR Risk", bgy_data['risk'])
        c3.metric("Zone", bgy_data['zone'])
        
        bar = alt.Chart(df).mark_bar().encode(
            x='name:N', y='p24:Q', 
            color=alt.condition(alt.datum.name == target_bgy, alt.value('#2AA198'), alt.value('#BDC3C7'))
        ).properties(height=350)
        st.altair_chart(bar, use_container_width=True)

    with t2:
        st.subheader("Interactive GIS Reference")
        m = folium.Map(location=[bgy_data['lat'], bgy_data['lon']], zoom_start=15, tiles='CartoDB Positron')
        folium.TileLayer('OpenStreetMap', name="Street Map").add_to(m)
        folium.LayerControl().add_to(m)
        folium_static(m, width=1100)

        st.markdown("---")
        st.subheader("Formal Map Output (Standard Engineering Layout)")
        st.info("The layout below uses the Technical Sidebar format for thesis and professional presentations.")
        fig = generate_formal_plate(bgy_data, map_view, city_meta)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
