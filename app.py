import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from io import BytesIO

st.set_page_config(page_title="Eco-Resilience AI Platform", layout="wide")

# -------------------------------------------------
# STYLE
# -------------------------------------------------
background_image_url = "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1600&q=80"

st.markdown(f"""
<style>
.stApp {{
    background-image:
        linear-gradient(rgba(239,246,243,0.88), rgba(239,246,243,0.88)),
        url("{background_image_url}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}}
.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}}
h1, h2, h3 {{
    color: #184d3b;
}}
.custom-card {{
    background: rgba(255,255,255,0.88);
    border: 1px solid #d8e6df;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}}
.hero-box {{
    background: linear-gradient(135deg, rgba(24,77,59,0.92), rgba(36,111,86,0.88));
    color: white;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 18px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.10);
}}
.legend-box {{
    background: rgba(255,255,255,0.92);
    border-left: 5px solid #184d3b;
    border-radius: 12px;
    padding: 12px 15px;
    margin-bottom: 10px;
}}
.small-note {{
    font-size: 0.9rem;
    color: #4b5d56;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATA
# -------------------------------------------------
city_profile = {
    "City": "Butuan City",
    "Region": "Caraga (Region XIII)",
    "Type": "Highly Urbanized City",
    "Barangays": 86,
    "Population_2020": 372910,
    "Land_Area_km2": 816.62,
    "Density_per_km2": 457,
    "Latitude": 8.9534,
    "Longitude": 125.5288,
}

barangay_data = pd.DataFrame([
    {"Barangay": "Libertad", "Population_2020": 25296, "Population_2015": 21703, "Growth_Rate": 3.28, "Percent_Share": 6.78, "Latitude": 8.9500, "Longitude": 125.5170},
    {"Barangay": "San Vicente", "Population_2020": 19500, "Population_2015": 16187, "Growth_Rate": 4.00, "Percent_Share": 5.23, "Latitude": 8.9640, "Longitude": 125.5400},
    {"Barangay": "Baan KM 3", "Population_2020": 14539, "Population_2015": 11308, "Growth_Rate": 5.43, "Percent_Share": 3.90, "Latitude": 8.9570, "Longitude": 125.5320},
    {"Barangay": "Ambago", "Population_2020": 13634, "Population_2015": 12656, "Growth_Rate": 1.58, "Percent_Share": 3.66, "Latitude": 8.9430, "Longitude": 125.5340},
    {"Barangay": "Ampayon", "Population_2020": 13820, "Population_2015": 12720, "Growth_Rate": 1.76, "Percent_Share": 3.71, "Latitude": 8.9700, "Longitude": 125.5600},
    {"Barangay": "Doongan", "Population_2020": 13814, "Population_2015": 13728, "Growth_Rate": 0.13, "Percent_Share": 3.70, "Latitude": 8.9420, "Longitude": 125.5510},
    {"Barangay": "Obrero Poblacion", "Population_2020": 8643, "Population_2015": 9774, "Growth_Rate": -2.56, "Percent_Share": 2.32, "Latitude": 8.9490, "Longitude": 125.5430},
])

hazard_info = {
    "Flood Hazard": {
        "color": "#2b6cb0",
        "description": "Reference view for flood-prone planning analysis."
    },
    "Rain-Induced Landslide": {
        "color": "#dd6b20",
        "description": "Reference view for slope-related hazard analysis."
    },
    "Topographic Reference": {
        "color": "#2f855a",
        "description": "Reference view for terrain and elevation context."
    },
    "Storm Surge Reference": {
        "color": "#805ad5",
        "description": "Reference view for coastal hazard analysis."
    },
    "Integrated Risk View": {
        "color": "#c53030",
        "description": "Combined planning risk reference."
    }
}

# -------------------------------------------------
# HELPER: MAP GENERATOR
# -------------------------------------------------
def generate_map_layout(selected_barangay, selected_theme):
    selected_row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]
    theme_color = hazard_info[selected_theme]["color"]

    fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
    ax = fig.add_axes([0.06, 0.18, 0.62, 0.72])
    info_ax = fig.add_axes([0.72, 0.18, 0.24, 0.72])

    # Main map panel
    ax.set_facecolor("#f7fafc")

    # Plot all barangays
    ax.scatter(
        barangay_data["Longitude"],
        barangay_data["Latitude"],
        s=60,
        edgecolors="#184d3b",
        facecolors="white",
        linewidths=1.2,
        zorder=2
    )

    # Highlight selected barangay
    ax.scatter(
        selected_row["Longitude"],
        selected_row["Latitude"],
        s=260,
        color=theme_color,
        edgecolors="black",
        linewidths=1.2,
        zorder=4
    )

    # Simulated thematic extent
    circle = plt.Circle(
        (selected_row["Longitude"], selected_row["Latitude"]),
        0.010,
        color=theme_color,
        alpha=0.20,
        zorder=1
    )
    ax.add_patch(circle)

    # Labels
    for _, row in barangay_data.iterrows():
        ax.text(
            row["Longitude"] + 0.0012,
            row["Latitude"] + 0.0008,
            row["Barangay"],
            fontsize=8
        )

    ax.set_title(f"{selected_theme} Map of {selected_barangay}, Butuan City", fontsize=14, weight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle="--", alpha=0.3)

    # Tight map extent
    ax.set_xlim(barangay_data["Longitude"].min() - 0.01, barangay_data["Longitude"].max() + 0.01)
    ax.set_ylim(barangay_data["Latitude"].min() - 0.01, barangay_data["Latitude"].max() + 0.01)

    # North arrow
    ax.annotate(
        "N",
        xy=(0.95, 0.90), xytext=(0.95, 0.78),
        arrowprops=dict(facecolor='black', width=3, headwidth=10),
        ha='center', va='center',
        fontsize=12, fontweight='bold',
        xycoords='axes fraction'
    )

    # Info panel
    info_ax.axis("off")
    info_ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, linewidth=1.5, edgecolor="black"))

    info_text = (
        f"MAP TITLE:\n{selected_theme} Map of\n{selected_barangay}, Butuan City\n\n"
        f"BARANGAY:\n{selected_barangay}\n\n"
        f"POPULATION (2020):\n{int(selected_row['Population_2020']):,}\n\n"
        f"GROWTH RATE:\n{selected_row['Growth_Rate']:.2f}%\n\n"
        f"DESCRIPTION:\n{hazard_info[selected_theme]['description']}\n\n"
        f"LEGEND:\n"
        f"● Selected Barangay\n"
        f"○ Nearby Barangays\n"
        f"◌ Thematic Extent\n\n"
        f"SOURCE NOTE:\nPrepared by the researcher using\nencoded barangay reference data\nfor academic demonstration.\nOfficial hazard validation should\nbe verified with authorized agencies."
    )
    info_ax.text(0.05, 0.95, info_text, va="top", fontsize=9)

    legend_elements = [
        Patch(facecolor=theme_color, edgecolor='black', label='Selected Barangay / Theme'),
        Patch(facecolor='white', edgecolor='#184d3b', label='Nearby Barangays'),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8, frameon=True)

    # Bottom title block
    fig.text(0.06, 0.07, "Prepared through Eco-Resilience AI Platform", fontsize=9, weight="bold")
    fig.text(0.06, 0.045, "Map use: preliminary research, thesis illustration, and planning presentation", fontsize=8)
    fig.text(0.06, 0.02, "Note: This is a prototype map layout and not an official government hazard map.", fontsize=8)

    return fig

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="hero-box">
    <h1 style="color:white; margin-bottom:0.3rem;">Eco-Resilience AI Platform</h1>
    <p style="font-size:1.05rem; margin-bottom:0;">
    A decision-support and research-assist website for DRRM, circular economy, demographic profiling,
    barangay mapping, and thesis-ready planning outputs.
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Research Controls")

selected_barangay = st.sidebar.selectbox(
    "Select Barangay",
    barangay_data["Barangay"].tolist()
)

selected_theme = st.sidebar.selectbox(
    "Select Map Theme",
    list(hazard_info.keys())
)

planning_focus = st.sidebar.radio(
    "Planning Focus",
    ["Integrated", "DRRM", "Circular Economy"]
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Map Studio",
    "Assessment Tool",
    "Map Generator"
])

# -------------------------------------------------
# TAB 1
# -------------------------------------------------
with tab1:
    st.subheader("Butuan City Profile")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Population (2020)", f"{city_profile['Population_2020']:,}")
    c2.metric("Land Area (km²)", f"{city_profile['Land_Area_km2']:.2f}")
    c3.metric("Density / km²", f"{city_profile['Density_per_km2']}")
    c4.metric("Barangays", f"{city_profile['Barangays']}")

    st.dataframe(
        barangay_data[["Barangay", "Population_2020", "Population_2015", "Growth_Rate", "Percent_Share"]],
        use_container_width=True
    )

    chart = alt.Chart(barangay_data).mark_bar().encode(
        x=alt.X("Population_2020:Q", title="Population 2020"),
        y=alt.Y("Barangay:N", sort="-x"),
        tooltip=["Barangay", "Population_2020", "Growth_Rate"]
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)

# -------------------------------------------------
# TAB 2
# -------------------------------------------------
with tab2:
    st.subheader("Interactive Map Studio")
    row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]
    theme_color = hazard_info[selected_theme]["color"]

    m = folium.Map(location=[row["Latitude"], row["Longitude"]], zoom_start=13, tiles="OpenStreetMap")
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=selected_barangay,
        tooltip=selected_barangay
    ).add_to(m)

    folium.Circle(
        location=[row["Latitude"], row["Longitude"]],
        radius=1200,
        color=theme_color,
        fill=True,
        fill_opacity=0.25
    ).add_to(m)

    for _, r in barangay_data.iterrows():
        folium.CircleMarker(
            location=[r["Latitude"], r["Longitude"]],
            radius=4,
            color="#184d3b",
            fill=True,
            fill_color="#184d3b",
            popup=r["Barangay"]
        ).add_to(m)

    st_folium(m, height=500)

    st.markdown(f"""
    <div class="custom-card">
    <b>Selected Theme:</b> {selected_theme}<br>
    <b>Description:</b> {hazard_info[selected_theme]["description"]}
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# TAB 3
# -------------------------------------------------
with tab3:
    st.subheader("Assessment Tool")

    col1, col2 = st.columns(2)
    with col1:
        flood = st.selectbox("Flood Exposure", ["Low", "Moderate", "High"])
        waste = st.selectbox("Waste Management Condition", ["Good", "Fair", "Poor"])
    with col2:
        drainage = st.selectbox("Drainage Condition", ["Good", "Fair", "Poor"])
        exposure = st.selectbox("Population Exposure", ["Low", "Moderate", "High"])

    def score_value(v):
        mapping = {
            "Low": 1, "Good": 1,
            "Moderate": 2, "Fair": 2,
            "High": 3, "Poor": 3
        }
        return mapping[v]

    if st.button("Generate Assessment"):
        total_score = score_value(flood) + score_value(waste) + score_value(drainage) + score_value(exposure)
        level = "HIGH" if total_score >= 10 else "MODERATE" if total_score >= 7 else "LOW"
        st.metric("Risk Score", total_score)
        st.metric("Risk Level", level)

# -------------------------------------------------
# TAB 4
# -------------------------------------------------
with tab4:
    st.subheader("Thesis-Ready Map Generator")

    st.markdown("""
    <div class="custom-card">
    This tool generates a downloadable map layout with title, legend, north arrow, source note,
    and highlighted barangay context. This is the most functional thesis-ready output in the current prototype.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Map Plate"):
        fig = generate_map_layout(selected_barangay, selected_theme)

        st.pyplot(fig, use_container_width=True)

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)

        st.download_button(
            label="Download Map Plate as PNG",
            data=buf,
            file_name=f"{selected_barangay.lower().replace(' ', '_')}_{selected_theme.lower().replace(' ', '_')}_map.png",
            mime="image/png"
        )

        plt.close(fig)

    st.markdown("### Copy-Ready Thesis Caption")
    st.code(
        f"Figure X. {selected_theme} map of {selected_barangay}, Butuan City, showing the selected barangay in relation to nearby barangay context and thematic research reference.",
        language="text"
    )

    st.markdown("### Copy-Ready Source Note")
    st.code(
        "Source: Prepared by the researcher using encoded barangay reference data through the Eco-Resilience AI Platform. Official hazard validation should be verified from authorized government agencies.",
        language="text"
    )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="custom-card small-note">
This improved version can now generate a downloadable thesis-ready map plate.
For true hazard maps, the next step is to connect verified GIS datasets or official live geospatial services.
</div>
""", unsafe_allow_html=True)
