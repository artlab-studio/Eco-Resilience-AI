import streamlit as st
import sqlite3, uuid
from datetime import datetime, date
from pathlib import Path
import pandas as pd

APP_TITLE = "CSU General Services Office Digital Operations Platform"
DB_PATH = Path("gso_operations.db")

UNITS = ["Facility Maintenance Unit", "Landscaping Unit", "Transportation Unit", "GSO Admin / Service Desk"]

REQUEST_TYPES = [
    "Electrical Works", "Plumbing Works", "Civil Works", "Carpentry", "Masonry",
    "Welding / Hotworks", "Electronics", "Aircon / HVAC", "Grounds Maintenance",
    "Janitorial / Utility", "Solid Waste & Sustainability", "Hauling / Clearing",
    "Vehicle Assignment", "Vehicle Repair / Maintenance", "Fuel Usage",
    "Drafting / Estimates", "Program of Works", "Data Request",
    "Procurement / Service Request", "Others"
]

PPE = [
    "Hard Hat", "Safety Shoes", "Gloves", "Goggles", "Harness",
    "Mask", "Reflectorized Vest", "Face Shield"
]

st.set_page_config(
    page_title="CSU GSO Platform",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
.small-muted {color:#64748b;font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id TEXT PRIMARY KEY,
        created_at TEXT,
        updated_at TEXT,
        requestor TEXT,
        position TEXT,
        contact TEXT,
        email TEXT,
        office TEXT,
        building TEXT,
        unit TEXT,
        request_type TEXT,
        classification TEXT,
        priority TEXT,
        status TEXT,
        purpose TEXT,
        description TEXT,
        schedule_from TEXT,
        schedule_to TEXT,
        site_access TEXT,
        docs TEXT,
        safety_risk INTEGER,
        users_affected INTEGER,
        operational_impact INTEGER,
        estimated_cost REAL,
        ai_score INTEGER,
        ai_notes TEXT,
        recommended_action TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS deployments(
        id TEXT PRIMARY KEY,
        request_id TEXT,
        created_at TEXT,
        team_leader TEXT,
        start_date TEXT,
        target_completion TEXT,
        personnel TEXT,
        ppe TEXT,
        tools TEXT,
        materials TEXT,
        scope TEXT,
        action TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS completions(
        id TEXT PRIMARY KEY,
        request_id TEXT,
        created_at TEXT,
        date_completed TEXT,
        actual_completion TEXT,
        work_performed TEXT,
        tools_used TEXT,
        materials_used TEXT,
        personnel TEXT,
        scope TEXT,
        issues TEXT,
        final_condition TEXT,
        site_status TEXT,
        rating TEXT,
        post_requirements TEXT,
        user_ack TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ready_reports(
        id TEXT PRIMARY KEY,
        created_at TEXT,
        reported_by TEXT,
        office TEXT,
        location TEXT,
        contact TEXT,
        incident_category TEXT,
        priority TEXT,
        concern TEXT,
        hazard_present TEXT,
        hazard_description TEXT,
        affected_operations TEXT,
        area_secured TEXT,
        responding_team TEXT,
        initial_action TEXT,
        temporary_measures TEXT,
        utilities_isolated TEXT,
        declared_safe TEXT,
        further_repair TEXT,
        followup_wo TEXT,
        restoration_time TEXT,
        actual_completion TEXT,
        final_status TEXT,
        findings TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vehicles(
        id TEXT PRIMARY KEY,
        created_at TEXT,
        vehicle TEXT,
        driver TEXT,
        requesting_office TEXT,
        trip_date TEXT,
        destination TEXT,
        purpose TEXT,
        passengers INTEGER,
        fuel_liters REAL,
        odometer_start REAL,
        odometer_end REAL,
        status TEXT,
        remarks TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert(table, data):
    conn = get_conn()
    cur = conn.cursor()
    keys = list(data.keys())
    placeholders = ",".join(["?"] * len(keys))
    cur.execute(
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
        [data[k] for k in keys]
    )
    conn.commit()
    conn.close()


def update_request_status(req_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE requests SET status=?, updated_at=? WHERE id=?",
        (status, now(), req_id)
    )
    conn.commit()
    conn.close()


def read_table(table):
    conn = get_conn()
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_request(req_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM requests WHERE id=?", (req_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def calc_priority(safety, affected, impact, cost, text):
    text_l = (text or "").lower()

    emergency_terms = [
        "fire", "exposed wire", "flood", "fallen tree", "overflow",
        "no water", "no electricity", "collapse", "accident",
        "hazard", "blocked road", "emergency"
    ]

    complexity_terms = [
        "renovation", "construction", "program of works", "estimate",
        "procurement", "upgrade", "development", "design", "budget",
        "multiple buildings", "campus-wide"
    ]

    score = safety * 25 + affected * 15 + impact * 20

    if cost and cost >= 50000:
        score += 15

    if any(term in text_l for term in emergency_terms):
        score += 25

    if any(term in text_l for term in complexity_terms):
        score += 18

    if score >= 140:
        priority = "P1 - Critical"
    elif score >= 105:
        priority = "P2 - High"
    elif score >= 70:
        priority = "P3 - Moderate"
    elif score >= 35:
        priority = "P4 - Low"
    else:
        priority = "P5 - Scheduled / Programmed"

    if safety >= 4 or any(term in text_l for term in emergency_terms[:8]):
        classification = "Emergency"
    elif any(term in text_l for term in complexity_terms) or (cost and cost >= 50000):
        classification = "Special Project"
    else:
        classification = "Routine"

    notes = []

    if classification == "Emergency":
        notes.append("Immediate action is recommended due to possible safety risk or operational disruption.")

    if classification == "Special Project":
        notes.append("This may require planning, cost estimate, approval, procurement, or programmed implementation.")

    if classification == "Routine":
        notes.append("This can be queued as normal service work subject to manpower and materials availability.")

    if priority in ["P1 - Critical", "P2 - High"]:
        notes.append("Target response should be prioritized by the GSO Service Desk and concerned unit head.")

    return classification, priority, min(score, 200), " ".join(notes)


init_db()

with st.sidebar:
    st.title("CSU GSO")
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "New Service Request",
            "RAPID Assessment",
            "READY Emergency",
            "Workforce Deployment",
            "Completion / PRIME",
            "Transportation Log",
            "Records & Export",
            "Admin Guide"
        ]
    )
    st.caption("Prototype v1 · SQLite local database")

st.title(APP_TITLE)
st.caption("Digital request intake, triage, deployment, reporting, and monitoring for CSU General Services Office operations.")

if page == "Dashboard":
    req = read_table("requests")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Requests", len(req))

    if not req.empty:
        c2.metric("Open / Active", int(req[~req["status"].isin(["Completed", "Cancelled"])].shape[0]))
        c3.metric("Emergency", int((req["classification"] == "Emergency").sum()))
        c4.metric("Special Projects", int((req["classification"] == "Special Project").sum()))
    else:
        c2.metric("Open / Active", 0)
        c3.metric("Emergency", 0)
        c4.metric("Special Projects", 0)

    st.subheader("Operations Overview")

    if req.empty:
        st.info("No records yet. Start by creating a New Service Request.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.write("Requests by Unit")
            st.bar_chart(req["unit"].value_counts())

        with col2:
            st.write("Requests by Status")
            st.bar_chart(req["status"].value_counts())

        st.dataframe(
            req[
                [
                    "id", "created_at", "requestor", "office", "unit",
                    "request_type", "classification", "priority", "status", "building"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

elif page == "New Service Request":
    st.subheader("Digital Service Request Form / Work Order Intake")

    with st.form("request_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        requestor = c1.text_input("Requestor / Authorized Personnel")
        position = c2.text_input("Position / Designation")
        contact = c3.text_input("Contact No.")

        c4, c5, c6 = st.columns(3)
        email = c4.text_input("Email Address")
        office = c5.text_input("Requesting Office / Department")
        building = c6.text_input("Building / Exact Location")

        unit = st.selectbox("Concerned GSO Unit", UNITS)
        request_type = st.multiselect("Scope / Type of Work", REQUEST_TYPES)

        purpose = st.text_area("Purpose of Request")
        description = st.text_area("Work Description / Nature of Concern", height=130)

        c7, c8 = st.columns(2)
        schedule_from = c7.date_input("Preferred Start Date", value=date.today())
        schedule_to = c8.date_input("Preferred End Date", value=date.today())

        site_access = st.multiselect(
            "Site Access Needed",
            [
                "Ingress", "Egress", "Delivery", "Pull-out", "Room Access",
                "Utility Shutdown", "After-office Access"
            ]
        )

        docs = st.multiselect(
            "Attached / Required Documents",
            [
                "Letter Request", "Pre-Inspection Report",
                "Program of Works / Cost Estimates",
                "Material Request / Supply Availability",
                "Technical Assessment Report", "Safety Permit", "Photos",
                "Location Sketch", "Others"
            ]
        )

        st.markdown("#### AI-Assisted Initial Triage")

        c9, c10, c11, c12 = st.columns(4)
        safety = c9.slider("Safety Risk", 1, 4, 1, help="1 Low, 4 Critical")
        affected = c10.slider("Users Affected", 1, 4, 1, help="1 Few, 4 Entire Building / Large group")
        impact = c11.slider("Operational Impact", 1, 4, 1, help="1 Minor, 4 Severe")
        cost = c12.number_input("Estimated Cost (₱)", min_value=0.0, step=1000.0)

        submitted = st.form_submit_button("Submit Request")

    if submitted:
        text = " ".join(request_type) + " " + purpose + " " + description
        classification, priority, score, notes = calc_priority(safety, affected, impact, cost, text)
        rid = make_id("WO")

        insert("requests", {
            "id": rid,
            "created_at": now(),
            "updated_at": now(),
            "requestor": requestor,
            "position": position,
            "contact": contact,
            "email": email,
            "office": office,
            "building": building,
            "unit": unit,
            "request_type": ", ".join(request_type),
            "classification": classification,
            "priority": priority,
            "status": "Submitted",
            "purpose": purpose,
            "description": description,
            "schedule_from": str(schedule_from),
            "schedule_to": str(schedule_to),
            "site_access": ", ".join(site_access),
            "docs": ", ".join(docs),
            "safety_risk": safety,
            "users_affected": affected,
            "operational_impact": impact,
            "estimated_cost": cost,
            "ai_score": score,
            "ai_notes": notes,
            "recommended_action": "For GSO Service Desk assessment and routing."
        })

        st.success(f"Request submitted: {rid}")
        st.info(f"Suggested Classification: {classification} | Priority: {priority} | Score: {score}. {notes}")

elif page == "RAPID Assessment":
    st.subheader("RAPID: Risk Assessment & Priority Index for Deployment")

    req = read_table("requests")

    if req.empty:
        st.info("No service requests available.")
    else:
        req_id = st.selectbox("Select Work Order", req["id"].tolist())
        r = get_request(req_id)

        st.write(f"**Location:** {r['building']}")
        st.write(f"**Unit:** {r['unit']}")
        st.write(f"**Current Classification:** {r['classification']}")
        st.write(f"**Current Priority:** {r['priority']}")

        with st.form("rapid"):
            c1, c2, c3, c4 = st.columns(4)

            safety = c1.slider("Safety Risk", 1, 4, int(r["safety_risk"] or 1))
            affected = c2.slider("Users Affected", 1, 4, int(r["users_affected"] or 1))
            impact = c3.slider("Operational Impact", 1, 4, int(r["operational_impact"] or 1))
            cost = c4.number_input(
                "Estimated Cost (₱)",
                min_value=0.0,
                value=float(r["estimated_cost"] or 0),
                step=1000.0
            )

            action = st.text_area("Recommended Action", value=r.get("recommended_action") or "")

            status = st.selectbox(
                "Next Status",
                ["For Approval", "Approved", "Assigned", "Deferred", "Cancelled"]
            )

            go = st.form_submit_button("Save RAPID Assessment")

        if go:
            classification, priority, score, notes = calc_priority(
                safety,
                affected,
                impact,
                cost,
                r["description"] + " " + r["purpose"]
            )

            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                UPDATE requests
                SET safety_risk=?, users_affected=?, operational_impact=?,
                    estimated_cost=?, classification=?, priority=?, ai_score=?,
                    ai_notes=?, recommended_action=?, status=?, updated_at=?
                WHERE id=?
            """, (
                safety, affected, impact, cost, classification, priority,
                score, notes, action, status, now(), req_id
            ))

            conn.commit()
            conn.close()

            st.success(f"RAPID saved. Classification: {classification}; Priority: {priority}; Score: {score}")

elif page == "READY Emergency":
    st.subheader("READY: Rapid Emergency Assistance for Damage & Yield Recovery")

    with st.form("ready", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        reported_by = c1.text_input("Reported by")
        office = c2.text_input("Requesting Office / Department")
        contact = c3.text_input("Contact No.")

        location = st.text_input("Exact Location / Building")

        c4, c5 = st.columns(2)
        category = c4.selectbox(
            "Incident Category",
            [
                "Civil/Structural", "Electrical", "Plumbing", "Mechanical",
                "Grounds", "Safety Hazard", "Flooding", "Vehicle", "Other"
            ]
        )
        priority = c5.selectbox("Priority Level", ["Critical", "High", "Moderate", "Low"])

        concern = st.text_area("Nature of Emergency Concern")
        hazard = st.radio("Immediate Hazard Present?", ["Yes", "No"], horizontal=True)
        hazard_desc = st.text_area("Hazard Description")
        affected_ops = st.text_area("Affected Occupants / Operations")
        area_secured = st.radio("Area Secured / Isolated?", ["Yes", "No"], horizontal=True)

        team = st.text_input("GSO Responding Team / Team Leader")
        initial = st.text_area("Initial Action Taken")
        temp = st.text_area("Temporary Corrective Measures")

        utilities = st.multiselect("Utilities Isolated", ["Power", "Water", "ICT", "None"])
        safe = st.radio("Area Declared Safe?", ["Yes", "No"], horizontal=True)
        further = st.radio("Further Repair Required?", ["Yes", "No"], horizontal=True)

        final_status = st.selectbox(
            "Final Status",
            ["Resolved", "Temporary Fix", "For Major Repair", "Endorsed"]
        )

        findings = st.text_area("Findings / Recommendations")

        submitted = st.form_submit_button("Save READY Report")

    if submitted:
        rid = make_id("READY")
        followup = make_id("WO") if further == "Yes" else ""

        insert("ready_reports", {
            "id": rid,
            "created_at": now(),
            "reported_by": reported_by,
            "office": office,
            "location": location,
            "contact": contact,
            "incident_category": category,
            "priority": priority,
            "concern": concern,
            "hazard_present": hazard,
            "hazard_description": hazard_desc,
            "affected_operations": affected_ops,
            "area_secured": area_secured,
            "responding_team": team,
            "initial_action": initial,
            "temporary_measures": temp,
            "utilities_isolated": ", ".join(utilities),
            "declared_safe": safe,
            "further_repair": further,
            "followup_wo": followup,
            "restoration_time": "",
            "actual_completion": "",
            "final_status": final_status,
            "findings": findings
        })

        if further == "Yes":
            priority_map = {
                "Critical": "P1 - Critical",
                "High": "P2 - High",
                "Moderate": "P3 - Moderate",
                "Low": "P4 - Low"
            }

            insert("requests", {
                "id": followup,
                "created_at": now(),
                "updated_at": now(),
                "requestor": reported_by,
                "position": "",
                "contact": contact,
                "email": "",
                "office": office,
                "building": location,
                "unit": "Facility Maintenance Unit",
                "request_type": category,
                "classification": "Emergency",
                "priority": priority_map[priority],
                "status": "Submitted",
                "purpose": "Follow-up work order from READY emergency report",
                "description": concern,
                "schedule_from": str(date.today()),
                "schedule_to": str(date.today()),
                "site_access": "Emergency access",
                "docs": "READY report",
                "safety_risk": 4 if priority == "Critical" else 3,
                "users_affected": 3,
                "operational_impact": 3,
                "estimated_cost": 0,
                "ai_score": 150,
                "ai_notes": "Auto-created from emergency READY report.",
                "recommended_action": "Immediate assessment and deployment."
            })

        st.success(
            f"READY report saved: {rid}" +
            (f". Follow-up work order created: {followup}" if followup else "")
        )

elif page == "Workforce Deployment":
    st.subheader("Workforce Deployment Slip")

    req = read_table("requests")

    if req.empty:
        st.info("No active requests available.")
    else:
        active = req[~req["status"].isin(["Completed", "Cancelled"])]
        req_id = st.selectbox("Select Work Order", active["id"].tolist())

        with st.form("deploy", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            leader = c1.text_input("Team Leader")
            start = c2.date_input("Start Date", value=date.today())
            target = c3.date_input("Target Completion", value=date.today())

            ppe = st.multiselect("Safety PPE Required", PPE)
            personnel = st.text_area("Assigned Personnel, one per line with designation")
            tools = st.text_area("Tools Needed, quantity/unit/item")
            materials = st.text_area("Materials Needed, quantity/unit/item")
            scope = st.text_area("Scope of Works")
            action = st.text_area("Recommended Action")

            submitted = st.form_submit_button("Save Deployment")

        if submitted:
            did = make_id("WDS")

            insert("deployments", {
                "id": did,
                "request_id": req_id,
                "created_at": now(),
                "team_leader": leader,
                "start_date": str(start),
                "target_completion": str(target),
                "personnel": personnel,
                "ppe": ", ".join(ppe),
                "tools": tools,
                "materials": materials,
                "scope": scope,
                "action": action
            })

            update_request_status(req_id, "Assigned")
            st.success(f"Deployment saved: {did}")

elif page == "Completion / PRIME":
    st.subheader("PRIME: Project Resolution, Inspection & Maintenance Exit Report")

    req = read_table("requests")

    if req.empty:
        st.info("No requests available.")
    else:
        req_id = st.selectbox("Select Work Order", req["id"].tolist())

        with st.form("prime", clear_on_submit=True):
            c1, c2 = st.columns(2)
            completed = c1.date_input("Date Completed", value=date.today())
            actual = c2.text_input("Actual Completion Time / Duration")

            work = st.multiselect(
                "Work Performed",
                [
                    "Repair", "Renovation", "Installation", "Maintenance",
                    "Fabrication", "Emergency Response", "Transport Support",
                    "Grounds Maintenance"
                ]
            )

            tools = st.text_area("Tools Used")
            materials = st.text_area("Materials Used")
            personnel = st.text_area("Assigned Personnel")
            scope = st.text_area("Actual Scope of Works Performed")
            issues = st.text_area("Issues Encountered")

            c3, c4, c5 = st.columns(3)
            condition = c3.selectbox(
                "Final Condition",
                ["Fully Completed", "Partially Completed", "Deferred", "For Rework"]
            )

            site_status = c4.multiselect(
                "Site Status",
                ["Cleaned", "Safe", "Operational", "Turned Over"]
            )

            rating = c5.selectbox(
                "Completion Rating",
                ["Excellent", "Satisfactory", "Needs Follow-up", "Critical Observation"]
            )

            post = st.multiselect(
                "Post-Completion Requirements",
                [
                    "No Further Action Needed",
                    "Include in Preventive Maintenance Schedule",
                    "Requires Budget",
                    "Subject for Technical Reassessment"
                ]
            )

            ack = st.text_input("User Acknowledgement / Requestor Name")

            submitted = st.form_submit_button("Save Completion Report")

        if submitted:
            cid = make_id("PRIME")

            insert("completions", {
                "id": cid,
                "request_id": req_id,
                "created_at": now(),
                "date_completed": str(completed),
                "actual_completion": actual,
                "work_performed": ", ".join(work),
                "tools_used": tools,
                "materials_used": materials,
                "personnel": personnel,
                "scope": scope,
                "issues": issues,
                "final_condition": condition,
                "site_status": ", ".join(site_status),
                "rating": rating,
                "post_requirements": ", ".join(post),
                "user_ack": ack
            })

            update_request_status(
                req_id,
                "Completed" if condition == "Fully Completed" else condition
            )

            st.success(f"Completion report saved: {cid}")

elif page == "Transportation Log":
    st.subheader("Transportation Unit: Vehicle Assignment, Utilization, Fuel and Monitoring")

    with st.form("vehicle", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        vehicle = c1.text_input("Vehicle / Plate No.")
        driver = c2.text_input("Driver")
        office = c3.text_input("Requesting Office")

        c4, c5, c6 = st.columns(3)
        trip_date = c4.date_input("Trip Date", value=date.today())
        destination = c5.text_input("Destination")
        passengers = c6.number_input("No. of Passengers", min_value=0, step=1)

        purpose = st.text_area("Purpose of Trip / Assignment")

        c7, c8, c9 = st.columns(3)
        fuel = c7.number_input("Fuel Used / Issued in Liters", min_value=0.0, step=1.0)
        odo_start = c8.number_input("Odometer Start", min_value=0.0, step=1.0)
        odo_end = c9.number_input("Odometer End", min_value=0.0, step=1.0)

        status = st.selectbox(
            "Status",
            ["Scheduled", "Dispatched", "Completed", "Cancelled", "For Repair / Maintenance"]
        )

        remarks = st.text_area("Remarks")

        submitted = st.form_submit_button("Save Transportation Record")

    if submitted:
        vid = make_id("TRN")

        insert("vehicles", {
            "id": vid,
            "created_at": now(),
            "vehicle": vehicle,
            "driver": driver,
            "requesting_office": office,
            "trip_date": str(trip_date),
            "destination": destination,
            "purpose": purpose,
            "passengers": passengers,
            "fuel_liters": fuel,
            "odometer_start": odo_start,
            "odometer_end": odo_end,
            "status": status,
            "remarks": remarks
        })

        st.success(f"Transportation record saved: {vid}")

    df = read_table("vehicles")

    if not df.empty:
        df["distance"] = df["odometer_end"] - df["odometer_start"]
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Records & Export":
    st.subheader("Records, Search, and CSV Export")

    tabs = st.tabs(["Requests", "Deployments", "Completions", "READY", "Transportation"])
    tables = ["requests", "deployments", "completions", "ready_reports", "vehicles"]

    for tab, table in zip(tabs, tables):
        with tab:
            df = read_table(table)

            q = st.text_input(f"Search {table}", key=f"q_{table}")

            if q and not df.empty:
                mask = df.astype(str).apply(
                    lambda col: col.str.contains(q, case=False, na=False)
                ).any(axis=1)
                df = df[mask]

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                f"Download {table}.csv",
                df.to_csv(index=False).encode("utf-8"),
                file_name=f"{table}.csv",
                mime="text/csv"
            )

elif page == "Admin Guide":
    st.subheader("Prototype Guide and Recommended Office Workflow")

    st.markdown("""
### Core Workflow

1. Service Desk receives the request through the New Service Request page.
2. The system suggests classification and priority using risk, affected users, operational impact, estimated cost, and keywords.
3. RAPID validates the risk level, priority, and recommended action.
4. Workforce Deployment records assigned personnel, PPE, tools, materials, and target completion.
5. PRIME closes the work order with completion status, issues encountered, rating, and post-completion requirements.
6. READY handles emergency incidents and can automatically create a follow-up work order.
7. Transportation Log monitors vehicle assignment, trip purpose, fuel usage, odometer reading, and vehicle status.

### Classification Rules

**Emergency**  
Safety hazard, service disruption, blocked access, exposed electrical risk, flooding, no water or power, or incident affecting many users.

**Routine**  
Recurring, minor, scheduled, or quick-response work using available manpower and materials.

**Special Project**  
Work requiring planning, funding, procurement, technical drawings, program of works, or formal approval.

### Recommended Next Improvements

- Add role-based accounts for requestors, service desk, unit heads, and director.
- Add file uploads for photos, permits, cost estimates, and scanned forms.
- Add printable PDF versions of WO, RAPID, WDS, READY, and PRIME.
- Add email or SMS notification.
- Replace SQLite with PostgreSQL for full institutional deployment.
""")
