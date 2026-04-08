import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import contextily as cx
import altair as alt
from datetime import datetime

# ==========================================
# 1. SETUP & THEMING
# ==========================================
st.set_page_config(
    page_title="Eco-Resilience AI Platform",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main UI and Glassmorphism */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hero Section */
        .hero-section {
            background: linear-gradient(rgba(0, 43, 54, 0.8), rgba(0, 43, 54, 0.8)), 
                        url('https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            padding: 80px 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 20px;
        }

        .stButton>button {
            border-radius: 8px;
            background-color: #2AA198;
            color: white;
            font-weight: 600;
            padding: 0.6rem 2rem;
            border: none;
            transition: 0.3s;
        }

        .stButton>button:hover {
            background-color: #23867f;
            box-shadow: 0 4px 15px rgba(42, 161, 152, 0.4);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #002B36;
        }
        section[data-testid="stSidebar"] .css-ng1t4o {
            color: #93a1a1;
        }

        h1, h2, h3 { color: #002B36; font-weight: 700; }
        .disclaimer-text {
            font-size: 0.75rem;
            color: #64748b;
            font-style: italic;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_city_data():
    city_summary = {
        "Name": "Butuan City",
        "Pop2020": 372910,
        "Pop2024": 385530,
        "Area": 816.62,
        "Coords": [8.9534, 125.5288]
    }
    
    # Barangay Data Simulation
    data = [
        {"name": "Ambago", "p15": 12656, "p20": 13634, "p24": 15523, "lat": 8.9430, "lon": 125.5340, "risk": "High", "zone": "R-2"},
        {"name": "Ampayon", "p15": 12720, "p20": 13820, "p24": 14200, "lat": 8.9700, "lon": 125.5600, "risk": "Moderate", "zone": "INST"},
        {"name": "Baan KM 3", "p15": 11308, "p20": 14539, "p24": 15100, "lat": 8.9570, "lon": 125.5320, "risk": "High", "zone": "C-2"},
        {"name": "Doongan", "p15": 13728, "p20": 13814, "p24": 14600, "lat": 8.9420, "lon": 125.5510, "risk": "High", "zone": "R-1"},
        {"name": "Libertad", "p15": 21703, "p20": 25296, "p24": 26100, "lat": 8.9500, "lon": 125.5170, "risk": "Low", "zone": "C-3"},
        {"name": "Obrero", "p15": 9774, "p20": 8643, "p24": 9100, "lat": 8.9490, "lon": 125.5430, "risk": "Moderate", "zone": "IND-1"},
        {"name": "San Vicente", "p15": 16187, "p20": 19500, "p24": 20400, "lat": 8.9640, "lon": 125.5400, "risk": "Moderate", "zone": "R-2"}
    ]
    df = pd.DataFrame(data)
    df['Pop_Change'] = df['p24'] - df['p20']
    df['Growth_Rate'] = ((df['p24'] - df['p20']) / df['p20'] * 100).round(2)
    return city_summary, df

# ==========================================
# 3. MAP GENERATOR (TECHNICAL PLATE)
# ==========================================
def generate_professional_plate(bgy_data, theme, basemap_provider, city_meta):
    fig = plt.figure(figsize=(15, 9), constrained_layout=True)
    gs = gridspec.GridSpec(1, 2, width_ratios=[3.5, 1], figure=fig)
    
    # Left Axis: The Map
    ax_map = fig.add_subplot(gs[0])
    ax_map.scatter(bgy_data['lon'], bgy_data['lat'], c='#d32f2f', s=400, marker='X', edgecolors='white', zorder=10)
    
    # Basemap Mapping
    providers = {
        "Satellite": cx.providers.Esri.WorldImagery,
        "Terrain": cx.providers.Stamen.Terrain,
        "Light": cx.providers.CartoDB.Positron,
        "Dark": cx.providers.CartoDB.DarkMatter
    }
    
    try:
        cx.add_basemap(ax_map, crs='EPSG:4326', source=providers.get(basemap_provider, cx.providers.CartoDB.Positron))
    except:
        ax_map.set_facecolor('#e0e0e0')
        ax_map.text(0.5, 0.5, "Basemap Load Failed", ha='center')

    ax_map.set_axis_off()
    ax_map.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    xycoords='axes fraction', ha='center', fontsize=20, fontweight='bold')

    # Right Axis: Title Block
    ax_side = fig.add_subplot(gs[1])
    ax_side.set_axis_off()
    ax_side.axvline(x=0, color='black', lw=2)
    
    # Layout Text
    y = 0.95
    def write_t(txt, sz, wt='normal', clr='black', space=0.05):
        nonlocal y
        ax_side.text(0.05, y, txt, fontsize=sz, fontweight=wt, color=clr, transform=ax_side.transAxes)
        y -= space

    write_t("ECO-RESILIENCE AI PLATFORM", 12, 'bold', '#002B36')
    write_t("GEOSPATIAL PLANNING PORTAL", 8, 'normal', '#2AA198')
    y -= 0.05
    write_t("PROJECT TITLE:", 7, 'bold', 'gray')
    write_t("Butuan Planning & Research", 10, 'normal')
    y -= 0.03
    write_t("MAP THEME:", 7, 'bold', 'gray')
    write_t(theme.upper(), 10, 'bold', '#d32f2f')
    y -= 0.03
    write_t("SELECTED AREA:", 7, 'bold', 'gray')
    write_t(f"Barangay {bgy_data['name']}", 9, 'normal')
    y -= 0.15
    write_t("DATA SOURCES:", 7, 'bold', 'gray')
    write_t("NAMRIA | MGB | NOAH | DENR | PSA", 6, 'normal')
    write_t("(Referenced – Prototype Academic Use)", 5, 'italic')
    y -= 0.1
    write_t("TECHNICAL NOTES:", 7, 'bold', 'gray')
    write_t(f"Datum: PRS92 / WGS 84\nGen Date: {datetime.now().strftime('%Y-%m-%d')}\nScale: Not to Scale (NTS)", 6, space=0.1)
    
    # Disclaimer bottom
    ax_side.text(0.05, 0.05, "ACADEMIC DISCLAIMER:\nThis map is a prototype academic visualization.\nOfficial GIS datasets are required for technical\nplanning and final outputs.", 
                 fontsize=6, fontstyle='italic', transform=ax_side.transAxes)

    return fig

# ==========================================
# 4. MAIN APP LOGIC
# ==========================================
def main():
    apply_custom_styles()
    meta, df = load_city_data()

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://img.icons8.com/external-flat-icons-inorganic-studio/100/external-urban-infrastructure-flat-icons-inorganic-studio.png", width=80)
        st.markdown("<h2 style='color:white;'>Control Panel</h2>", unsafe_allow_html=True)
        
        selected_bgy_name = st.selectbox("🎯 Select Barangay", df['name'].tolist())
        map_theme = st.selectbox("🎨 Map Theme", ["Population Density", "Flood Hazard Reference", "Landslide Reference", "Topographic Reference", "Integrated Risk"])
        planning_focus = st.multiselect("🏗️ Planning Focus", ["Housing", "Ecology", "Infrastructure", "Disaster Resilience"], default=["Disaster Resilience"])
        
        st.markdown("---")
        st.markdown("### Visualization Settings")
        interactive_base = st.selectbox("Basemap (Interactive)", ["CartoDB Positron", "OpenStreetMap", "Stamen Terrain"])
        static_base = st.selectbox("Basemap (Map Plate)", ["Satellite", "Terrain", "Light", "Dark"])
        
        st.markdown("---")
        st.caption("🔍 **Platform Notes:**")
        st.caption("This platform is intended for preliminary academic and planning use only.")

    bgy_data = df[df['name'] == selected_bgy_name].iloc[0]

    # --- HERO SECTION ---
    st.markdown(f"""
        <div class="hero-section">
            <h1 style='color:white; margin-bottom:10px;'>ECO-RESILIENCE AI PLATFORM</h1>
            <p style='font-size:1.2rem; opacity:0.9;'>Early-Stage Geospatial Planning & Decision-Support System for Butuan City</p>
        </div>
    """, unsafe_allow_html=True)

    # --- TABS ---
    t1, t2, t3, t4, t5 = st.tabs([
        "📊 Dashboard Overview", 
        "👥 Population Profile", 
        "🗺️ Interactive Studio", 
        "🧠 AI Assessment", 
        "📄 Thesis Map Generator"
    ])

    # TAB 1: DASHBOARD
    with t1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Est. Population (2024)", f"{meta['Pop2024']:,}", "3.4%")
        col2.metric("Land Area", f"{meta['Area']} km²")
        col3.metric("Barangays", meta["Barangays"])
        col4.metric("Planning Status", "Preliminary")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### City Strategy Summary")
        st.write("Butuan City is positioned as a strategic hub in the Caraga Region. This platform integrates thematic layers to evaluate how urban growth interacts with environmental geohazards. Our focus is on fostering a resilient urban fabric that respects the natural hydrological and geological constraints of the Agusan River basin.")

    # TAB 2: POPULATION
    with t2:
        st.subheader(f"Demographic Profile: Brgy. {selected_bgy_name}")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.write(f"**Current Population:** {bgy_data['p24']:,}")
            st.write(f"**Net Change (2020-24):** {bgy_data['Pop_Change']}")
            st.write(f"**Growth Rate:** {bgy_data['Growth_Rate']}%")
            st.write(f"**Zoning Class:** {bgy_data['zone']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            pop_chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('name:N', sort='-y', title="Barangay"),
                y=alt.Y('p24:Q', title="2024 Population"),
                color=alt.condition(alt.datum.name == selected_bgy_name, alt.value('#2AA198'), alt.value('#cbd5e1'))
            ).properties(height=300)
            st.altair_chart(pop_chart, use_container_width=True)

    # TAB 3: INTERACTIVE STUDIO
    with t3:
        st.subheader("Spatial Decision Support Interface")
        m = folium.Map(location=[bgy_data['lat'], bgy_data['lon']], zoom_start=15, tiles=interactive_base)
        
        # Prototype marker
        folium.Marker(
            [bgy_data['lat'], bgy_data['lon']],
            popup=f"Brgy. {bgy_data['name']}",
            icon=folium.Icon(color="teal", icon="info-sign")
        ).add_to(m)
        
        folium_static(m, width=1200, height=500)
        st.markdown("<p class='disclaimer-text'>Barangay locations are approximate reference points only and do not represent official GIS boundaries.</p>", unsafe_allow_html=True)

    # TAB 4: AI ASSESSMENT
    with t4:
        st.subheader("Automated Planning Risk Assessment")
        with st.form("risk_form"):
            col_a, col_b = st.columns(2)
            flood = col_a.slider("Flood Exposure (1-3)", 1, 3, 2)
            waste = col_a.slider("Solid Waste Density (1-3)", 1, 3, 1)
            drain = col_b.slider("Drainage Capacity (1-3)", 1, 3, 2)
            pop_den = col_b.slider("Population Density (1-3)", 1, 3, 2)
            submit = st.form_submit_button("Run AI Assessment")
        
        if submit:
            risk_score = (flood + waste + drain + pop_den) / 4
            level = "High" if risk_score > 2.2 else "Moderate" if risk_score > 1.5 else "Low"
            
            st.markdown(f"""
                <div class="glass-card">
                    <h4>Assessment Result: <span style='color:#d32f2f;'>{level} Risk</span></h4>
                    <p><b>Composite Score:</b> {risk_score}/3.0</p>
                    <p><b>Interpretation:</b> The selected area shows {level.lower()} sensitivity to climate stress based on current prototype weights.</p>
                    <p><b>Recommendations:</b> Prioritize Nature-Based Solutions (NBS) and upgrade permeable surfaces to mitigate seasonal runoff.</p>
                </div>
            """, unsafe_allow_html=True)

    # TAB 5: MAP GENERATOR
    with t5:
        st.subheader("Thesis-Ready Map Plate Generator")
        st.write("Generate a formal planning plate for research documentation.")
        
        if st.button("🖼️ Render Professional Map Plate"):
            with st.spinner("Compiling technical layers..."):
                fig = generate_professional_plate(bgy_data, map_theme, static_base, meta)
                st.pyplot(fig)
            
            st.markdown("### 📝 Academic Attribution")
            source_text = "Source: Prepared by the researcher through the Eco-Resilience AI Platform using demographic reference data and prototype spatial visualization. Hazard references are aligned with NAMRIA, MGB, Project NOAH, DENR, and PSA datasets. Official GIS data is recommended for final outputs."
            st.code(source_text, language="text")
            st.write("**Disclaimer:** This map is a prototype academic visualization. Official GIS datasets are required for technical planning.")

    # --- FOOTER ---
    st.markdown("---")
    st.markdown(
        "<center><p style='color:#64748b;'>© 2024 Eco-Resilience AI Platform | Butuan City Research Initiative</p></center>", 
        unsafe_allow_html=True
    )

    # FUTURE IMPROVEMENT NOTES:
    # 1. Replace prototype thematic layers with official hazard datasets from MGB.
    # 2. Add NAMRIA GeoJSON for exact barangay polygon boundaries.
    # 3. Integrate Project NOAH real-time flood sensor data via API.
    # 4. Integrate PHIVOLCS fault line data for seismic resilience analysis.

if __name__ == "__main__":
    main()
