import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(page_title="Eco-Resilience AI Platform", layout="wide")

# Header
st.title("Eco-Resilience AI Platform")
st.caption("Decision-Support Tool for DRRM and Circular Economy Planning")
st.markdown("---")

st.write(
    "This platform helps local governments assess environmental risk conditions "
    "and generate planning recommendations for disaster resilience and circular economy action."
)

# Layout for inputs
col1, col2 = st.columns(2)

with col1:
    barangay = st.selectbox(
        "Select Barangay",
        ["Ampayon", "Libertad", "Obrero", "Doongan", "Baan"]
    )

    flood = st.selectbox(
        "Flood Risk Level",
        ["Low", "Medium", "High"]
    )

    waste = st.selectbox(
        "Waste Management Condition",
        ["Good", "Fair", "Poor"]
    )

with col2:
    drainage = st.selectbox(
        "Drainage Condition",
        ["Good", "Fair", "Poor"]
    )

    exposure = st.selectbox(
        "Population Exposure",
        ["Low", "Medium", "High"]
    )

# Analysis function
def analyze_risk(flood, waste, drainage, exposure):
    score = 0

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

    if flood in ["Medium", "High"]:
        recommendations.append("Strengthen disaster preparedness and evacuation planning.")
    if drainage == "Poor":
        recommendations.append("Prioritize drainage clearing and flood control measures.")
    if waste in ["Fair", "Poor"]:
        recommendations.append("Improve waste segregation and establish or strengthen a Materials Recovery Facility (MRF).")
    if exposure == "High":
        recommendations.append("Prioritize high-risk households for early warning and response coordination.")
    if flood == "High" and waste == "Poor":
        recommendations.append("Integrate DRRM and circular waste management actions to reduce waterway blockage and flooding risk.")

    if not recommendations:
        recommendations.append("Maintain current systems and continue regular monitoring.")

    chart_data = pd.DataFrame({
        "Factor": ["Flood", "Waste", "Drainage", "Exposure"],
        "Score": [flood_score, waste_score, drainage_score, exposure_score]
    })

    return level, score, recommendations, chart_data

# Analyze button
if st.button("Analyze"):
    level, score, recommendations, chart_data = analyze_risk(flood, waste, drainage, exposure)

    st.markdown("---")
    st.subheader(f"Assessment Result for {barangay}")

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric("Total Risk Score", score)

    with metric_col2:
        if level == "HIGH":
            st.error(f"Risk Level: {level}")
        elif level == "MODERATE":
            st.warning(f"Risk Level: {level}")
        else:
            st.success(f"Risk Level: {level}")

    st.markdown("### Risk Interpretation")
    if level == "HIGH":
        st.write("This area requires immediate intervention and priority planning action.")
    elif level == "MODERATE":
        st.write("This area requires preventive measures, preparedness improvements, and close monitoring.")
    else:
        st.write("This area is relatively stable but should continue regular monitoring and maintenance.")

    st.markdown("### Recommended Actions")
    for rec in recommendations:
        st.write(f"- {rec}")

    st.markdown("### Risk Factor Breakdown")
    st.bar_chart(chart_data.set_index("Factor"))

    st.markdown("### Planning Summary")
    st.info(
        f"For {barangay}, the current combination of hazard exposure, drainage condition, "
        f"waste management status, and population vulnerability indicates a {level.lower()} "
        f"level of concern. The recommended actions support both disaster resilience and "
        f"resource-efficiency planning."
    )

    st.markdown("### Why This Matters")
    st.write(
        "This tool helps local governments make faster, data-driven decisions by integrating "
        "disaster risk reduction and circular economy strategies into one platform."
    )
