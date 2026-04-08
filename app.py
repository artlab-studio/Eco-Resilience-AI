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
# 1. SETUP & THEME (GLASSMORPHISM)
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
            padding: 50px 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }

        .stButton>button {
            border-radius: 6px;
            background-color: #2AA198;
            color: white;
            font-weight: 600;
            width: 100%;
            border: none;
            transition: 0.2s;
        }

        section[data-testid="stSidebar"] { background-color: #002B36; }
        
        .metric-label { font-size: 0.9rem; color: #64748b; font-weight: 600; }
        .metric-value { font-size: 1.8rem; color: #002B36; font-weight: 700; }
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
        "Coords": [8.9534, 125.5288],
        "Barangays": 86 
    }
    
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
# 3. STABILIZED MAP GENERATOR
# ==========================================
def generate_professional_plate(bgy_data, theme, basemap_provider, city_meta):
    plt.rcParams.update({'figure.max_open_warning': 0})
    fig = plt.figure(figsize=(15, 9))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3.8, 1.2])
    
    # Map Frame
    ax_map = fig.add_subplot(gs[0])
    ax_map.scatter(bgy_data['lon'], bgy_data['lat'], c='#d32f2f', s=450, marker='X', edgecolors='white', zorder=10)
    
    providers = {
        "Satellite": cx.providers.Esri.WorldImagery,
        "Light": cx.providers.CartoDB.Positron,
        "Dark": cx.providers.CartoDB.DarkMatter,
        "Terrain": cx.providers.CartoDB.Voyager
    }
    
    try:
        cx.add_basemap(ax_map, crs='EPSG:4326', source=providers.get(basemap_provider, cx.providers.CartoDB.Positron))
    except Exception:
        ax_map.set_facecolor('#cbd5e1')

    ax_map.set_axis_off()
    ax_map.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    xycoords='axes fraction', ha='center', fontsize=22, fontweight=700)

    # Technical Sidebar (Fixed Weight Logic)
    ax_side = fig.add_subplot(gs[1])
    ax_side.set_axis_off()
    ax_side.axvline(x=0, color='black', lw=1.5)
    
    y_pos = [0.96] 
    
    def write_t(txt, sz, wt='normal', clr='black', space=0.04):
        # Using numeric weights to bypass Matplotlib ValueError
        w_val = 700 if wt == 'bold' else 400
        f_style = 'italic' if wt == 'italic' else 'normal'
        
        ax_side.text(0.05, y_pos[0], txt, 
                     fontsize=sz, 
                     fontweight=w_val, 
                     fontstyle=f_style,
                     color=clr, 
                     transform=ax_side.transAxes)
        y_pos[0] -= space

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
    
    ax_side.text(0.05, 0.05, "DISCLAIMER: This map is a prototype.\nOfficial GIS datasets are required for\nfinal technical planning.", 
                 fontsize=6, fontstyle='italic', transform=ax_side.transAxes)

    plt.tight_layout()
    return fig

# ==========================================
# 4. APP INTERFACE
# ==========================================
def main():
    apply_custom_styles()
    meta, df = load_city_data()

    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Control Panel</h2>", unsafe_allow_html=True)
        selected_bgy = st.selectbox("🎯 Select Barangay", df['name'].tolist())
        map_theme = st.selectbox("🎨 Map Theme", ["Population Map", "Flood Hazard Reference", "Landslide Reference", "Topographic Reference"])
        
        st.markdown("---")
        interactive_base = st.selectbox("Basemap (Live)", ["CartoDB Positron", "OpenStreetMap"])
        static_base = st.selectbox("Basemap (Plate)", ["Satellite", "Light", "Dark", "Terrain"])
        
        st.markdown("---")
        st.caption("🔍 **Academic Note:** Prototype visualize reference data only.")

    bgy_data = df[df['name'] == selected_bgy].iloc[0]

    # --- HERO ---
    st.markdown(f"""
        <div class="hero-section">
            <h1 style='color:white; margin:0;'>ECO-RESILIENCE AI PLATFORM</h1>
            <p style='font-size:1.1rem; opacity:0.9;'>Early-Stage Geospatial Support System for Butuan City</p>
        </div>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "👥 Population", "🗺️ GIS Studio", "🧠 AI Assessment", "📄 Thesis Generator"])

    # TAB 1: DASHBOARD
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='glass-card'><p class='metric-label'>City Population</p><p class='metric-value'>{meta['Pop2024']:,}</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='glass-card'><p class='metric-label'>Land Area</p><p class='metric-value'>{meta['Area']} km²</p></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='glass-card'><p class='metric-label'>Barangay Count</p><p class='metric-value'>{meta['Barangays']}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'><h3>Planning Framework</h3><p>Integrating urban demographic growth with ecological risk profiles to support sustainable development in the Caraga Region. This platform acts as a bridge between fragmented agency data and academic research.</p></div>", unsafe_allow_html=True)

    # TAB 2: POPULATION
    with t2:
        st.subheader(f"Demographics: Brgy. {selected_bgy}")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.markdown(f"""<div class='glass-card'>
                <p><b>2024 Population:</b> {bgy_data['p24']:,}</p>
                <p><b>4-Year Growth:</b> {bgy_data['Growth_Rate']}%</p>
                <p><b>Zoning:</b> {bgy_data['zone']}</p></div>""", unsafe_allow_html=True)
        with col_p2:
            chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X('name:N', title="Barangay"),
                y=alt.Y('p24:Q', title="Population"),
                color=alt.condition(alt.datum.name == selected_bgy, alt.value('#2AA198'), alt.value('#cbd5e1'))
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

    # TAB 3: GIS STUDIO
    with t3:
        st.subheader("Interactive Visualizer")
        m = folium.Map(location=[bgy_data['lat'], bgy_data['lon']], zoom_start=15, tiles=interactive_base)
        folium.CircleMarker([bgy_data['lat'], bgy_data['lon']], radius=10, color="#d32f2f", fill=True, popup=selected_bgy).add_to(m)
        folium_static(m, width=1100, height=500)
        st.caption("Coordinate Reference: WGS 84. Barangay boundaries are conceptual.")

    # TAB 4: AI ASSESSMENT
    with t4:
        st.subheader("Planning Impact Scoring")
        with st.form("risk_form"):
            ca, cb = st.columns(2)
            f_in = ca.select_slider("Flood Frequency", options=[1, 2, 3])
            p_in = cb.select_slider("Pop. Density", options=[1, 2, 3])
            run = st.form_submit_button("Generate Assessment")
        
        if run:
            risk = (f_in + p_in) / 2
            status = "High Priority" if risk > 2 else "Routine Monitoring"
            st.info(f"AI Score: {risk}/3.0 - Action Status: **{status}**")

    # TAB 5: THESIS GENERATOR
    with t5:
        st.subheader("Professional Map Output")
        if st.button("🖼️ Render Professional Map Plate"):
            with st.spinner("Generating High-Res Plate..."):
                fig = generate_professional_plate(bgy_data, map_theme, static_base, meta)
                st.pyplot(fig)
            st.markdown("### Academic Source Documentation")
            st.code("Source: Eco-Resilience AI Platform (Prototype), referencing NAMRIA, MGB, NOAH, DENR, and PSA datasets. For academic use only.", language="text")

    st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:40px;'>© 2024 Eco-Resilience AI Initiative | Butuan City Project</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
