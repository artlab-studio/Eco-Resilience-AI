import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Eco-Resilience AI Platform", layout="wide")

# ---------- CUSTOM STYLE ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef5f3 0%, #dceee7 50%, #f6fbf9 100%);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.75);
    border: 1px solid #d9e6df;
    padding: 15px;
    border-radius: 14px;
}
.custom-card {
    background-color: rgba(255,255,255,0.82);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #d9e6df;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}
h1, h2, h3 {
    color: #1f4d3b;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("Eco-Resilience AI Platform")
st.caption("Decision-Support Tool for DRRM and Circular Economy Planning")

st.markdown("""
<div class="custom-card">
This platform helps local governments assess environmental risk conditions and generate
planning recommendations for disaster resilience and circular economy action.
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("Project Overview")
st.sidebar.write("**Hackathon Entry Type:** Professional Category")
st.sidebar.write("**Focus:** DRRM + Circular Economy + Planning Support")
st.sidebar.write("**Target Users:** LGUs, planners, DRRM offices, waste management units")
st.sidebar.write("**Prototype Type:** AI-assisted decision-support dashboard")

track = st.sidebar.radio(
    "Planning Focus",
    ["Integrated", "DRRM", "Circular Economy"]
)

# ---------- SAMPLE DATA ----------
barangay_data = pd.DataFrame({
    "Barangay": ["Ampayon", "Libertad", "Obrero", "Doongan", "Baan"],
    "Latitude": [8.9540, 8.9475, 8.9502, 8.9440, 8.9578],
    "Longitude": [125.5480, 125.5345, 125.5408, 125.5525, 125.5318],
    "Population": [18500, 12400, 9800, 14300, 11000]
})

# ---------- INPUT SECTION ----------
st.subheader("Assessment Input")

col1, col2 = st.columns(2)

with col1:
    barangay = st.selectbox("Select Barangay", barangay_data["Barangay"].tolist())
    flood = st.selectbox("Flood Risk Level", ["Low", "Medium", "High"])
    waste = st.selectbox("Waste Management Condition", ["Good", "Fair", "Poor"])

with col2:
    drainage = st.selectbox("Drainage Condition", ["Good", "Fair", "Poor"])
    exposure = st.selectbox("Population Exposure", ["Low", "Medium", "High"])

# ---------- ANALYSIS ----------
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
            recommendations.append("Strengthen disaster preparedness, early warning, and evacuation planning.")
        if drainage == "Poor":
            recommendations.append("Prioritize drainage clearing, desilting, and flood control measures.")
        if exposure == "High":
            recommendations.append("Prioritize high-risk households for response coordination and preparedness planning.")

    if track in ["Integrated", "Circular Economy"]:
        if waste in ["Fair", "Poor"]:
            recommendations.append("Improve waste segregation and establish or strengthen a Materials Recovery Facility (MRF).")
        if flood == "High" and waste == "Poor":
            recommendations.append("Integrate flood mitigation and waste management to reduce waterway blockage and environmental risk.")
        recommendations.append("Promote circular economy practices through recovery, reuse, and barangay-level waste diversion strategies.")

    if not recommendations:
        recommendations.append("Maintain current systems and continue regular monitoring.")

    chart_data = pd.DataFrame({
        "Factor": ["Flood", "Waste", "Drainage", "Exposure"],
        "Score": [flood_score, waste_score, drainage_score, exposure_score]
    })

    return level, score, recommendations, chart_data

if st.button("Analyze Area"):
    level, score, recommendations, chart_data = analyze_risk(flood, waste, drainage, exposure, track)

    st.markdown("---")
    st.subheader(f"Assessment Result for {barangay}")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Risk Score", score)
    with m2:
        st.metric("Planning Focus", track)
    with m3:
        st.metric("Selected Barangay", barangay)

    if level == "HIGH":
        st.error(f"Risk Level: {level}")
        interpretation = "This area requires immediate intervention and priority planning action."
    elif level == "MODERATE":
        st.warning(f"Risk Level: {level}")
        interpretation = "This area requires preventive measures, preparedness improvements, and close monitoring."
    else:
        st.success(f"Risk Level: {level}")
        interpretation = "This area is relatively stable but should continue regular monitoring and maintenance."

    result_col1, result_col2 = st.columns([1.1, 1])

    with result_col1:
        st.markdown("### Risk Interpretation")
        st.markdown(f"""
        <div class="custom-card">
        {interpretation}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Recommended Actions")
        rec_html = "<div class='custom-card'>" + "".join([f"<p>• {r}</p>" for r in recommendations]) + "</div>"
        st.markdown(rec_html, unsafe_allow_html=True)

        st.markdown("### Planning Summary")
        st.info(
            f"For {barangay}, the combined conditions of flood risk, waste management, drainage, "
            f"and exposure indicate a {level.lower()} level of concern. The proposed actions support "
            f"both resilience and resource-efficiency planning for local governments."
        )

    with result_col2:
        st.markdown("### Risk Factor Breakdown")
        st.bar_chart(chart_data.set_index("Factor"))

    st.markdown("### Barangay Reference Map")
    selected_row = barangay_data[barangay_data["Barangay"] == barangay]

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=float(selected_row["Latitude"].iloc[0]),
            longitude=float(selected_row["Longitude"].iloc[0]),
            zoom=12,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=barangay_data,
                get_position='[Longitude, Latitude]',
                get_radius=250,
                pickable=True,
            )
        ],
        tooltip={"text": "{Barangay}\nPopulation: {Population}"}
    ))

    st.markdown("### Sample Barangay Data")
    st.dataframe(barangay_data, use_container_width=True)

    st.markdown("### Why This Matters")
    st.markdown("""
    <div class="custom-card">
    This prototype demonstrates how a local government can combine disaster risk reduction
    and circular economy strategies into one decision-support platform. It helps planners and
    decision-makers assess priority areas, interpret risk factors, and identify practical actions.
    </div>
    """, unsafe_allow_html=True)
