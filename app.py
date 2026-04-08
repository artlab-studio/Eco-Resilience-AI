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
# 1. SETUP & THEME (GLASSMORPHISM & ACADEMIC)
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .hero-section {
            background: linear-gradient(rgba(0, 43, 54, 0.85), rgba(0, 43, 54, 0.85)), 
                        url('https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            padding: 60px 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.95);
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
            width: 100%;
            border: none;
            transition: 0.3s;
        }

        section[data-testid="stSidebar"] { background-color: #002B36; }
        
        .disclaimer-text {
            font-size: 0.75rem;
            color: #64748b;
            font-style: italic;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE (FIXED KEYERROR)
# ==========================================
@st.cache_data
def load_city_data():
    city_summary = {
        "Name": "Butuan City",
        "Pop2020": 372910,
        "Pop2024": 385530,
        "Area": 816.62,
        "Coords": [8.9534, 125.5288],
        "Barangays": 86  # Fixed the KeyError by adding this key
    }
    
    # Barangay Data Matrix
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
# 3. MAP GENERATOR (BOHOL SIDEBAR STYLE)
# ==========================================
def generate_professional_plate(bgy_data, theme, basemap_provider, city_meta):
    fig = plt.figure(figsize=(15, 9))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3.8, 1.2])
    
    # Map Frame
    ax_map = fig.add_subplot(gs[0])
    ax_map.scatter(bgy_data['lon'], bgy_data['lat'], c='#d32f2f', s=450, marker='X', edgecolors='white', zorder=10)
    
    providers = {
        "Satellite": cx.providers.Esri.WorldImagery,
        "Terrain": cx.providers.CartoDB.Positron, # Contextily terrain fallback
        "Light": cx.providers.CartoDB.Positron,
        "Dark": cx.providers.CartoDB.DarkMatter
    }
    
    try:
        cx.add_basemap(ax_map, crs='EPSG:4326', source=providers.get(basemap_provider))
    except:
        ax_map.set_facecolor('#d1d5db')

    ax_map.set_axis_off()
    ax_map.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                    arrowprops=dict(facecolor='black', width=4, headwidth=12),
                    xycoords='axes fraction', ha='center', fontsize=20)

    # Technical Sidebar (Bohol Layout)
    ax_side = fig.add_subplot(gs[1])
    ax_side.set_axis_off()
    ax_side.axvline(x=0, color='black', lw=1.5)
    
    y = 0.96
    def write_t(txt, sz, wt='normal', clr='black', space=0.04):
        nonlocal y
        ax_side.text(0.05, y, txt, fontsize=sz, fontweight=wt, color=clr, transform=ax_side.transAxes)
        y -= space

    write_t("ECO-RESILIENCE AI PLATFORM", 11, 'bold', '#002B36')
    write_t("TECHNICAL PLANNING PORTAL", 7, 'normal', '#2AA198', space=0.06)
    
    write_t("PROJECT:", 7, 'bold', 'gray')
    write_t("BUTUAN RESILIENCE INITIATIVE", 9, 'bold', space=0.06)
    
    write_t("MAP THEME:", 7, 'bold', 'gray')
    write_t(theme.upper(), 9, 'bold', '#d32f2f', space=0.06)
    
    write_t("LOCATION:", 7, 'bold', 'gray')
    write_t(f"BARANGAY {bgy_data['name'].upper()}", 9, 'bold', space=0.1)
    
    write_t("DATA SOURCES:", 7, 'bold', 'gray')
    write_t("NAMRIA | MGB | NOAH | DENR | PSA", 6, 'normal')
    write_t("(Referenced – Prototype Use Only)", 5, 'italic', space=0.1)
    
    write_t("TECHNICAL NOTES:", 7, 'bold', 'gray')
    write_t(f"Datum: PRS92 / WGS 84\nGen: {datetime.now().strftime('%Y-%m-%d')}\nScale: Not to Scale", 6, space=0.1)
    
    write_t("SOURCE NOTE:", 7, 'bold', 'gray')
    source_msg = "Prepared through the Eco-Resilience AI\nPlatform using reference data. Hazard\nrefs aligned with NAMRIA, MGB, and NOAH."
    ax_side.text(0.05, y-0.05, source_msg, fontsize=5.5, transform=ax_side.transAxes)

    ax_side.text(0.05, 0.05, "DISCLAIMER: This map is a prototype.\nOfficial GIS datasets are required for\nfinal technical planning.", 
                 fontsize=5.5, fontstyle='italic', transform=ax_side.transAxes)

    plt.tight_layout()
    return fig

