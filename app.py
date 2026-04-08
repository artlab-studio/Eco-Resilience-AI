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
# 1. ARCHITECTURAL UI & THEME ENGINE
# ==========================================
st.set_page_config(
    page_title="Eco-Resilience AI | LiDAR & Planning Portal",
    page_icon="📐",
    layout="wide"
)

def apply_professional_theme():
    st.markdown("""
        <style>
        :root {
            --header-bg: #002B36;
            --accent-teal: #2AA198;
            --panel-bg: #FFFFFF;
        }
        .stApp { background-color: #F4F7F6; }
        
        /* Engineering Header */
        .eng-header {
            background-color: var(--header-bg);
            color: white;
            padding: 2.5rem;
            border-left: 10px solid var(--accent-teal);
            border-radius: 0 10px 10px 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        /* Professional Buttons */
        div.stButton > button {
            background-color: var(--accent-teal);
            color: white;
            border-radius: 4px;
            font-weight: 600;
            height: 3em;
            width: 100%;
            border: none;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #23867f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Title Block Styling */
        .title-block-text {
            font-family: 'Courier New', Courier, monospace;
            line-height: 1.2;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE DATA & LIDAR CONFIG
# ==========================================
@st.cache_data
def get_butuan_technical_data():
    # Technical Metadata derived from UP DREAM / LIPAD (2017 LiDAR)
    city_meta = {
        "Project": "LiDAR-Based Flood Hazard Mapping",
        "Source": "UP DREAM / LIPAD / NAMRIA",
        "CRS": "UTM Zone 52N / PRS92",
        "Data_Year": 2017
    }
    
    # Barangay Matrix with LiDAR-based risk approximations
    data = [
        {"name": "Ambago", "p24": 15523, "lat": 8.9430, "lon": 125.5340, "lidar_flood": "High (Level 3)", "zone": "R-2"},
        {"name": "Ampayon", "p24": 13872, "lat": 8.9700, "lon": 125.5600, "lidar_flood": "Moderate (Level 2)", "zone": "INST"},
        {"name": "Baan KM 3", "p24": 15066, "lat": 8.9570, "lon": 125.5320, "lidar_flood": "High (Level 3)", "zone": "C-2"},
        {"name": "Doongan", "p24": 14591, "lat": 8.9420, "lon": 125.5510, "lidar_flood": "High (Level 3)", "zone": "R-1"},
        {"name": "Libertad", "p24": 24880, "lat": 8.9500, "lon": 125.5170, "lidar_flood": "Low (Level 1)", "zone": "C-3"},
        {"name": "Obrero", "p24": 8505, "lat": 8.9490, "lon": 125.5430, "lidar_flood": "Moderate (Level 2)", "zone": "IND-1"},
        {"name": "San Vicente", "p24": 20369, "lat": 8.9640, "lon": 125.5400, "lidar_flood": "Moderate (Level 2)", "zone": "R-2"}
    ]
    return city_meta, pd.DataFrame(data)

# ==========================================
# 3. GEODETIC TITLE BLOCK GENERATOR
# ==========================================
def render_geodetic_title_block(ax, bgy_name, map_type):
    # Professional Title Block in Matplotlib
    rect = plt.Rectangle((0.68, 0.02), 0.30, 0.28, transform=ax.transAxes, 
                          facecolor='white', edgecolor='black', linewidth=1.5, zorder=10)
    ax.add_patch(rect)
    
    t_start = 0.69
    ax.text(t_start, 0.26, "REPUBLIC OF THE PHILIPPINES", transform=ax.transAxes, fontsize=7, fontweight='bold')
    ax.text(t_start, 0.24, "CITY GOVERNMENT OF BUTUAN", transform=ax.transAxes, fontsize=6)
    ax.text(t_start, 0.21, f"OFFICE OF THE CITY PLANNER", transform=ax.transAxes, fontsize=6, fontweight='bold')
    ax.text(t_start, 0.17, f"MAP: {map_type.upper()}", transform=ax.transAxes, fontsize=8, color='#d32f2f', fontweight='bold')
    ax.text(t_start, 0.14, f"SITE: BARANGAY {bgy_name.upper()}", transform=ax.transAxes, fontsize=7)
    ax.text(t_start, 0.11, "REF: LiDAR (LIPAD 2017) / MGB", transform=ax.transAxes, fontsize=5, fontstyle='italic')
    ax.text(t_start, 0.08, f"PRINT DATE: {datetime.now().strftime('%Y-%m-%d')}", transform=ax.transAxes, fontsize=5)
    ax.text(t_start, 0.05, "COORD REF: PRS92 / WGS 84 DATUM", transform=ax.transAxes, fontsize=5)

# ==========================================
# 4. MAIN APP INTERFACE
# ==========================================
def main():
    apply_professional_theme()
    city_meta, df = get_butuan_technical_data()

    # --- HEADER ---
    st.markdown(f"""
        <div class="eng-header">
            <h1 style='margin:0; letter-spacing: 1px;'>Eco-Resilience AI: Technical Data Portal</h1>
            <p style='margin:0; opacity:0.8;'>LIDAR-SUPPORTED PLANNING & RESEARCH | BUTUAN CITY</p>
        </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("📋 ANALYSIS PARAMETERS")
        target_bgy = st.selectbox("Focus Area", df['name'].tolist())
        map_view = st.radio("Map Framework", 
                           ["LiDAR Flood Hazard (5yr)", "NAMRIA Topographic", "Land Use (Zoning)", "Sun/Wind Analysis"])
        
        st.markdown("---")
        st.header("📥 DATA EXPORT")
        st.button("📄 Export Thesis Map Plate")
        st.button("📊 Download Demographic CSV")
        
        st.markdown("---")
        st.caption("v3.0 Prototype | Geodetic Engineering Standard")

    bgy_data = df[df['name'] == target_bgy].iloc[0]

    # --- TABS ---
    tab_stats, tab_gis, tab_envi = st.tabs(["📉 Analytical Metrics", "🗺️ GIS LiDAR Studio", "📐 Arch-Environmental"])

    # --- TAB 1: METRICS ---
    with tab_stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Projected Pop 2024", f"{bgy_data['p24']:,}")
        col2.metric("LiDAR Risk Level", bgy_data['lidar_flood'])
        col3.metric("Zoning Code", bgy_data['zone'])
        col4.metric("Data Accuracy", "High (LiDAR)")

        st.subheader("Regional Comparative Analysis")
        c1, c2 = st.columns([2, 1])
        with c1:
            bar = alt.Chart(df).mark_bar(size=40).encode(
                x=alt.X('name:N', title="Barangay"),
                y=alt.Y('p24:Q', title="2024 Population Estimate"),
                color=alt.condition(alt.datum.name == target_bgy, alt.value('#2AA198'), alt.value('#BDC3C7'))
            ).properties(height=400)
            st.altair_chart(bar, use_container_width=True)
        with c2:
            st.info("**Researcher Note:**")
            st.write(f"Barangay **{target_bgy}** is identified as a **{bgy_data['lidar_flood']}** zone. Site-level mitigation must prioritize high-capacity drainage systems aligned with the LiDAR elevation profiles.")
            st.dataframe(df[['name', 'p24', 'lidar_flood', 'zone']], height=300)

    # --- TAB 2: GIS STUDIO ---
    with tab_gis:
        st.subheader("LiDAR-Integrated Map Viewer")
        
        # INTERACTIVE GIS
        m = folium.Map(location=[bgy_data['lat'], bgy_data['lon']], zoom_start=15, tiles='CartoDB Positron')
        
        # Add a Layer Control
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer('Stamen Terrain').add_to(m)

        # Simulation of LIPAD Flood Overlay
        if "Flood" in map_view:
            # Drawing a simulated LiDAR-derived hazard polygon
            points = [[bgy_data['lat']+0.005, bgy_data['lon']-0.005], 
                      [bgy_data['lat']-0.005, bgy_data['lon']-0.005],
                      [bgy_data['lat']-0.005, bgy_data['lon']+0.005],
                      [bgy_data['lat']+0.005, bgy_data['lon']+0.005]]
            folium.Polygon(locations=points, color="red", fill=True, fill_color="red", fill_opacity=0.3, popup="LiDAR 5yr Flood Zone").add_to(m)

        folium_static(m, width=1100, height=500)

        st.markdown("---")
        st.subheader("Professional Presentation Plate")
        
        # STATIC PLATE GENERATION
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.scatter(bgy_data['lon'], bgy_data['lat'], c='red', s=200, marker='+', linewidth=2, label="Reference Point")
        
        try:
            cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.Esri.WorldImagery)
        except:
            ax.set_facecolor('#d1d1d1')

        # Generate Title Block
        render_geodetic_title_block(ax, target_bgy, map_view)

        # North Arrow
        ax.annotate('N', xy=(0.05, 0.9), xytext=(0.05, 0.8),
                    arrowprops=dict(facecolor='black', width=4, headwidth=12),
                    xycoords='axes fraction', ha='center', fontsize=20, fontweight='bold')

        ax.set_axis_off()
        st.pyplot(fig)

    # --- TAB 3: ENVIRONMENTAL ---
    with tab_envi:
        st.subheader("Architectural Climate Analysis")
        col_env1, col_env2 = st.columns(2)

        with col_env1:
            st.markdown("### ☀️ Sun Path Orientation")
            fig_sun, ax_sun = plt.subplots(subplot_kw={'projection': 'polar'})
            # Simulated sun angles for 8.9° N (Butuan)
            theta = np.linspace(0, 2*np.pi, 100)
            ax_sun.plot(theta, [0.7]*100, color='orange', label='Zenith Path')
            ax_sun.set_theta_zero_location('N')
            ax_sun.set_theta_direction(-1)
            ax_sun.set_yticklabels([])
            st.pyplot(fig_sun)
            st.caption("Polar Plot: Solar orientation at 8.95° Latitude.")

        with col_env2:
            st.markdown("### 🌬️ Prevailing Wind (Amihan/Habagat)")
            fig_wind, ax_wind = plt.subplots(subplot_kw={'projection': 'polar'})
            # NE Wind (Amihan) and SW Wind (Habagat)
            ax_wind.bar([np.pi/4, 5*np.pi/4], [1, 0.7], width=0.4, color='teal', alpha=0.6)
            ax_wind.set_theta_zero_location('N')
            ax_wind.set_theta_direction(-1)
            ax_wind.set_yticklabels([])
            st.pyplot(fig_wind)
            st.caption("Wind Rose: Primary vectors for Caraga Region.")

if __name__ == "__main__":
    main()
