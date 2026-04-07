import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

st.set_page_config(page_title="Eco-Resilience AI Platform", layout="wide")

# -----------------------------
# CUSTOM STYLING
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef6f3 0%, #dceee7 45%, #f8fbfa 100%);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #184d3b;
}
.custom-card {
    background: rgba(255,255,255,0.84);
    border: 1px solid #d8e6df;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}
.small-note {
    font-size: 0.9rem;
    color: #4b5d56;
}
.section-title {
    font-weight: 700;
    color: #184d3b;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# Encoded demo values based on PhilAtlas Butuan profile and selected barangay figures
# -----------------------------
city_profile = {
    "City": "Butuan",
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

# -----------------------------
# HEADER
# -----------------------------
st.title("Eco-Resilience AI Platform")
st.caption("Decision-Support Tool for DRRM, Circular Economy, and Hazard-Informed Planning")

st.markdown("""
<div class="custom-card">
This prototype combines local demographic context, barangay reference data, hazard-reference links,
and a simple AI-assisted assessment workflow to support students, researchers, planners, and local governments.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Project Panel")
st.sidebar.write("**Application Context:** Butuan City, Caraga")
st.sidebar.write("**Prototype Category:** Professional")
st.sidebar.write("**Primary Users:** Students, researchers, planners, LGUs")

track = st.sidebar.radio(
    "Planning Focus",
    ["Integrated", "DRRM", "Circular Economy"]
)

selected_barangay = st.sidebar.selectbox(
    "Quick Barangay Selector",
    barangay_data["Barangay"].tolist()
)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "City & Barangay Profile",
    "Hazard Reference Tools",
    "Assessment & Export"
])

# =========================================================
# TAB 1 - PROFILE
# =========================================================
with tab1:
    st.subheader("Butuan City Profile")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Population (2020)", f"{city_profile['Population_2020']:,}")
    m2.metric("Land Area (km²)", f"{city_profile['Land_Area_km2']:.2f}")
    m3.metric("Density / km²", f"{city_profile['Density_per_km2']}")
    m4.metric("Barangays", f"{city_profile['Barangays']}")

    st.markdown(f"""
    <div class="custom-card">
    <b>Location Context:</b> {city_profile['City']} is a {city_profile['Type']} in {city_profile['Region']}.
    Its reference coordinates are approximately ({city_profile['Latitude']}, {city_profile['Longitude']}), with
    an estimated elevation of {city_profile['Elevation_m']} meters above sea level.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Barangay Reference Map")

    view_state = pdk.ViewState(
        latitude=city_profile["Latitude"],
        longitude=city_profile["Longitude"],
        zoom=11,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=barangay_data,
        get_position='[Longitude, Latitude]',
        get_radius=350,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{Barangay}\nPopulation: {Population_2020}\nGrowth Rate: {Growth_Rate}%"}
    ))

    st.subheader("Selected Barangay Demographic Profile")

    display_df = barangay_data[[
        "Barangay", "Population_2020", "Population_2015", "Growth_Rate", "Percent_Share"
    ]].copy()

    display_df.columns = [
        "Barangay", "Population 2020", "Population 2015", "Annual Growth Rate (%)", "Population Share (%)"
    ]

    st.dataframe(display_df, use_container_width=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### Top Selected Barangays by Population")
        pop_chart = alt.Chart(barangay_data).mark_bar().encode(
            x=alt.X("Population_2020:Q", title="Population (2020)"),
            y=alt.Y("Barangay:N", sort="-x", title="Barangay"),
            tooltip=["Barangay", "Population_2020", "Growth_Rate", "Percent_Share"]
        ).properties(height=350)
        st.altair_chart(pop_chart, use_container_width=True)

    with chart_col2:
        st.markdown("### Population Share of Selected Barangays")
        share_chart = alt.Chart(barangay_data).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Percent_Share", type="quantitative"),
            color=alt.Color(field="Barangay", type="nominal"),
            tooltip=["Barangay", "Percent_Share", "Population_2020"]
        ).properties(height=350)
        st.altair_chart(share_chart, use_container_width=True)

# =========================================================
# TAB 2 - HAZARD REFERENCE TOOLS
# =========================================================
with tab2:
    st.subheader("Hazard Reference Tools")

    st.markdown("""
    <div class="custom-card">
    This section points users to official hazard platforms that can support flood, landslide,
    storm surge, seismic, and general geospatial reference work.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Official Hazard Platforms")
        st.markdown("""
        <div class="custom-card">
        <b>Project NOAH</b><br>
        Hazard viewing and public hazard awareness for floods, landslides, and storm surge.<br><br>
        <a href="https://noah.up.edu.ph/" target="_blank">Open Project NOAH</a><br>
        <a href="https://noah.up.edu.ph/noah-studio" target="_blank">Open NOAH Studio</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="custom-card">
        <b>HazardHunterPH</b><br>
        Location-based indicative hazard assessment and report generation.<br><br>
        <a href="https://hazardhunter.georisk.gov.ph/" target="_blank">Open HazardHunterPH</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="custom-card">
        <b>MGB Geohazard Maps</b><br>
        Official geohazard map reference portal from the Mines and Geosciences Bureau.<br><br>
        <a href="https://databaseportal.mgb.gov.ph/" target="_blank">Open MGB Portal</a>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("### Geospatial Reference Platforms")
        st.markdown("""
        <div class="custom-card">
        <b>NAMRIA</b><br>
        National mapping and geospatial reference resources.<br><br>
        <a href="https://www.namria.gov.ph/" target="_blank">Open NAMRIA</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="custom-card">
        <b>GeoRiskPH</b><br>
        National geospatial risk and hazard initiative.<br><br>
        <a href="https://georisk.gov.ph/" target="_blank">Open GeoRiskPH</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="custom-card">
        <b>NAMRIA eMapa</b><br>
        Reference portal for maps, charts, and publications.<br><br>
        <a href="https://isportal.namria.gov.ph/eMapa/" target="_blank">Open NAMRIA eMapa</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Hazard Research Workflow")
    workflow_df = pd.DataFrame({
        "Step": [
            "1. Select location",
            "2. Check demographic profile",
            "3. Review official hazard sources",
            "4. Record observations",
            "5. Generate planning notes"
        ],
        "Description": [
            "Choose the barangay or study area.",
            "Review population and growth context.",
            "Open NOAH, HazardHunterPH, MGB, or NAMRIA for hazard reference.",
            "Summarize flood, landslide, storm surge, or other relevant findings.",
            "Use the assessment tab to generate a concise planning interpretation."
        ]
    })
    st.dataframe(workflow_df, use_container_width=True)

    st.markdown("### Hazard Notes Template")
    hazard_note = st.text_area(
        "Paste or type your hazard observations here",
        height=180,
        placeholder="Example: Barangay shows exposure to flooding near low-lying areas based on official hazard references..."
    )

# =========================================================
# TAB 3 - ASSESSMENT & EXPORT
# =========================================================
with tab3:
    st.subheader("AI-Assisted Area Assessment")

    area_row = barangay_data[barangay_data["Barangay"] == selected_barangay].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        barangay = st.selectbox("Select Barangay", barangay_data["Barangay"].tolist(),
                                index=barangay_data["Barangay"].tolist().index(selected_barangay))
        flood = st.selectbox("Flood Risk Level", ["Low", "Medium", "High"])
        waste = st.selectbox("Waste Management Condition", ["Good", "Fair", "Poor"])

    with col2:
        drainage = st.selectbox("Drainage Condition", ["Good", "Fair", "Poor"])
        exposure = st.selectbox("Population Exposure", ["Low", "Medium", "High"])

    def analyze_risk(flood, waste, drainage, exposure, track):
        flood_score = 3 if flood == "High" else 2 if flood == "Medium" else 1
        waste_score = 3 if waste == "Poor" else 2 if waste == "Fair" else 1
        drainage_score = 3 if drainage == "Poor" else 2 if drainage == "Fair" else 1
        exposure_score = 3 if exposure == "High" else 2 if exposure == "Medium" else 1

        score = flood_score + waste_score + drainage_score + exposure_score

        if score >= 10:
            level = "HIGH"
        elif score >= 7:
            level = "MODERATE"
        else:
            level = "LOW"

        recommendations = []

        if track in ["Integrated", "DRRM"]:
            if flood in ["Medium", "High"]:
                recommendations.append("Strengthen disaster preparedness, evacuation planning, and early warning measures.")
            if drainage == "Poor":
                recommendations.append("Prioritize drainage clearing, desilting, and flood-control interventions.")
            if exposure == "High":
                recommendations.append("Prioritize high-exposure households for preparedness and response coordination.")

        if track in ["Integrated", "Circular Economy"]:
            if waste in ["Fair", "Poor"]:
                recommendations.append("Improve segregation at source and strengthen barangay-level Materials Recovery Facility operations.")
            if flood == "High" and waste == "Poor":
                recommendations.append("Integrate flood mitigation and waste management to reduce blockage of waterways and drainage lines.")
            recommendations.append("Promote recovery, reuse, and diversion strategies consistent with circular economy action.")

        if not recommendations:
            recommendations.append("Maintain current systems and continue monitoring.")

        chart_data = pd.DataFrame({
            "Factor": ["Flood", "Waste", "Drainage", "Exposure"],
            "Score": [flood_score, waste_score, drainage_score, exposure_score]
        })

        return level, score, recommendations, chart_data

    if st.button("Analyze Area"):
        level, score, recommendations, chart_data = analyze_risk(flood, waste, drainage, exposure, track)

        st.markdown("---")
        st.subheader(f"Assessment Result for {barangay}")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Risk Score", score)
        r2.metric("Planning Focus", track)
        r3.metric("Population 2020", f"{int(area_row['Population_2020']):,}")
        r4.metric("Growth Rate (%)", f"{area_row['Growth_Rate']:.2f}")

        if level == "HIGH":
            st.error(f"Risk Level: {level}")
            interpretation = "This area requires immediate intervention and priority planning action."
        elif level == "MODERATE":
            st.warning(f"Risk Level: {level}")
            interpretation = "This area requires preventive action, preparedness improvements, and regular monitoring."
        else:
            st.success(f"Risk Level: {level}")
            interpretation = "This area is relatively stable but should continue routine monitoring and maintenance."

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### Interpretation")
            st.markdown(f"<div class='custom-card'>{interpretation}</div>", unsafe_allow_html=True)

            st.markdown("### Recommended Actions")
            rec_html = "<div class='custom-card'>" + "".join([f"<p>• {r}</p>" for r in recommendations]) + "</div>"
            st.markdown(rec_html, unsafe_allow_html=True)

            planning_summary = (
                f"For {barangay}, the combined conditions of hazard exposure, drainage condition, "
                f"waste management status, and population vulnerability indicate a {level.lower()} "
                f"level of concern. These actions support both resilience planning and resource-efficiency measures."
            )
            st.markdown("### Planning Summary")
            st.info(planning_summary)

            if hazard_note:
                st.markdown("### User Hazard Notes")
                st.markdown(f"<div class='custom-card'>{hazard_note}</div>", unsafe_allow_html=True)

        with right:
            st.markdown("### Risk Factor Breakdown")
            st.bar_chart(chart_data.set_index("Factor"))

        export_df = pd.DataFrame({
            "Field": [
                "Barangay", "Population 2020", "Growth Rate (%)", "Planning Focus",
                "Flood Risk", "Waste Condition", "Drainage Condition", "Population Exposure",
                "Risk Score", "Risk Level", "Planning Summary"
            ],
            "Value": [
                barangay,
                int(area_row["Population_2020"]),
                area_row["Growth_Rate"],
                track,
                flood,
                waste,
                drainage,
                exposure,
                score,
                level,
                planning_summary
            ]
        })

        st.markdown("### Download Output")
        st.download_button(
            label="Download assessment as CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{barangay.lower().replace(' ', '_')}_assessment.csv",
            mime="text/csv"
        )

# -----------------------------
# SOURCE NOTE
# -----------------------------
st.markdown("---")
st.markdown("""
<div class="custom-card small-note">
<b>Source note:</b> This prototype uses encoded Butuan demographic/profile values for presentation and demonstration.
Official hazard-reference platforms linked in the site include Project NOAH, HazardHunterPH, MGB, NAMRIA, and GeoRiskPH.
Students and researchers should verify hazard findings directly from the official sources before formal use.
</div>
""", unsafe_allow_html=True)
