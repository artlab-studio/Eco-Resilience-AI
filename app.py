import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from io import BytesIO
import contextily as ctx

st.set_page_config(page_title="Eco-Resilience AI Platform", layout="wide")

# -------------------------------------------------
# STYLE
# -------------------------------------------------
background_image_url = "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1600&q=80"

st.markdown(f"""
<style>
.stApp {{
    background-image:
        linear-gradient(rgba(239,246,243,0.90), rgba(239,246,243,0.90)),
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
    background: rgba(255,255,255,0.90);
    border: 1px solid #d8e6df;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}}

.hero-box {{
    background: linear-gradient(135deg, rgba(24,77,59,0.94), rgba(36,111,86,0.90));
    color: white;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 18px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.10);
}}

.legend-box {{
    background: rgba(255,255,255,0.94);
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
# SIDEBAR
# -------------------------------------------------
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

basemap_choice = st.sidebar.selectbox(
    "Interactive Basemap",
    ["OpenStreetMap", "CartoDB Positron", "CartoDB Voyager"]
)

basemap_for_plate = st.sidebar.selectbox(
    "Basemap for Map Plate",
    ["OpenStreetMap", "CartoDB Positron", "CartoDB Voyager"]
)

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

st.markdown("""
<div class="custom-card">
This prototype is designed to help students, researchers, planners, and local governments work with
fragmented spatial and planning information in one place. It combines barangay profile data, map viewing,
hazard-theme switching, assessment tools, and thesis-oriented output structure.
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def get_folium_tiles(choice):
    if choice == "OpenStreetMap":
        return "OpenStreetMap"
    elif choice == "CartoDB Positron":
        return "CartoDB positron"
    else:
        return "CartoDB Voyager"

def get_contextily_provider(choice):
    if choice == "OpenStreetMap":
        return ctx.providers.OpenStreetMap.Mapnik
    elif choice == "CartoDB Positron":
        return ctx.providers.CartoDB.Positron
    else:
        return ctx.providers.CartoDB.Voyager

def score_value(v):
    mapping = {
        "Low": 1, "Good": 1,
        "Moderate": 2, "Fair": 2,
        "High": 3, "Poor": 3
    }
    return mapping[v]

def generate_map_layout(selected_barangay, selected_theme, basemap_for_plate):
    selected_row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]
    theme_color = hazard_info[selected_theme]["color"]
    basemap_source = get_contextily_provider(basemap_for_plate)

    fig = plt.figure(figsize=(11.69, 8.27))  # A4 Landscape
    ax = fig.add_axes([0.06, 0.18, 0.62, 0.72])
    info_ax = fig.add_axes([0.72, 0.18, 0.24, 0.72])

    ax.scatter(
        barangay_data["Longitude"],
        barangay_data["Latitude"],
        s=60,
        edgecolors="#184d3b",
        facecolors="white",
        linewidths=1.2,
        zorder=3
    )

    ax.scatter(
        selected_row["Longitude"],
        selected_row["Latitude"],
        s=260,
        color=theme_color,
        edgecolors="black",
        linewidths=1.2,
        zorder=5
    )

    thematic_circle = plt.Circle(
        (selected_row["Longitude"], selected_row["Latitude"]),
        0.010,
        color=theme_color,
        alpha=0.20,
        zorder=2
    )
    ax.add_patch(thematic_circle)

    for _, row in barangay_data.iterrows():
        ax.text(
            row["Longitude"] + 0.0010,
            row["Latitude"] + 0.0008,
            row["Barangay"],
            fontsize=8,
            zorder=6
        )

    xmin = barangay_data["Longitude"].min() - 0.01
    xmax = barangay_data["Longitude"].max() + 0.01
    ymin = barangay_data["Latitude"].min() - 0.01
    ymax = barangay_data["Latitude"].max() + 0.01

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    try:
        ctx.add_basemap(
            ax,
            crs="EPSG:4326",
            source=basemap_source,
            alpha=0.85
        )
    except Exception:
        ax.set_facecolor("#f7fafc")

    ax.set_title(f"{selected_theme} Map of {selected_barangay}, Butuan City", fontsize=14, weight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle="--", alpha=0.25, zorder=1)

    ax.annotate(
        "N",
        xy=(0.95, 0.90), xytext=(0.95, 0.78),
        arrowprops=dict(facecolor='black', width=3, headwidth=10),
        ha='center', va='center',
        fontsize=12, fontweight='bold',
        xycoords='axes fraction'
    )

    ax.text(
        0.02, 0.02,
        "Approximate map context only",
        transform=ax.transAxes,
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray")
    )

    info_ax.axis("off")
    info_ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, linewidth=1.5, edgecolor="black"))

    info_text = (
        f"MAP TITLE:\n{selected_theme} Map of\n{selected_barangay}, Butuan City\n\n"
        f"BARANGAY:\n{selected_barangay}\n\n"
        f"POPULATION (2020):\n{int(selected_row['Population_2020']):,}\n\n"
        f"GROWTH RATE:\n{selected_row['Growth_Rate']:.2f}%\n\n"
        f"BASEMAP:\n{basemap_for_plate}\n\n"
        f"DESCRIPTION:\n{hazard_info[selected_theme]['description']}\n\n"
        f"LEGEND:\n"
        f"● Selected Barangay / Theme\n"
        f"○ Nearby Barangays\n"
        f"◌ Thematic Extent\n\n"
        f"SOURCE NOTE:\nPrepared by the researcher using\nencoded barangay reference data\nwith web basemap support for\nacademic demonstration.\nOfficial hazard validation should\nbe verified with authorized agencies."
    )
    info_ax.text(0.05, 0.95, info_text, va="top", fontsize=9)

    legend_elements = [
        Patch(facecolor=theme_color, edgecolor='black', label='Selected Barangay / Theme'),
        Patch(facecolor='white', edgecolor='#184d3b', label='Nearby Barangays')
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8, frameon=True)

    fig.text(0.06, 0.07, "Prepared through Eco-Resilience AI Platform", fontsize=9, weight="bold")
    fig.text(0.06, 0.045, "Map use: preliminary research, thesis illustration, and planning presentation", fontsize=8)
    fig.text(0.06, 0.02, "Note: Hazard themes shown here are prototype overlays unless validated with official datasets.", fontsize=8)

    return fig

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Map Studio",
    "Assessment Tool",
    "Map Generator"
])

