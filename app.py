import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import altair as alt
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Eco-Resilience AI | Butuan City",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS for Glassmorphism and UI Elegance
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url('https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        padding: 60px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }

    .stButton>button {
        border-radius: 10px;
        padding: 10px 24px;
        background-color: #2e7d32;
        color: white;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #1b5e20;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    h1, h2, h3 { color: #1e3a5f; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# DATA INITIALIZATION
# ==========================================
def load_data():
    # City General Info
    city_info = {
        "Name": "Butuan City",
        "Region": "Caraga (Region XIII)",
        "Type": "Highly Urbanized City",
        "Barangays": 86,
        "Pop2020": 372910,
        "Pop2024": 385530,
        "LandArea": 816.62,
        "Density": 457,
        "Lat": 8.9534,
        "Lon": 125.5288
    }

    # Barangay dataset
    data = [
        {"Barangay": "Ambago", "Pop2015": 12656, "Pop2020": 13634, "Pop2024": 15523, "Growth": 1.58, "Lat": 8.9430, "Lon": 125.5340},
        {"Barangay": "Ampayon", "Pop2015": 12720, "Pop2020": 13820, "Pop2024": 13872, "Growth": 1.76, "Lat": 8.9700, "Lon": 125.5600},
        {"Barangay": "Baan KM 3", "Pop2015": 11308, "Pop2020": 14539, "Pop2024": 15066, "Growth": 5.43, "Lat": 8.9570, "Lon": 125.5320},
        {"Barangay": "Doongan", "Pop2015": 13728, "Pop2020": 13814, "Pop2024": 14591, "Growth": 0.13, "Lat": 8.9420, "Lon": 125.5510},
        {"Barangay": "Libertad", "Pop2015": 21703, "Pop2020": 25296, "Pop2024": 24880, "Growth": 3.28, "Lat": 8.9500, "Lon": 125.5170},
        {"Barangay": "Obrero", "Pop2015": 9774, "Pop2020": 8643, "Pop2024": 8505, "Growth": -2.56, "Lat": 8.9490, "Lon": 125.5430},
        {"Barangay": "San Vicente", "Pop2015": 16187, "Pop2020": 19500, "Pop2024": 20369, "Growth": 4.00, "Lat": 8.9640, "Lon": 125.5400}
    ]
    df = pd.DataFrame(data)
    df['PopChange'] = df['Pop2024'] - df['Pop2020']
    return city_info, df

city_info, bgy_df = load_data()

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-city-smart-city-flatart-icons-flat-flatarticons-1.png", width=80)
    st.title("Control Center")
    st.markdown("---")
    
    selected_bgy = st.selectbox("🎯 Select Barangay Focus", bgy_df['Barangay'].tolist())
    map_theme = st.selectbox("🗺️ Select Map Theme", 
                             ["Population Map", "Flood Hazard Reference", "Rain-Induced Landslide Reference", "Topographic Reference", "Integrated Risk View"])
    
    planning_focus = st.selectbox("🌱 Planning Focus", ["Integrated", "DRRM", "Circular Economy"])
    
    st.markdown("---")
    st.subheader("Map Visuals")
    basemap_option = st.selectbox("Interactive Basemap", ["OpenStreetMap", "CartoDB Positron", "CartoDB Voyager"])
    static_basemap = st.selectbox("Map Plate Basemap", ["CartoDB Positron", "OpenStreetMap"])
    
    st.markdown("---")
    st.info("**Research Guide:** This platform is designed for preliminary academic planning. Data points are approximate for prototype demonstration.")

# Get focused data
focus_data = bgy_df[bgy_df['Barangay'] == selected_bgy].iloc[0]

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard Overview", 
    "📊 Demographics", 
    "🗺️ Interactive Studio", 
    "🤖 AI Assessment", 
    "📜 Thesis Map Generator"
])

