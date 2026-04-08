import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime

# ==========================================
# 1. UI RECOVERY & STYLING
# ==========================================
st.set_page_config(page_title="Eco-Resilience AI | Butuan", page_icon="📐", layout="wide")

# Modernized, lightweight CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stHeader {
        background: #002B36;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 8px solid #2AA198;
    }
    .metric-box {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE DATA
# ==========================================
@st.cache_data
def load_butuan_data():
    meta = {"Project": "Eco-Resilience Platform", "Region": "Caraga XIII", "Datum": "PRS92"}
    data = [
        {"name": "Ambago", "p24": 15523, "lat": 8.9430, "lon": 125.5340, "risk": "High", "zone": "R-2"},
        {"name": "Ampayon", "p24": 13872, "lat": 8.9700, "lon": 125.5600, "risk": "Moderate", "zone": "INST"},
        {"name": "Baan KM 3", "p24": 15066, "lat": 8.9570, "lon": 125.5320, "risk": "High", "zone": "C-2"},
        {"name": "Doongan", "p24": 14591, "lat": 8.9420, "lon": 125.5510, "risk": "High", "zone": "R-1"},
        {"name": "Libertad", "p24": 24880, "lat": 8.9500, "lon": 125.5170, "risk": "Low", "zone": "C-3"},
        {"name": "Obrero", "p24": 8505, "lat": 8.9490, "lon": 125.5430, "risk": "Moderate", "zone": "IND-1"},
        {"name": "San Vicente", "p24": 20369, "lat": 8.9640, "lon": 125.5400, "risk": "Moderate", "zone": "R-2"}
    ]
    return meta, pd.DataFrame(data)

# ==========================================
# 3. STABLE MAP PLATE (BOHOL STYLE)
# ==========================================
def create_stable_plate(bgy_data, map_type):
    # Create the figure with GridSpec
    fig = plt.figure(figsize=(14, 8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
    
    # 1. THE MAP AXIS
    ax_map = fig.add_subplot(gs[0])
    ax_map.set_facecolor('#e3f2fd')
    # Use a simpler scatter plot to avoid contextily memory crashes
    ax_map.scatter(bgy_data['lon'], bgy_data['lat'], c='red', s=400, marker='*', edgecolors='black', label="Current Site")
    ax_map.set_title(f"Spatial Context: Barangay {bgy_data['name']}", fontsize=14, pad=15)
    ax_map.grid(True, linestyle='--', alpha=0.6)
    ax_map.set_xlabel("Longitude (E)")
    ax_map.set_ylabel("Latitude (N)")

    # 2. THE TECHNICAL SIDEBAR (BOHOL LAYOUT)
    ax_side = fig.add_subplot(gs[1])
    ax_side.set_axis_off()
    
    # Textual Content
    y = 0.95
    texts = [
        ("REPUBLIC OF THE PHILIPPINES", 10, "bold"),
        ("CITY OF BUTUAN", 9, "normal"),
        ("", 5, "normal"), # Spacer
        ("PROJECT:", 7, "italic"),
        ("ECO-RESILIENCE PLATFORM", 11, "bold"),
        ("", 5, "normal"), # Spacer
        ("MAP TYPE:", 7, "italic"),
        (map_type.upper(), 10, "bold"),
        ("", 5, "normal"), # Spacer
        ("LOCATION:", 7, "italic"),
        (f"Brgy. {bgy_data['name']}", 9, "normal"),
        ("", 30, "normal"), # Large Spacer
        ("NOTES:", 7, "italic"),
        ("Datum: PRS92", 6, "normal"),
        ("Source: LiDAR/NAMRIA", 6, "normal"),
        ("", 5, "normal"), # Spacer
        (f"DATE: {datetime.now().strftime('%m/%Y')}", 8, "bold")
    ]
    
    for text, size, weight in texts:
        if text != "":
            ax_side.text(0.05, y, text, fontsize=size, fontweight=weight)
        y -= 0.05

    # North Arrow
    ax_map.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.85),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    xycoords='axes fraction', ha='center', fontsize=18)

    plt.tight_layout()
    return fig

# ==========================================
# 4. APP RENDERING
# ==========================================
def main():
    meta, df = load_butuan_data()

    st.markdown('<div class="stHeader"><h1>📐 Butuan Geodetic Planning Portal</h1><p>Integrated LiDAR & Demographic Analysis</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.title("Settings")
        target = st.selectbox("Select Target Area", df['name'].tolist())
        map_type = st.radio("Map Profile", ["Flood Hazard Map", "Zoning Map", "Infrastructure Plan"])
        st.markdown("---")
        st.success("App Status: Functional")

    bgy = df[df['name'] == target].iloc[0]

    # Analytics Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><h4>Population</h4><h2>{bgy["p24"]:,}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><h4>Risk Level</h4><h2>{bgy["risk"]}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><h4>Zone</h4><h2>{bgy["zone"]}</h2></div>', unsafe_allow_html=True)

    # Interactive Map
    st.subheader("Interactive GIS Viewer")
    m = folium.Map(location=[bgy['lat'], bgy['lon']], zoom_start=15, tiles='CartoDB Positron')
    folium_static(m, width=1100)

    # Formal Map Plate
    st.markdown("---")
    st.subheader("Formal Map Plate (Technical Sidebar)")
    try:
        plate = create_stable_plate(bgy, map_type)
        st.pyplot(plate)
    except Exception as e:
        st.error(f"Error generating plate: {e}")

if __name__ == "__main__":
    main()