# -------------------------------------------------
# TAB 1 - OVERVIEW
# -------------------------------------------------
with tab1:
    st.subheader("Butuan City Profile")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Population (2020)", f"{city_profile['Population_2020']:,}")
    c2.metric("Land Area (km²)", f"{city_profile['Land_Area_km2']:.2f}")
    c3.metric("Density / km²", f"{city_profile['Density_per_km2']}")
    c4.metric("Barangays", f"{city_profile['Barangays']}")

    st.markdown(f"""
    <div class="custom-card">
    <b>Urban Context:</b> {city_profile['City']} is a {city_profile['Type']} in {city_profile['Region']}.
    This dashboard uses Butuan-focused demographic and spatial reference content to support academic and planning workflows.
    </div>
    """, unsafe_allow_html=True)

    display_df = barangay_data[[
        "Barangay", "Population_2020", "Population_2015", "Growth_Rate", "Percent_Share"
    ]].copy()

    display_df.columns = [
        "Barangay", "Population 2020", "Population 2015", "Annual Growth Rate (%)", "Population Share (%)"
    ]

    st.dataframe(display_df, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Population by Selected Barangays")
        pop_chart = alt.Chart(barangay_data).mark_bar().encode(
            x=alt.X("Population_2020:Q", title="Population (2020)"),
            y=alt.Y("Barangay:N", sort="-x", title="Barangay"),
            tooltip=["Barangay", "Population_2020", "Growth_Rate", "Percent_Share"]
        ).properties(height=360)
        st.altair_chart(pop_chart, use_container_width=True)

    with col_b:
        st.markdown("### Population Share")
        share_chart = alt.Chart(barangay_data).mark_arc(innerRadius=70).encode(
            theta=alt.Theta(field="Percent_Share", type="quantitative"),
            color=alt.Color(field="Barangay", type="nominal"),
            tooltip=["Barangay", "Percent_Share", "Population_2020"]
        ).properties(height=360)
        st.altair_chart(share_chart, use_container_width=True)

# -------------------------------------------------
# TAB 2 - MAP STUDIO
# -------------------------------------------------
with tab2:
    st.subheader("Interactive Map Studio")

    row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]
    theme_color = hazard_info[selected_theme]["color"]

    m = folium.Map(
        location=[row["Latitude"], row["Longitude"]],
        zoom_start=13,
        tiles=get_folium_tiles(basemap_choice)
    )

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"{selected_barangay}<br>Population: {int(row['Population_2020']):,}",
        tooltip=selected_barangay,
        icon=folium.Icon(color="darkgreen", icon="info-sign")
    ).add_to(m)

    folium.Circle(
        location=[row["Latitude"], row["Longitude"]],
        radius=1200,
        color=theme_color,
        fill=True,
        fill_opacity=0.25,
        popup=selected_theme
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

    st_folium(m, height=520, width=None)

    st.markdown(f"""
    <div class="custom-card">
    <b>Selected Theme:</b> {selected_theme}<br>
    <b>Description:</b> {hazard_info[selected_theme]['description']}<br>
    <b>Basemap:</b> {basemap_choice}
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# TAB 3 - ASSESSMENT TOOL
# -------------------------------------------------
with tab3:
    st.subheader("AI-Assisted Assessment Tool")

    row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        flood = st.selectbox("Flood Exposure", ["Low", "Moderate", "High"])
        waste = st.selectbox("Waste Management Condition", ["Good", "Fair", "Poor"])
    with col2:
        drainage = st.selectbox("Drainage Condition", ["Good", "Fair", "Poor"])
        exposure = st.selectbox("Population Exposure", ["Low", "Moderate", "High"])

    if st.button("Generate Assessment"):
        flood_score = score_value(flood)
        waste_score = score_value(waste)
        drainage_score = score_value(drainage)
        exposure_score = score_value(exposure)

        total_score = flood_score + waste_score + drainage_score + exposure_score

        if total_score >= 10:
            level = "HIGH"
            interpretation = "This barangay requires immediate intervention and stronger planning control."
        elif total_score >= 7:
            level = "MODERATE"
            interpretation = "This barangay requires preventive action, monitoring, and planning attention."
        else:
            level = "LOW"
            interpretation = "This barangay is relatively stable but still requires regular monitoring."

        recommendations = []

        if planning_focus in ["Integrated", "DRRM"]:
            if flood in ["Moderate", "High"]:
                recommendations.append("Strengthen flood preparedness and community response planning.")
            if drainage == "Poor":
                recommendations.append("Prioritize drainage rehabilitation and localized flood mitigation.")
            if exposure == "High":
                recommendations.append("Focus on highly exposed households for early warning and response coordination.")

        if planning_focus in ["Integrated", "Circular Economy"]:
            if waste in ["Fair", "Poor"]:
                recommendations.append("Improve segregation at source and strengthen barangay-level recovery systems.")
            recommendations.append("Promote circular economy actions through reuse, diversion, and community waste reduction.")

        if not recommendations:
            recommendations.append("Maintain current systems and continue monitoring.")

        chart_df = pd.DataFrame({
            "Factor": ["Flood", "Waste", "Drainage", "Exposure"],
            "Score": [flood_score, waste_score, drainage_score, exposure_score]
        })

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Risk Score", total_score)
        r2.metric("Risk Level", level)
        r3.metric("Population 2020", f"{int(row['Population_2020']):,}")
        r4.metric("Growth Rate (%)", f"{row['Growth_Rate']:.2f}")

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### Assessment Interpretation")
            st.markdown(f"<div class='custom-card'>{interpretation}</div>", unsafe_allow_html=True)

            st.markdown("### Recommended Actions")
            rec_html = "<div class='custom-card'>" + "".join([f"<p>• {r}</p>" for r in recommendations]) + "</div>"
            st.markdown(rec_html, unsafe_allow_html=True)

            planning_summary = (
                f"{selected_barangay} shows a {level.lower()} level of planning concern based on flood exposure, "
                f"waste condition, drainage condition, and population exposure. The results support {planning_focus.lower()} "
                f"planning actions for local resilience and resource efficiency."
            )

            st.markdown("### Planning Summary")
            st.info(planning_summary)

            export_df = pd.DataFrame({
                "Field": [
                    "Barangay", "Population 2020", "Growth Rate (%)", "Map Theme",
                    "Planning Focus", "Flood Exposure", "Waste Condition",
                    "Drainage Condition", "Population Exposure", "Risk Score", "Risk Level"
                ],
                "Value": [
                    selected_barangay, int(row["Population_2020"]), row["Growth_Rate"], selected_theme,
                    planning_focus, flood, waste, drainage, exposure, total_score, level
                ]
            })

            st.download_button(
                label="Download Assessment CSV",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_barangay.lower().replace(' ', '_')}_assessment.csv",
                mime="text/csv"
            )

        with right:
            st.markdown("### Factor Breakdown")
            st.bar_chart(chart_df.set_index("Factor"))

# -------------------------------------------------
# TAB 4 - MAP GENERATOR
# -------------------------------------------------
with tab4:
    st.subheader("Thesis-Ready Map Generator")

    st.markdown("""
    <div class="custom-card">
    This tool generates a downloadable map layout with title, legend, north arrow, source note,
    and highlighted barangay context. It now includes a real basemap background for a more complete thesis-ready plate.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Map Plate"):
        fig = generate_map_layout(selected_barangay, selected_theme, basemap_for_plate)

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
        f"Source: Prepared by the researcher using encoded barangay reference data through the Eco-Resilience AI Platform with {basemap_for_plate} basemap support. Official hazard validation should be verified from authorized government agencies.",
        language="text"
    )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="custom-card small-note">
This improved version can generate a downloadable thesis-ready map plate with a real basemap background.
For true official hazard maps, the next step is to connect verified GIS datasets or authorized live geospatial services.
</div>
""", unsafe_allow_html=True)
