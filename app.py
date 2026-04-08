import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import altair as alt
import matplotlib.pyplot as plt
import contextily as cx
from datetime import datetime

# ==========================================
# 1. CORE CONFIGURATION & THEMING
# ==========================================
st.set_page_config(
    page_title="Eco-Resilience AI: Butuan City",
    page_icon="🏙️",
    layout="wide"
)

def apply_custom_style():
    st.markdown("""
        <style>
        /* Modern UI Accents */
        .stApp { background-color: #f8fafc; }
        .main-header {
            background: linear-gradient(90deg, #1e3a8a 0%, #064e3b 100%);
            padding: 3rem;
            border-radius: 1rem;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border-left: 5px solid #10b981;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .report-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 2rem;
            border-radius: 0.5rem;
            font-family: 'Inter', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def get_master_data():
    city = {
        "name": "Butuan City", "pop_2024": 385530, "area": 816.62, 
        "coords": [8.9534, 125.5288], "region": "Caraga (Region XIII)"
    }
    
    # Comprehensive Barangay Data
    data = [
        {"name": "Ambago", "p15": 12656, "p20": 13634, "p24": 15523, "gr": 1.58, "lat": 8.9430, "lon": 125.5340},
        {"name": "Ampayon", "p15": 12720, "p20": 13820, "p24": 13872, "gr": 1.76, "lat": 8.9700, "lon": 125.5600},
        {"name": "Baan KM 3", "p15": 11308, "p20": 14539, "p24": 15066, "gr": 5.43, "lat": 8.9570, "lon": 125.5320},
        {"name": "Doongan", "p15": 13728, "p20": 13814, "p24": 14591, "gr": 0.13, "lat": 8.9420, "lon": 125.5510},
        {"name": "Libertad", "p15": 21703, "p20": 25296, "p24": 24880, "gr": 3.28, "lat": 8.9500, "lon": 125.5170},
        {"name": "Obrero", "p15": 9774, "p20": 8643, "p24": 8505, "gr": -2.56, "lat": 8.9490, "lon": 125.5430},
        {"name": "San Vicente", "p15": 16187, "p20": 19500, "p24": 20369, "gr": 4.00, "lat": 8.9640, "lon": 125.5400}
    ]
    df = pd.DataFrame(data)
    df['change'] = df['p24'] - df['p20']
    return city, df

# ==========================================
# 3. LOGIC ENGINES
# ==========================================
def calculate_risk(f, w, d, p):
    # Professional weighted scoring
    weights = {'Flood': 0.4, 'Waste': 0.2, 'Drainage': 0.2, 'Pop': 0.2}
    scores = {"Low": 1, "Moderate": 2, "High": 3, "Good": 1, "Fair": 2, "Poor": 3}
    
    total = (scores[f]*weights['Flood']) + (scores[w]*weights['Waste']) + \
            (scores[d]*weights['Drainage']) + (scores[p]*weights['Pop'])
    
    if total > 2.5: return "CRITICAL", "#991b1b", "Immediate structural intervention required."
    if total > 1.8: return "CAUTIONARY", "#92400e", "Enhanced monitoring and localized mitigation."
    return "STABLE", "#065f46", "Maintain existing resilience protocols."

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
def main():
    apply_custom_style()
    city, df = get_master_data()

    # Sidebar Navigation & Context
    with st.sidebar:
        st.title("🛡️ Eco-Resilience")
        st.markdown("---")
        target_bgy = st.selectbox("Select Target Barangay", df['name'].tolist())
        theme = st.selectbox("Map Framework", ["Population Density", "Hazard Sensitivity", "Resource Flow"])
        st.markdown("---")
        st.caption("v2.1.0-Alpha | Butuan Planning Portal")
        st.info("Note: This portal uses prototype reference points for academic demonstration.")

    bgy_data = df[df['name'] == target_bgy].iloc[0]

    # Tabs
    t1, t2, t3, t4 = st.tabs(["🏛️ Executive Summary", "🗺️ Geospatial Studio", "🧠 Resilience AI", "📄 Research Output"])

    # --- TAB 1: EXECUTIVE SUMMARY ---
    with t1:
        st.markdown(f"""
            <div class="main-header">
                <h1>{city['name']} Resilience Dashboard</h1>
                <p>Data-Driven Urban Planning & Disaster Risk Reduction Platform</p>
            </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Projected Pop (2024)", f"{city['pop_2024']:,}")
        m2.metric("Land Area", f"{city['area']} km²")
        m3.metric("Growth Intensity", "High")
        m4.metric("Research Status", "Active")

        st.subheader("Regional Context")
        chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('name:N', title='Barangay'),
            y=alt.Y('p24:Q', title='2024 Population'),
            color=alt.condition(alt.datum.name == target_bgy, alt.value('#10b981'), alt.value('#cbd5e1'))
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)

    # --- TAB 2: GEOSPATIAL STUDIO ---
    with t2:
        st.subheader("Interactive Planning Map")
        col_map, col_info = st.columns([3, 1])
        
        with col_map:
            m = folium.Map(location=city['coords'], zoom_start=13, tiles="CartoDB Positron")
            for _, row in df.iterrows():
                is_target = row['name'] == target_bgy
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=row['p24']/1500 if theme == "Population Density" else 10,
                    color="#10b981" if is_target else "#3b82f6",
                    fill=True,
                    popup=f"<b>{row['name']}</b><br>Pop: {row['p24']:,}"
                ).add_to(m)
            folium_static(m, width=850)

        with col_info:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{target_bgy} Focus</h4>
                    <p><b>2024 Pop:</b> {bgy_data['p24']:,}</p>
                    <p><b>Growth Rate:</b> {bgy_data['gr']}%</p>
                    <hr>
                    <small>Layer: {theme}</small>
                </div>
            """, unsafe_allow_html=True)

    # --- TAB 3: RESILIENCE AI ---
    with t3:
        st.subheader("Parametric Risk Assessment")
        c1, c2, c3, c4 = st.columns(4)
        f_risk = c1.select_slider("Flood Exposure", options=["Low", "Moderate", "High"])
        w_risk = c2.select_slider("Waste Mgmt", options=["Good", "Fair", "Poor"])
        d_risk = c3.select_slider("Drainage Info", options=["Good", "Fair", "Poor"])
        p_risk = c4.select_slider("Density Strain", options=["Low", "Moderate", "High"])

        status, color, desc = calculate_risk(f_risk, w_risk, d_risk, p_risk)
        
        st.markdown(f"""
            <div style="background:{color}; color:white; padding:2rem; border-radius:1rem; text-align:center;">
                <h2 style="color:white;">STATUS: {status}</h2>
                <p>{desc}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- TAB 4: RESEARCH OUTPUT ---
    with t4:
        st.subheader("Automated Thesis Documentation")
        if st.button("Generate Professional Map Plate"):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(df['lon'], df['lat'], c='#cbd5e1', s=50, label="Adjacent Barangays")
            ax.scatter(bgy_data['lon'], bgy_data['lat'], c='#10b981', s=200, label=f"Target: {target_bgy}", edgecolors='black')
            cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.CartoDB.Positron)
            ax.set_axis_off()
            ax.set_title(f"Planning Context: {target_bgy}, Butuan City", fontsize=14, pad=10)
            plt.legend(loc='lower right')
            st.pyplot(fig)
            
            st.markdown(f"""
                <div class="report-box">
                    <h4>Figure Caption:</h4>
                    <p><i>Figure 1.1 Spatial distribution and thematic planning reference for {target_bgy}, Butuan City. 
                    Visualized using Eco-Resilience AI Platform v2.1.</i></p>
                    <br>
                    <h4>Analysis Summary:</h4>
                    <p>The barangay of {target_bgy} shows a growth rate of {bgy_data['gr']}%. 
                    Under current {f_risk} flood exposure levels, the area is categorized as <b>{status}</b>. 
                    Recommended action: {desc}</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