# ------------------------------------------
# TAB 1: DASHBOARD
# ------------------------------------------
with tab1:
    st.markdown(f"""
        <div class="hero-container">
            <h1 style='color: white; margin-bottom: 0;'>Eco-Resilience AI Platform</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Decision Support System for Butuan City Urban Resilience</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Population 2024 (Est)", f"{city_info['Pop2024']:,}")
    col2.metric("Land Area", f"{city_info['LandArea']} km²")
    col3.metric("Barangays", city_info['Barangays'])
    col4.metric("Density", f"{city_info['Density']}/km²")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Mission & Scope")
        st.write("""
            This platform serves as a unified digital environment for architects, environmental planners, and researchers 
            studying **Butuan City**. By synthesizing fragmented demographic data and spatial references, we empower 
            evidence-based decision-making for Disaster Risk Reduction (DRRM) and Circular Economy initiatives.
        """)
        st.success("**Quick Planning Insight:** Coastal and riverside barangays in Butuan require priority drainage rehabilitation due to high 2024 population growth in low-lying areas.")
    with c2:
        st.write("Current Focus Area")
        st.info(f"**{selected_bgy}**")
        st.write(f"Focusing on **{planning_focus}** strategy.")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: DEMOGRAPHICS
# ------------------------------------------
with tab2:
    st.header("📊 Demographic Research Portal")
    
    # Barangay Selector / Stats
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    sub_col1, sub_col2 = st.columns([1, 2])
    with sub_col1:
        st.subheader("Barangay Profile")
        st.write(f"**Name:** {focus_data['Barangay']}")
        st.write(f"**2024 Pop:** {focus_data['Pop2024']:,}")
        st.write(f"**Growth Rate:** {focus_data['Growth']}%")
        st.write(f"**Net Change (20-24):** {focus_data['PopChange']:,}")
    with sub_col2:
        # Mini Chart
        chart_data = pd.DataFrame({
            'Year': ['2015', '2020', '2024'],
            'Population': [focus_data['Pop2015'], focus_data['Pop2020'], focus_data['Pop2024']]
        })
        line_chart = alt.Chart(chart_data).mark_line(point=True, color='#2e7d32').encode(
            x='Year', y='Population'
        ).properties(height=200)
        st.altair_chart(line_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Comparison Charts
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Barangay Population Distribution (2024)**")
        bar1 = alt.Chart(bgy_df).mark_bar().encode(
            x='Pop2024', y=alt.Y('Barangay', sort='-x'), color=alt.value('#2e7d32')
        )
        st.altair_chart(bar1, use_container_width=True)
    with col_b:
        st.markdown("**Population Change (2020-2024)**")
        bar2 = alt.Chart(bgy_df).mark_bar().encode(
            x='PopChange', y=alt.Y('Barangay', sort='-x'), 
            color=alt.condition(alt.datum.PopChange > 0, alt.value('#2e7d32'), alt.value('#d32f2f'))
        )
        st.altair_chart(bar2, use_container_width=True)

    st.dataframe(bgy_df.drop(columns=['Lat', 'Lon']), use_container_width=True)

# ------------------------------------------
# TAB 3: INTERACTIVE MAP STUDIO
# ------------------------------------------
with tab3:
    st.header("🗺️ Interactive Geospatial Studio")
    
    col_m1, col_m2 = st.columns([3, 1])
    
    with col_m1:
        # Folium Map
        m = folium.Map(location=[city_info['Lat'], city_info['Lon']], zoom_start=13, tiles=basemap_option)
        
        for idx, row in bgy_df.iterrows():
            is_selected = row['Barangay'] == selected_bgy
            color = 'red' if is_selected else 'blue'
            radius = (row['Pop2024'] / 1000) * 2 if map_theme == "Population Map" else 6
            
            # Add Marker
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=radius,
                color=color,
                fill=True,
                fill_opacity=0.6,
                popup=f"{row['Barangay']}: {row['Pop2024']:,} pop",
                tooltip=row['Barangay']
            ).add_to(m)
        
        folium_static(m, width=900)
    
    with col_m2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Legend & Insights")
        st.write(f"**Theme:** {map_theme}")
        st.write(f"**Focus:** {selected_bgy}")
        st.divider()
        if map_theme == "Population Map":
            st.write("Circle size corresponds to 2024 population density.")
        else:
            st.info(f"Visualizing {map_theme} overlay. This is a preliminary spatial assessment for academic research.")
        
        st.warning("⚠️ Points are approximate reference centroids. Future upgrades should integrate official .geojson boundaries.")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: AI PLANNING ASSESSMENT
# ------------------------------------------
with tab4:
    st.header("🤖 AI-Assisted Assessment")
    
    with st.expander("Configure Assessment Parameters", expanded=True):
        ac1, ac2, ac3, ac4 = st.columns(4)
        flood = ac1.selectbox("Flood Exposure", ["Low", "Moderate", "High"])
        waste = ac2.selectbox("Waste Management", ["Good", "Fair", "Poor"])
        drain = ac3.selectbox("Drainage Condition", ["Good", "Fair", "Poor"])
        pop_ex = ac4.selectbox("Population Exposure", ["Low", "Moderate", "High"])

    # Logic
    score_map = {"Low": 1, "Moderate": 2, "High": 3, "Good": 1, "Fair": 2, "Poor": 3}
    total_score = score_map[flood] + score_map[waste] + score_map[drain] + score_map[pop_ex]
    
    risk_level = "LOW"
    risk_color = "green"
    if total_score >= 10:
        risk_level = "HIGH"
        risk_color = "red"
    elif total_score >= 7:
        risk_level = "MODERATE"
        risk_color = "orange"

    st.markdown(f"""
        <div style="background-color: {risk_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin:0;">Composite Risk Score: {total_score} / 12</h2>
            <h3 style="color: white; margin:0;">Priority Level: {risk_level}</h3>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Planning Recommendations")
    recs = []
    if planning_focus == "DRRM":
        recs = ["Implement community-based early warning systems.", "Upgrade evacuation center facilities.", "Map household-level vulnerability."]
    elif planning_focus == "Circular Economy":
        recs = ["Introduce barangay-level Materials Recovery Facility (MRF).", "Implement 'Plastic-to-Road' initiatives.", "Encourage composting for urban gardening."]
    else:
        recs = ["Integrate blue-green infrastructure into land use plans.", "Conduct periodic climate-risk audits.", "Strengthen multi-stakeholder resilience councils."]

    for r in recs:
        st.write(f"✅ {r}")

    # Factor Breakdown Chart
    breakdown_df = pd.DataFrame({
        'Factor': ['Flood', 'Waste', 'Drainage', 'Population'],
        'Score': [score_map[flood], score_map[waste], score_map[drain], score_map[pop_ex]]
    })
    breakdown_chart = alt.Chart(breakdown_df).mark_bar().encode(
        x='Score', y='Factor', color=alt.value(risk_color)
    ).properties(height=150)
    st.altair_chart(breakdown_chart, use_container_width=True)

# ------------------------------------------
# TAB 5: THESIS MAP GENERATOR
# ------------------------------------------
with tab5:
    st.header("📜 Thesis Map Generator")
    st.write("Generate a standardized, high-resolution map plate for your academic documents.")

    if st.button("Generate Map Plate"):
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot all points
        ax.scatter(bgy_df['Lon'], bgy_df['Lat'], c='blue', s=50, alpha=0.5, label='Other Barangays')
        # Highlight selected
        ax.scatter(focus_data['Lon'], focus_data['Lat'], c='red', s=200, edgecolors='black', label=f'Focus: {selected_bgy}')
        
        # Add Basemap
        try:
            cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.CartoDB.Positron)
        except:
            pass # Fallback if provider is down
            
        ax.set_title(f"{map_theme.upper()}\n{selected_bgy}, Butuan City", fontsize=16, fontweight='bold', pad=20)
        ax.legend()
        
        # Text Blocks (Title Block Style)
        plt.figtext(0.15, 0.05, f"Source: Eco-Resilience AI Platform | Reference: Census 2020-2024\nNote: Approximate Centroids Used.", fontsize=8, style='italic')
        plt.figtext(0.75, 0.05, "NORTH ↑", fontsize=12, fontweight='bold')
        
        st.pyplot(fig)
        
        st.markdown("### Thesis-Ready Documentation")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            caption = f"**Figure 1.** {map_theme} map of {selected_bgy}, Butuan City, showing the selected barangay in relation to nearby context and thematic planning reference."
            st.info(caption)
            st.button("Copy Caption", on_click=lambda: st.write("Caption Copied! (Simulated)"))
        with col_c2:
            source_note = "Source: Prepared by the researcher through the Eco-Resilience AI Platform using demographic reference data, web basemap support, and prototype barangay reference points. Official barangay GIS boundaries are recommended for final spatial outputs."
            st.code(source_note, language=None)

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
        <strong>Eco-Resilience AI Platform | Butuan City Research Portal</strong><br>
        Developed for Academic & Innovation Presentation Purposes. <br>
        <em>Future Upgrades: Integration of official GeoJSON boundaries, real-time satellite flood monitoring, and WMS hazard layers.</em>
    </div>
    """, unsafe_allow_html=True
)