# ==========================================
# 4. APP INTERFACE
# ==========================================
def main():
    apply_custom_styles()
    meta, df = load_city_data()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Control Panel</h2>", unsafe_allow_html=True)
        selected_bgy = st.selectbox("🎯 Select Barangay", df['name'].tolist())
        map_theme = st.selectbox("🎨 Map Theme", ["Population Density", "Flood Hazard Reference", "Landslide Reference", "Topographic Reference"])
        
        st.markdown("---")
        interactive_base = st.selectbox("Basemap (Live)", ["CartoDB Positron", "OpenStreetMap"])
        static_base = st.selectbox("Basemap (Plate)", ["Satellite", "Light", "Dark"])
        
        st.markdown("---")
        st.caption("🔍 **Platform Notes:** Preliminary academic and planning use only.")

    bgy_data = df[df['name'] == selected_bgy].iloc[0]

    # --- HERO ---
    st.markdown(f"""
        <div class="hero-section">
            <h1 style='color:white; margin:0;'>ECO-RESILIENCE AI PLATFORM</h1>
            <p style='font-size:1.1rem; opacity:0.9;'>Integrated Geospatial & Demographic Portal for Butuan City</p>
        </div>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "👥 Population", "🗺️ GIS Studio", "🧠 AI Assessment", "📄 Thesis Generator"])

    # TAB 1: DASHBOARD
    with t1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Est. Population (2024)", f"{meta['Pop2024']:,}")
        col2.metric("Land Area", f"{meta['Area']} km²")
        col3.metric("Barangays", meta["Barangays"])
        
        st.markdown("<div class='glass-card'><h3>Strategy Overview</h3><p>Butuan City faces complex ecological challenges. This platform centralizes data from NAMRIA, MGB, and PSA to support site-specific planning and academic research.</p></div>", unsafe_allow_html=True)

    # TAB 2: POPULATION
    with t2:
        st.subheader(f"Demographics: Brgy. {selected_bgy}")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""<div class='glass-card'>
                <p><b>2024 Pop:</b> {bgy_data['p24']:,}</p>
                <p><b>Growth Rate:</b> {bgy_data['Growth_Rate']}%</p>
                <p><b>Zoning:</b> {bgy_data['zone']}</p></div>""", unsafe_allow_html=True)
        with c2:
            chart = alt.Chart(df).mark_bar().encode(
                x='name:N', y='p24:Q',
                color=alt.condition(alt.datum.name == selected_bgy, alt.value('#2AA198'), alt.value('#cbd5e1'))
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

    # TAB 3: GIS STUDIO
    with t3:
        m = folium.Map(location=[bgy_data['lat'], bgy_data['lon']], zoom_start=15, tiles=interactive_base)
        folium.Marker([bgy_data['lat'], bgy_data['lon']], popup=f"Brgy. {bgy_data['name']}").add_to(m)
        folium_static(m, width=1100, height=500)
        st.caption("Note: Barangay locations are approximate reference points only.")

    # TAB 4: AI ASSESSMENT
    with t4:
        st.subheader("Planning Risk Assessment")
        with st.form("ai_form"):
            f_risk = st.slider("Flood Exposure", 1, 3, 2)
            d_risk = st.slider("Drainage Gap", 1, 3, 1)
            sub = st.form_submit_button("Run Assessment")
        if sub:
            score = (f_risk + d_risk) / 2
            st.info(f"Composite Risk Score: {score}/3.0 - Recommended Action: Upgrade NBS Infrastructure.")

    # TAB 5: THESIS GENERATOR
    with t5:
        st.subheader("Professional Map Plate Generator")
        if st.button("🖼️ Render Thesis Plate"):
            fig = generate_professional_plate(bgy_data, map_theme, static_base, meta)
            st.pyplot(fig)
            st.markdown("### Academic Source Note")
            st.code("Source: Eco-Resilience AI Platform (Prototype), with reference to NAMRIA, MGB, Project NOAH, DENR, and PSA datasets. For academic use only.", language="text")

    st.markdown("<center><p style='color:#64748b; font-size:0.8rem;'>© 2024 Eco-Resilience AI Platform | Prototype Academic Project</p></center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
