import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium

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

.small-note {{
    font-size: 0.9rem;
    color: #4b5d56;
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

.title-block {{
    background: rgba(255,255,255,0.92);
    border: 2px solid #184d3b;
    border-radius: 12px;
    padding: 16px;
}}

.north-arrow {{
    font-size: 2rem;
    font-weight: bold;
    text-align: center;
    color: #184d3b;
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
    "Elevation_m": 6.8,
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
        "color": "blue",
        "description": "Used for identifying low-lying and flood-prone areas for settlement planning, evacuation strategy, and drainage intervention."
    },
    "Rain-Induced Landslide": {
        "color": "orange",
        "description": "Used for slope instability assessment and land suitability review in upland and disturbed areas."
    },
    "Topographic Reference": {
        "color": "green",
        "description": "Used as terrain context for elevation, landform interpretation, and site characterization."
    },
    "Storm Surge Reference": {
        "color": "purple",
        "description": "Useful for coastal hazard interpretation and evacuation planning in vulnerable areas."
    },
    "Integrated Risk View": {
        "color": "red",
        "description": "A combined planning view for disaster exposure, environmental condition, and settlement sensitivity."
    }
}

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
    "Basemap Style",
    ["OpenStreetMap", "CartoDB Positron", "CartoDB Voyager"]
)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Map Studio",
    "Assessment Tool",
    "Thesis Map Template"
])

