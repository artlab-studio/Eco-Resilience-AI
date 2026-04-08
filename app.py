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
# 1. UI ARCHITECTURE & THEME ENGINE
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
            text-transform: uppercase;
        }
        div.stButton > button:hover {
            background-color: #23867f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Card Styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATASET (LiDAR & DEMOGRAPHICS)
# ==========================================
@st.cache_data
def get_butuan_technical_data():
    city_meta = {
        "Project": "LiDAR-Based Flood Hazard Mapping",
        "Source": "UP DREAM / LIPAD / NAMRIA",
        "CRS": "UTM Zone 52N / PRS92",
        "Data_Year": 2017,
        "Datum": "WGS 84 / PRS92"
    }
    
    # 2024 Population Estimates & LiDAR Risk Profiles
    data = [
        {"name": "Ambago", "p15": 12656, "p20": 13634, "p24": 15523, "lat": 8.9430, "lon": 125.5340, "lidar_flood": "High (Level 3)", "zone": "R-2"},
        {"name": "Ampayon", "p15": 12720, "p20": 13820, "p24": 13872, "lat": 8.9700, "lon": 125.5600, "lidar_flood": "Moderate (Level 2)", "zone": "INST"},
        {"name": "Baan KM 3", "p15": 11308, "p20": 14539, "p24": 15066, "lat": 8.9570, "lon": 125.5320, "lidar_flood": "High (Level 3)", "zone": "C-2"},
        {"name": "Doongan", "p15": 13728, "p20": 13814, "p24": 14591, "lat": 8.9420, "lon": 125.5510, "lidar_flood": "High (Level 3)", "zone": "R-1"},
        {"name": "Libertad", "p15": 21703, "p20": 25296, "p24": 24880, "lat": 8.9500, "lon": 125.5170, "lidar_flood": "Low (Level 1)", "zone": "C-3"},
        {"name": "Obrero", "p15": 9774, "p20": 8643, "p24": 8505, "lat": 8.9490, "lon": 125.5430, "lidar_flood": "Moderate (Level 2)", "zone": "IND-1"},
        {"name": "San Vicente", "p15": 16187, "p20": 19500, "p24": 20369, "lat": 8.9640, "lon": 125.5400, "lidar_flood": "Moderate (Level 2)", "zone": "R-2"}
    ]
    df = pd.DataFrame(data)
    df['Pop_Change'] = df['p24'] - df['p20']
    return city_meta, df

# ==========================================
# 3. GEODETIC TITLE BLOCK GENERATOR
# ==========================================
def render_geodetic_title_block(ax, bgy_name, map_type, city_meta):
    # Draw White Box for Title Block
    rect = plt.Rectangle((0.68, 0.02), 0.30, 0.30, transform=ax.transAxes, 
                          facecolor='white', edgecolor='black', linewidth=1.5, zorder=10)
    ax.add_patch(rect)
    
    t_start = 0.69
    ax.text(t_start, 0.28, "REPUBLIC OF THE PHILIPPINES", transform=ax.transAxes, fontsize=7, fontweight='bold')
    ax.text(t_start, 0.26, "CITY GOVERNMENT OF BUTUAN", transform=ax.transAxes, fontsize=6)
    ax.text(t_start, 0.23, "OFFICE OF THE CITY PLANNER", transform=ax.transAxes, fontsize=6, fontweight='bold')
    ax.text(t_start, 0.19, f"MAP: {map_type.upper()}", transform=ax.transAxes, fontsize=8, color='#d32f2f', fontweight='bold')
    ax.text(t_start, 0.15, f"SITE: BARANGAY {bgy_name.upper()}", transform=ax.transAxes, fontsize=7)
    ax.text(t_start, 0.12, "REF: LiDAR (LIPAD 2017) / MGB", transform=ax.transAxes, fontsize=5, fontstyle='italic')
    ax.text(t_start, 0.09, f"PRINT DATE: {datetime.now().strftime('%Y-%m-%d')}", transform=ax.transAxes, fontsize=5)
    ax.text(t_start, 0.06, f"DATUM: {city_meta['Datum']}", transform=ax.transAxes, fontsize=5)

# ==========================================
# 4. MAIN APP LOGIC
# ==========================================
def main():
    apply_professional_theme()
    city_meta, df = get_butuan_technical_data()

    # --- TOP HEADER ---
    st.markdown(f"""
        <div class="eng-header">
            <h1 style='margin:0; letter-spacing: 1px;'>Eco-Resilience AI: Technical Data Portal</h1>
            <p style='margin:0; opacity:0.8;'>ONE-STOP GIS & DEMOGRAPHIC REPOSITORY | BUTUAN CITY</p>
        </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("📋 ANALYSIS PARAMETERS")
        target_bgy = st.selectbox("Focus Area", df['name'].tolist())
        map_view = st.radio("Analytical Framework", 
                           ["LiDAR Flood Hazard (5yr)", "NAMRIA Topographic", "Land Use (Zoning Map)", "Environmental (Sun/Wind)"])
        
        st.markdown("---")
        st.header("📥 EXPORT OPTIONS")
        st.button("💾 Generate Map Plate (PNG)")
        st.button("📊 Download Analysis (CSV)")
        
        st.markdown("---")
        st.caption("v3.2 Stable | Standard Engineering Resolution")

    bgy_data = df[df['name'] == target_bgy].iloc[0]

    # --- TABS ---
    tab_stats, tab_gis, tab_envi = st.tabs(["📉 Demographics & Charts", "🗺️ Technical GIS Studio", "📐 Architectural Analysis"])

    # --- TAB 1: DEMOGRAPHICS ---
    with tab_stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Est. Pop 2024", f"{bgy_data['p24']:,}")
        col2.metric("LiDAR Risk Level", bgy_data['lidar_flood'])
        col3.metric("Zoning Classification", bgy_data['zone'])
        col4.metric("Annual Growth", f"{bgy_data['Pop_Change']:,} net")

        st.markdown("### Regional Comparative Analysis")
        c1, c2 = st.columns([2, 1])
        with c1:
            bar = alt.Chart(df).mark_bar(size=45).encode(
                x=alt.X('name:N', title="Barangay"),
                y=alt.Y('p24:Q', title="2024 Population"),
                color=alt.condition(alt.datum.name == target_bgy, alt.value('#2AA198'), alt.value('#BDC3C7'))
            ).properties(height=400)
            st.altair_chart(bar, use_container_width=True)
        with c2:
            st.markdown("**Data Matrix**")
            st.dataframe(df[['name', 'p24', 'lidar_flood', 'zone']], height=380, use_container_width=True)

    # --- TAB 2: GIS STUDIO (FIXED) ---
    with tab_gis:
        st.subheader("Geospatial Visualization")
        
        # 1. Initialize Map with stable tiles
        m = folium.Map(
            location=[bgy_data['lat'], bgy_data['lon']], 
            zoom_start=15, 
            tiles='CartoDB Positron'
        )
        
        # 2. Add alternative layers with correct attribution (Fixes ValueError)
        folium.TileLayer('OpenStreetMap', name="Street Map").add_to(m)
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name="Terrain-Hybrid View",
            overlay=False
        ).add_to(m)

        # 3. LiDAR Simulation Overlay
        if "Flood" in map_view:
            pts = [[bgy_data['lat']+0.004, bgy_data['lon']-0.004], 
                   [bgy_data['lat']-0.004, bgy_data['lon']-0.004],
                   [bgy_data['lat']-0.004, bgy_data['lon']+0.004],
                   [bgy_data['lat']+0.004, bgy_data['lon']+0.004]]
            folium.Polygon(locations=pts, color="#d32f2f", fill=True, fill_opacity=0.35, 
                           popup="LiDAR-Derived Hazard Zone").add_to(m)

        folium.LayerControl().add_to(m)
        folium_static(m, width=1100, height=500)

        st.markdown("---")
        st.subheader("Professional Map Plate (Geodetic Standard)")
        
        # STATIC MAP PLATE GENERATION
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.scatter(bgy_data['lon'], bgy_data['lat'], c='red', s=250, marker='+', linewidth=2, label="Site Centroid")
        
        try:
            cx.add_basemap(ax, crs='EPSG:4326', source=cx.providers.Esri.WorldImagery)
        except:
            ax.set_facecolor('#d1d1d1')

        # Add Title Block
        render_geodetic_title_block(ax, target_bgy, map_view, city_meta)

        # North Arrow
        ax.annotate('N', xy=(0.05, 0.92), xytext=(0.05, 0.82),
                    arrowprops=dict(facecolor='black', width=4, headwidth=12),
                    xycoords='axes fraction', ha='center', fontsize=20, fontweight='bold')

        ax.set_axis_off()
        st.pyplot(fig)

    # --- TAB 3: ARCHITECTURAL ENVIRONMENTAL ---
    with tab_envi:
        st.subheader("Site-Specific Environmental Diagrams")
        st.info("These diagrams use polar coordinate systems to visualize solar and wind vectors for Butuan City ($8.95^\circ$N).")
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("#### ☀️ Annual Sun Path Diagram")
            fig_sun, ax_sun = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6,6))
            theta = np.linspace(0, 2*np.pi, 100)
            ax_sun.plot(theta, [0.8]*100, color='orange', lw=3, label='Summer Solstice Zenith')
            ax_sun.plot(theta, [0.4]*100, color='gold', ls='--', label='Equinox Path')
            ax_sun.set_theta_zero_location('N')
            ax_sun.set_theta_direction(-1)
            ax_sun.set_yticklabels([])
            ax_sun.legend(loc='lower right', fontsize=8)
            st.pyplot(fig_sun)

        with col_e2:
            st.markdown("#### 🌬️ Wind Rose (Amihan & Habagat)")
            fig_wind, ax_wind = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6,6))
            # Amihan (NE)
            ax_wind.bar([np.pi/4], [1.0], width=0.4, color='#2AA198', alpha=0.7, label='Amihan (NE)')
            # Habagat (SW)
            ax_wind.bar([5*np.pi/4], [0.8], width=0.4, color='#d32f2f', alpha=0.7, label='Habagat (SW)')
            ax_wind.set_theta_zero_location('N')
            ax_wind.set_theta_direction(-1)
            ax_wind.set_yticklabels([])
            ax_wind.legend(loc='lower right', fontsize=8)
            st.pyplot(fig_wind)

if __name__ == "__main__":
    main()
