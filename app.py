import streamlit as st

# Page settings
st.set_page_config(page_title="Eco-Resilience AI", layout="centered")

# Title
st.title("Eco-Resilience AI")
st.subheader("AI-Assisted DRRM and Circular Economy Planning Tool")

st.write("Select the conditions below and click Analyze.")

# Inputs
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

drainage = st.selectbox(
    "Drainage Condition",
    ["Good", "Fair", "Poor"]
)

exposure = st.selectbox(
    "Population Exposure",
    ["Low", "Medium", "High"]
)

# Analysis Logic
def analyze_risk(flood, waste, drainage, exposure):
    score = 0

    # Flood
    if flood == "High":
        score += 3
    elif flood == "Medium":
        score += 2
    else:
        score += 1

    # Waste
    if waste == "Poor":
        score += 3
    elif waste == "Fair":
        score += 2
    else:
        score += 1

    # Drainage
    if drainage == "Poor":
        score += 3
    elif drainage == "Fair":
        score += 2
    else:
        score += 1

    # Exposure
    if exposure == "High":
        score += 3
    elif exposure == "Medium":
        score += 2
    else:
        score += 1

    # Risk Level
    if score >= 10:
        level = "HIGH"
    elif score >= 7:
        level = "MODERATE"
    else:
        level = "LOW"

    # Recommendations
    recommendations = []

    if flood in ["Medium", "High"]:
        recommendations.append("Strengthen disaster preparedness and evacuation planning.")

    if drainage == "Poor":
        recommendations.append("Prioritize drainage clearing and flood control measures.")

    if waste in ["Fair", "Poor"]:
        recommendations.append("Improve waste segregation and establish Materials Recovery Facility (MRF).")

    if exposure == "High":
        recommendations.append("Prioritize high-risk households for early warning systems.")

    if flood == "High" and waste == "Poor":
        recommendations.append("Integrate DRRM and circular waste management to reduce waterway blockage.")

    if not recommendations:
        recommendations.append("Maintain current systems and continue monitoring.")

    return level, recommendations

# Button
if st.button("Analyze"):
    level, recommendations = analyze_risk(flood, waste, drainage, exposure)

    st.success(f"Risk Level for {barangay}: {level}")

    st.markdown("### Recommended Actions")
    for rec in recommendations:
        st.write(f"- {rec}")

    st.markdown("### Planning Insight")
    st.info(
        f"{barangay} requires a balanced strategy combining disaster resilience and resource efficiency."
    )
