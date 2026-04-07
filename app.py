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
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #184d3b;
}
.custom-card {
    background: rgba(255,255,255,0.82);
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
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# Source: PhilAtlas Butuan page (selected values encoded for demo use)
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
st.caption("Decision-Support Tool for DRRM and Circular Economy Planning in Butuan City")

st.markdown("""
<div class="custom-card">
This prototype combines local demographic context, barangay reference data, and a simple
AI-assisted risk assessment workflow to support planning decisions related to disaster risk
reduction and circular economy action.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Project Panel")
st.sidebar.write("**Prototype Category:** Professional")
st.sidebar.write("**Application Context:** Butuan City, Caraga")
st.sidebar.write("**Use Case:** DRRM + Circular Economy + Planning Support")

track = st.sidebar.radio(
    "Planning Focus",
    ["Integrated", "DRRM", "Circular Economy"]
)

# -----------------------------
# CITY PROFILE
# -----------------------------
st.subheader("Butuan City Profile")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Population (2020)", f"{city_profile['Population_2020']:,}")
m2.metric("Land Area (km²)", f"{city_profile['Land_Area_km2']:.2f}")
m3.metric("Density / km²", f"{city_profile['Density_per_km2']}")
m4.metric("Barangays", f"{city_profile['Barangays']}")

st.markdown(f"""
<div class="custom-card">
<b>Location Context:</b> {city_profile['City']} is a {city_profile['Type']} in {city_profile['Region']}. 
Its approximate reference coordinates are ({city_profile['Latitude']}, {city_profile['Longitude']}), 
with an estimated elevation of {city_profile['Elevation_m']} meters above sea level.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# MAP
# -----------------------------
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

# -----------------------------
# DEMOGRAPHIC PROFILE
# -----------------------------
st.subheader("Selected Barangay Demographic Profile")

display_df = barangay_data[[
    "Barangay", "Population_2020", "Population_2015", "Growth_Rate", "Percent_Share"
]].copy()

display_df.columns = [
    "Barangay", "Population 2020", "Population 2015", "Annual Growth Rate (%)", "Population Share (%)"
]

st.dataframe(display_df, use_container_width=True)

# -----------------------------
# CHARTS
# -----------------------------
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

# -----------------------------
# RISK ASSESSMENT INPUT
# -----------------------------
st.subheader("AI-Assisted Area Assessment")

col1, col2 = st.columns(2)

with col1:
    barangay = st.selectbox("Select Barangay", barangay_data["Barangay"].tolist())
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

    r1, r2, r3 = st.columns(3)
    r1.metric("Risk Score", score)
    r2.metric("Planning Focus", track)
    r3.metric("Selected Area", barangay)

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

        st.markdown("### Planning Summary")
        st.info(
            f"For {barangay}, the combined conditions of hazard exposure, drainage condition, "
            f"waste management status, and population vulnerability indicate a {level.lower()} "
            f"level of concern. These actions support both resilience planning and resource-efficiency measures."
        )

    with right:
        st.markdown("### Risk Factor Breakdown")
        st.bar_chart(chart_data.set_index("Factor"))

# -----------------------------
# SOURCE NOTE
# -----------------------------
st.markdown("---")
st.markdown("""
<div class="custom-card small-note">
<b>Source note:</b> City profile values and selected barangay demographic figures in this prototype
were encoded from the PhilAtlas Butuan City profile page for presentation and demonstration purposes.
Map points in this prototype are simplified reference locations for dashboard visualization.
</div>
""", unsafe_allow_html=True)