# -------------------------------------------------
# TAB 1 - OVERVIEW
# -------------------------------------------------
with tab1:
    st.subheader("Butuan City Profile")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Population (2020)", f"{city_profile['Population_2020']:,}")
    m2.metric("Land Area (km²)", f"{city_profile['Land_Area_km2']:.2f}")
    m3.metric("Density / km²", f"{city_profile['Density_per_km2']}")
    m4.metric("Barangays", f"{city_profile['Barangays']}")

    st.markdown(f"""
    <div class="custom-card">
    <b>Urban Context:</b> {city_profile['City']} is a {city_profile['Type']} in {city_profile['Region']}.
    This dashboard uses Butuan-focused demographic and spatial reference content to support academic and planning workflows.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Barangay Demographic Profile")

    display_df = barangay_data[[
        "Barangay", "Population_2020", "Population_2015", "Growth_Rate", "Percent_Share"
    ]].copy()

    display_df.columns = [
        "Barangay", "Population 2020", "Population 2015", "Annual Growth Rate (%)", "Population Share (%)"
    ]

    st.dataframe(display_df, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Population by Selected Barangays")
        pop_chart = alt.Chart(barangay_data).mark_bar().encode(
            x=alt.X("Population_2020:Q", title="Population (2020)"),
            y=alt.Y("Barangay:N", sort="-x", title="Barangay"),
            tooltip=["Barangay", "Population_2020", "Growth_Rate", "Percent_Share"]
        ).properties(height=360)
        st.altair_chart(pop_chart, use_container_width=True)

    with c2:
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

    if basemap_choice == "OpenStreetMap":
        tiles = "OpenStreetMap"
    elif basemap_choice == "CartoDB Positron":
        tiles = "CartoDB positron"
    else:
        tiles = "CartoDB Voyager"

    m = folium.Map(
        location=[row["Latitude"], row["Longitude"]],
        zoom_start=13,
        tiles=tiles
    )

    # Barangay marker
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"{selected_barangay}<br>Population: {int(row['Population_2020']):,}",
        tooltip=selected_barangay,
        icon=folium.Icon(color="darkgreen", icon="info-sign")
    ).add_to(m)

    # Theme layer simulation
    theme_color = hazard_info[selected_theme]["color"]

    folium.Circle(
        location=[row["Latitude"], row["Longitude"]],
        radius=1300,
        color=theme_color,
        fill=True,
        fill_opacity=0.22,
        popup=selected_theme
    ).add_to(m)

    # Nearby barangays
    for _, r in barangay_data.iterrows():
        folium.CircleMarker(
            location=[r["Latitude"], r["Longitude"]],
            radius=5,
            popup=f"{r['Barangay']}<br>Population: {int(r['Population_2020']):,}",
            color="#184d3b",
            fill=True,
            fill_color="#184d3b",
            fill_opacity=0.75
        ).add_to(m)

    st_folium(m, width=None, height=520)

    mc1, mc2 = st.columns([1.25, 1])

    with mc1:
        st.markdown("### Map Interpretation")
        st.markdown(f"""
        <div class="custom-card">
        <b>Selected Barangay:</b> {selected_barangay}<br>
        <b>Map Theme:</b> {selected_theme}<br>
        <b>Description:</b> {hazard_info[selected_theme]["description"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Technical Use")
        st.markdown("""
        <div class="custom-card">
        This map studio is intended as a research and planning workspace where a user can:
        <ul>
            <li>locate a barangay</li>
            <li>view a thematic hazard or reference mode</li>
            <li>relate demographic conditions with spatial context</li>
            <li>prepare a cleaner basis for thesis mapping and planning interpretation</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with mc2:
        st.markdown("### Layer Guide")
        st.markdown(f"""
        <div class="legend-box"><b>{selected_theme}</b><br>{hazard_info[selected_theme]["description"]}</div>
        <div class="legend-box"><b>Barangay Reference Point</b><br>Displays encoded barangay reference location.</div>
        <div class="legend-box"><b>Context Points</b><br>Shows nearby selected barangays for comparative context.</div>
        """, unsafe_allow_html=True)

        st.markdown("### Future Layer Expansion")
        st.markdown("""
        <div class="custom-card">
        The next development stage may connect verified external map services for:
        <ul>
            <li>flood hazard</li>
            <li>rain-induced landslide</li>
            <li>storm surge</li>
            <li>topographic and terrain references</li>
            <li>other technical geospatial layers</li>
        </ul>
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

    def score_value(v):
        mapping = {
            "Low": 1, "Good": 1,
            "Moderate": 2, "Fair": 2,
            "High": 3, "Poor": 3
        }
        return mapping[v]

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
# TAB 4 - THESIS MAP TEMPLATE
# -------------------------------------------------
with tab4:
    st.subheader("Thesis Map Template Panel")

    row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]

    st.markdown(f"""
    <div class="title-block">
        <div class="north-arrow">↑ N</div>
        <h3 style="margin-top:0.2rem;">Map Title</h3>
        <p><b>{selected_theme} Map of {selected_barangay}, Butuan City</b></p>
        <p><b>Description:</b> This map presents the selected barangay in relation to the chosen thematic reference layer for research, planning, and academic interpretation.</p>
        <p><b>Location:</b> {selected_barangay}, Butuan City, Caraga Region</p>
        <p><b>Reference Coordinates:</b> {row['Latitude']}, {row['Longitude']}</p>
        <p><b>Population (2020):</b> {int(row['Population_2020']):,}</p>
        <p><b>Legend:</b> Barangay reference point, thematic area of interest, nearby barangay context points</p>
        <p><b>Suggested Sources:</b> City demographic profile, barangay reference data, official hazard and geospatial agencies</p>
    </div>
    """, unsafe_allow_html=True)

    map_caption = (
        f"Figure X. {selected_theme} map of {selected_barangay}, Butuan City, showing the selected barangay "
        f"in relation to thematic planning and hazard reference context for academic and research use."
    )

    source_note = (
        "Source: Prepared by the researcher using encoded barangay reference data and thematic planning visualization. "
        "Official hazard and geospatial validation should be cross-checked with authorized government sources."
    )

    description_text = (
        f"The map highlights {selected_barangay} as the selected study area under the {selected_theme.lower()} mode. "
        f"It is intended to support preliminary spatial interpretation, demographic contextualization, and thesis presentation formatting."
    )

    st.markdown("### Copy-Ready Thesis Caption")
    st.code(map_caption, language="text")

    st.markdown("### Copy-Ready Source Note")
    st.code(source_note, language="text")

    st.markdown("### Copy-Ready Description")
    st.code(description_text, language="text")

    thesis_export = pd.DataFrame({
        "Section": ["Map Title", "Caption", "Source Note", "Description"],
        "Content": [
            f"{selected_theme} Map of {selected_barangay}, Butuan City",
            map_caption,
            source_note,
            description_text
        ]
    })

    st.download_button(
        label="Download Thesis Map Notes CSV",
        data=thesis_export.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_barangay.lower().replace(' ', '_')}_thesis_map_notes.csv",
        mime="text/csv"
    )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("""
<div class="custom-card small-note">
<b>Prototype note:</b> This version is a planning and research-oriented dashboard prototype.
It organizes barangay profile data, thematic map viewing, assessment logic, and thesis-ready formatting
into one workflow. Official live hazard layers may be integrated later once verified external geospatial services
and reusable map endpoints are confirmed.
</div>
""", unsafe_allow_html=True)
