import sqlite3
import uuid
from datetime import datetime, date
from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


APP_TITLE = "CSU General Services Office Digital Operations Platform"
DB_PATH = Path("gso_operations.db")

CSU_GREEN = "#0f3d2e"
CSU_GOLD = "#d4a017"
LIGHT_GREEN = "#e7f3ec"

UNITS = [
    "Facility Maintenance Unit",
    "Landscaping Unit",
    "Transportation Unit",
    "GSO Admin / Service Desk"
]

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


st.markdown(f"""
<style>
.block-container {{
    padding-top: 1rem;
}}

.main {{
    background: linear-gradient(135deg, #f8faf9 0%, #eef7f0 100%);
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {CSU_GREEN} 0%, #123828 100%);
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.gso-hero {{
    background: linear-gradient(135deg, {CSU_GREEN}, #1f6b4a);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 20px;
    border-left: 8px solid {CSU_GOLD};
}}

.gso-hero h1 {{
    margin-bottom: 4px;
    font-size: 30px;
}}

.gso-card {{
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #d9e7dc;
    box-shadow: 0 4px 14px rgba(15, 61, 46, 0.08);
}}

.small-muted {{
    color:#64748b;
    font-size:0.9rem;
}}

.section-title {{
    color: {CSU_GREEN};
    border-left: 6px solid {CSU_GOLD};
    padding-left: 10px;
    font-weight: 700;
    margin-top: 12px;
}}
</style>
""", unsafe_allow_html=True)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


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


def insert_record(table, data):
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
        "hazard", "blocked road", "emergency", "leak near electrical",
        "septic", "unsafe", "danger"
    ]

    complexity_terms = [
        "renovation", "construction", "program of works", "estimate",
        "procurement", "upgrade", "development", "design", "budget",
        "multiple buildings", "campus-wide", "minor construction",
        "installation", "improvement", "redevelopment"
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

    if safety >= 4 or any(term in text_l for term in emergency_terms):
        classification = "Emergency"
    elif any(term in text_l for term in complexity_terms) or (cost and cost >= 50000):
        classification = "Special Project"
    else:
        classification = "Routine"

    notes = []

    if classification == "Emergency":
        notes.append("Immediate action is recommended due to safety risk, service disruption, or possible damage to University property.")

    if classification == "Special Project":
        notes.append("This request may require planning, cost estimate, procurement, technical assessment, budget approval, or programmed implementation.")

    if classification == "Routine":
        notes.append("This request may be queued as regular service work, subject to manpower, material availability, and unit schedule.")

    if priority in ["P1 - Critical", "P2 - High"]:
        notes.append("The GSO Service Desk and concerned Unit Head should prioritize validation and deployment.")

    return classification, priority, min(score, 200), " ".join(notes)


def pdf_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CSUTitle",
        parent=styles["Title"],
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor(CSU_GREEN),
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name="CSUSubtitle",
        parent=styles["Normal"],
        fontSize=8,
        alignment=1,
        textColor=colors.black,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name="FormTitle",
        parent=styles["Title"],
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor(CSU_GREEN),
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=9,
        textColor=colors.white,
        backColor=colors.HexColor(CSU_GREEN),
        leftIndent=4,
        spaceBefore=6,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["Normal"],
        fontSize=7,
        leading=9
    ))

    styles.add(ParagraphStyle(
        name="SmallCenter",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        alignment=1
    ))

    return styles


def add_pdf_header(story, styles, title, form_no):
    header = [
        [Paragraph("<b>CARAGA STATE UNIVERSITY</b>", styles["CSUTitle"])],
        [Paragraph("General Services Office", styles["CSUSubtitle"])],
        [Paragraph("Ampayon, Butuan City, Philippines", styles["CSUSubtitle"])],
        [Paragraph(f"<b>{title}</b>", styles["FormTitle"])],
        [Paragraph(f"Reference No.: {form_no}", styles["CSUSubtitle"])]
    ]

    table = Table(header, colWidths=[7.2 * inch])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(CSU_GREEN)),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(LIGHT_GREEN)),
        ("LINEBELOW", (0, 2), (-1, 2), 1, colors.HexColor(CSU_GOLD)),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    story.append(Spacer(1, 8))


def build_field_table(data, styles):
    rows = []
    for key, value in data.items():
        rows.append([
            Paragraph(f"<b>{key}</b>", styles["Small"]),
            Paragraph(str(value) if value else "", styles["Small"])
        ])

    table = Table(rows, colWidths=[2.1 * inch, 5.1 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_signature_table(signatories, styles):
    rows = []
    for label, name in signatories:
        rows.append([
            Paragraph(
                f"<br/><br/>_____________________________________<br/>"
                f"<b>{name}</b><br/>{label}<br/>Date/Time: ___________________",
                styles["SmallCenter"]
            )
        ])

    table = Table(rows, colWidths=[7.2 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def generate_pdf_form(title, form_no, sections, signatories, footer_note=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = pdf_styles()
    story = []

    add_pdf_header(story, styles, title, form_no)

    for section_title, data in sections:
        story.append(Paragraph(section_title, styles["SectionHeader"]))
        story.append(build_field_table(data, styles))
        story.append(Spacer(1, 8))

    story.append(Paragraph("SIGNATURES AND APPROVAL", styles["SectionHeader"]))
    story.append(build_signature_table(signatories, styles))

    if footer_note:
        story.append(Spacer(1, 8))
        story.append(Paragraph(footer_note, styles["Small"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "This is a system-generated institutional form of the CSU General Services Office. "
        "Printed copies shall be signed by the concerned personnel for official processing.",
        styles["Small"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_work_order_pdf(row):
    sections = [
        ("I. REQUESTOR INFORMATION", {
            "Work Order No.": row.get("id"),
            "Date Filed": row.get("created_at"),
            "Requestor": row.get("requestor"),
            "Position / Designation": row.get("position"),
            "Contact No.": row.get("contact"),
            "Email Address": row.get("email"),
            "Requesting Office": row.get("office"),
            "Building / Location": row.get("building"),
        }),
        ("II. WORK REQUEST DETAILS", {
            "Concerned GSO Unit": row.get("unit"),
            "Scope / Type of Work": row.get("request_type"),
            "Classification": row.get("classification"),
            "Priority Level": row.get("priority"),
            "Status": row.get("status"),
            "Purpose": row.get("purpose"),
            "Work Description": row.get("description"),
            "Preferred Schedule": f"{row.get('schedule_from')} to {row.get('schedule_to')}",
            "Site Access": row.get("site_access"),
            "Required Documents": row.get("docs"),
        }),
        ("III. RAPID / AI-ASSISTED INITIAL ASSESSMENT", {
            "Safety Risk": row.get("safety_risk"),
            "Users Affected": row.get("users_affected"),
            "Operational Impact": row.get("operational_impact"),
            "Estimated Cost": row.get("estimated_cost"),
            "AI Score": row.get("ai_score"),
            "Assessment Notes": row.get("ai_notes"),
            "Recommended Action": row.get("recommended_action"),
        })
    ]

    signatories = [
        ("Requestor / Authorized Personnel", row.get("requestor", "")),
        ("Checked and Reviewed by Unit Head", "Concerned Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form(
        "SERVICE REQUEST / WORK ORDER FORM",
        row.get("id"),
        sections,
        signatories,
        "Work is allowed only on approved dates, approved locations, and approved scope. "
        "Any variation, additional work, safety concern, or budget requirement shall be endorsed for proper approval."
    )


def generate_rapid_pdf(row):
    sections = [
        ("I. RAPID ASSESSMENT DETAILS", {
            "Work Order Ref. No.": row.get("id"),
            "Date Assessed": row.get("updated_at"),
            "Facility / Location": row.get("building"),
            "Nature of Concern": row.get("description"),
            "Concerned Unit": row.get("unit"),
        }),
        ("II. RISK AND PRIORITY INDEX", {
            "Safety Risk Level": row.get("safety_risk"),
            "Users Affected": row.get("users_affected"),
            "Operational Impact": row.get("operational_impact"),
            "Estimated Cost": row.get("estimated_cost"),
            "Priority Level": row.get("priority"),
            "Classification": row.get("classification"),
            "AI Score": row.get("ai_score"),
            "Assessment Notes": row.get("ai_notes"),
            "Recommended Action": row.get("recommended_action"),
        })
    ]

    signatories = [
        ("Assessed by", "GSO Technical Personnel"),
        ("Checked and Reviewed by", "Concerned Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form("RISK ASSESSMENT & PRIORITY INDEX FOR DEPLOYMENT", row.get("id"), sections, signatories)


def generate_wds_pdf(dep_row, req_row):
    sections = [
        ("I. DEPLOYMENT REFERENCE", {
            "WDS No.": dep_row.get("id"),
            "Work Order Ref. No.": dep_row.get("request_id"),
            "Date Assigned": dep_row.get("created_at"),
            "Work Location": req_row.get("building") if req_row else "",
            "Requesting Office": req_row.get("office") if req_row else "",
            "Concerned Unit": req_row.get("unit") if req_row else "",
        }),
        ("II. WORKFORCE DEPLOYMENT DETAILS", {
            "Team Leader": dep_row.get("team_leader"),
            "Start Date": dep_row.get("start_date"),
            "Target Completion": dep_row.get("target_completion"),
            "Safety PPE Required": dep_row.get("ppe"),
            "Assigned Personnel": dep_row.get("personnel"),
            "Tools Needed": dep_row.get("tools"),
            "Materials Needed": dep_row.get("materials"),
            "Scope of Works": dep_row.get("scope"),
            "Recommended Action": dep_row.get("action"),
        })
    ]

    signatories = [
        ("Prepared by", "GSO Technical Personnel / Team Leader"),
        ("Checked and Reviewed by", "Concerned Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form("WORKFORCE DEPLOYMENT SLIP", dep_row.get("id"), sections, signatories)


def generate_prime_pdf(comp_row, req_row):
    sections = [
        ("I. COMPLETION REFERENCE", {
            "PRIME No.": comp_row.get("id"),
            "Work Order Ref. No.": comp_row.get("request_id"),
            "Date Completed": comp_row.get("date_completed"),
            "Actual Completion Time": comp_row.get("actual_completion"),
            "Work Location": req_row.get("building") if req_row else "",
            "Requesting Office": req_row.get("office") if req_row else "",
        }),
        ("II. COMPLETION DETAILS", {
            "Work Performed": comp_row.get("work_performed"),
            "Tools Used": comp_row.get("tools_used"),
            "Materials Used": comp_row.get("materials_used"),
            "Assigned Personnel": comp_row.get("personnel"),
            "Scope of Works": comp_row.get("scope"),
            "Issues Encountered": comp_row.get("issues"),
            "Final Condition": comp_row.get("final_condition"),
            "Site Status": comp_row.get("site_status"),
            "Completion Rating": comp_row.get("rating"),
            "Post-Completion Requirements": comp_row.get("post_requirements"),
            "User Acknowledgement": comp_row.get("user_ack"),
        })
    ]

    signatories = [
        ("Prepared by", "GSO Technical Personnel / Team Leader"),
        ("User Acknowledgement", comp_row.get("user_ack", "")),
        ("Verified by", "Concerned Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form("PROJECT RESOLUTION, INSPECTION & MAINTENANCE EXIT REPORT", comp_row.get("id"), sections, signatories)


def generate_ready_pdf(row):
    sections = [
        ("I. EMERGENCY REPORT DETAILS", {
            "READY No.": row.get("id"),
            "Date / Time Reported": row.get("created_at"),
            "Reported by": row.get("reported_by"),
            "Requesting Office / Department": row.get("office"),
            "Exact Location / Building": row.get("location"),
            "Contact No.": row.get("contact"),
        }),
        ("II. INCIDENT AND RESPONSE DETAILS", {
            "Incident Category": row.get("incident_category"),
            "Priority Level": row.get("priority"),
            "Nature of Emergency Concern": row.get("concern"),
            "Immediate Hazard Present": row.get("hazard_present"),
            "Hazard Description": row.get("hazard_description"),
            "Affected Occupants / Operations": row.get("affected_operations"),
            "Area Secured / Isolated": row.get("area_secured"),
            "GSO Responding Team": row.get("responding_team"),
            "Initial Action Taken": row.get("initial_action"),
            "Temporary Corrective Measures": row.get("temporary_measures"),
            "Utilities Isolated": row.get("utilities_isolated"),
            "Area Declared Safe": row.get("declared_safe"),
            "Further Repair Required": row.get("further_repair"),
            "Follow-up Work Order No.": row.get("followup_wo"),
            "Final Status": row.get("final_status"),
            "Findings / Recommendations": row.get("findings"),
        })
    ]

    signatories = [
        ("Prepared by", "GSO Responding Team / Team Leader"),
        ("Verified by", "Concerned Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form("RAPID EMERGENCY ASSISTANCE FOR DAMAGE & YIELD RECOVERY", row.get("id"), sections, signatories)


def generate_transport_pdf(row):
    distance = ""
    try:
        distance = float(row.get("odometer_end") or 0) - float(row.get("odometer_start") or 0)
    except Exception:
        distance = ""

    sections = [
        ("I. VEHICLE ASSIGNMENT DETAILS", {
            "Transport Ref. No.": row.get("id"),
            "Date Created": row.get("created_at"),
            "Vehicle / Plate No.": row.get("vehicle"),
            "Driver": row.get("driver"),
            "Requesting Office": row.get("requesting_office"),
            "Trip Date": row.get("trip_date"),
            "Destination": row.get("destination"),
            "Purpose": row.get("purpose"),
            "No. of Passengers": row.get("passengers"),
        }),
        ("II. UTILIZATION AND MONITORING", {
            "Fuel Used / Issued in Liters": row.get("fuel_liters"),
            "Odometer Start": row.get("odometer_start"),
            "Odometer End": row.get("odometer_end"),
            "Distance Travelled": distance,
            "Status": row.get("status"),
            "Remarks": row.get("remarks"),
        })
    ]

    signatories = [
        ("Requested / Confirmed by", row.get("requesting_office", "")),
        ("Driver", row.get("driver", "")),
        ("Checked and Reviewed by", "Transportation Unit Head"),
        ("Approved by", "ENGR. MARIEL M. DELO, Director, General Services Office")
    ]

    return generate_pdf_form("TRANSPORTATION SERVICE / VEHICLE UTILIZATION FORM", row.get("id"), sections, signatories)


init_db()


with st.sidebar:
    st.title("🏛️ CSU GSO")
    st.caption("Digital Operations Platform")
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
    st.markdown("---")
    st.caption("Prototype v2 · Institutional Forms · SQLite")


st.markdown(f"""
<div class="gso-hero">
    <h1>{APP_TITLE}</h1>
    <p>Institutional request intake, AI-assisted triage, deployment, emergency response, completion reporting, transportation monitoring, and printable approval forms.</p>
</div>
""", unsafe_allow_html=True)


if page == "Dashboard":
    req = read_table("requests")
    ready = read_table("ready_reports")
    dep = read_table("deployments")
    comp = read_table("completions")
    veh = read_table("vehicles")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Requests", len(req))

    if not req.empty:
        c2.metric("Active", int(req[~req["status"].isin(["Completed", "Cancelled"])].shape[0]))
        c3.metric("Emergency", int((req["classification"] == "Emergency").sum()))
        c4.metric("Special Projects", int((req["classification"] == "Special Project").sum()))
    else:
        c2.metric("Active", 0)
        c3.metric("Emergency", 0)
        c4.metric("Special Projects", 0)

    c5.metric("READY Reports", len(ready))

    st.markdown('<h3 class="section-title">Operations Overview</h3>', unsafe_allow_html=True)

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

        col3, col4 = st.columns(2)

        with col3:
            st.write("Requests by Classification")
            st.bar_chart(req["classification"].value_counts())

        with col4:
            st.write("Requests by Priority")
            st.bar_chart(req["priority"].value_counts())

        st.markdown('<h3 class="section-title">Recent Requests</h3>', unsafe_allow_html=True)
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
    st.markdown('<h3 class="section-title">Digital Service Request / Work Order Intake</h3>', unsafe_allow_html=True)

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

        insert_record("requests", {
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
    st.markdown('<h3 class="section-title">RAPID: Risk Assessment & Priority Index for Deployment</h3>', unsafe_allow_html=True)

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

            r2 = get_request(req_id)
            pdf = generate_rapid_pdf(r2)
            st.download_button(
                "Download RAPID PDF",
                data=pdf,
                file_name=f"{req_id}_RAPID.pdf",
                mime="application/pdf"
            )


elif page == "READY Emergency":
    st.markdown('<h3 class="section-title">READY: Rapid Emergency Assistance for Damage & Yield Recovery</h3>', unsafe_allow_html=True)

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

        insert_record("ready_reports", {
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

            insert_record("requests", {
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
    st.markdown('<h3 class="section-title">Workforce Deployment Slip</h3>', unsafe_allow_html=True)

    req = read_table("requests")

    if req.empty:
        st.info("No active requests available.")
    else:
        active = req[~req["status"].isin(["Completed", "Cancelled"])]
        if active.empty:
            st.info("No active requests available for deployment.")
        else:
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

                insert_record("deployments", {
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
    st.markdown('<h3 class="section-title">PRIME: Project Resolution, Inspection & Maintenance Exit Report</h3>', unsafe_allow_html=True)

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

            insert_record("completions", {
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
    st.markdown('<h3 class="section-title">Transportation Unit: Vehicle Assignment, Utilization, Fuel and Monitoring</h3>', unsafe_allow_html=True)

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

        insert_record("vehicles", {
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
    st.markdown('<h3 class="section-title">Records, Search, CSV Export, and Printable Institutional Forms</h3>', unsafe_allow_html=True)

    tabs = st.tabs(["Requests / WO", "Deployments / WDS", "Completions / PRIME", "READY", "Transportation"])
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

            if not df.empty:
                st.markdown("#### Printable Institutional Form")

                selected_id = st.selectbox(
                    "Select Record to Print",
                    df["id"].tolist(),
                    key=f"print_{table}"
                )

                selected = df[df["id"] == selected_id].iloc[0].to_dict()

                if table == "requests":
                    pdf = generate_work_order_pdf(selected)
                    fname = f"{selected_id}_GSO_Work_Order.pdf"

                elif table == "deployments":
                    req_row = get_request(selected.get("request_id"))
                    pdf = generate_wds_pdf(selected, req_row)
                    fname = f"{selected_id}_GSO_WDS.pdf"

                elif table == "completions":
                    req_row = get_request(selected.get("request_id"))
                    pdf = generate_prime_pdf(selected, req_row)
                    fname = f"{selected_id}_GSO_PRIME.pdf"

                elif table == "ready_reports":
                    pdf = generate_ready_pdf(selected)
                    fname = f"{selected_id}_GSO_READY.pdf"

                elif table == "vehicles":
                    pdf = generate_transport_pdf(selected)
                    fname = f"{selected_id}_GSO_Transportation.pdf"

                st.download_button(
                    "Download Printable PDF Form",
                    data=pdf,
                    file_name=fname,
                    mime="application/pdf",
                    key=f"download_pdf_{table}_{selected_id}"
                )


elif page == "Admin Guide":
    st.markdown('<h3 class="section-title">Prototype Guide and Recommended Office Workflow</h3>', unsafe_allow_html=True)

    st.markdown("""
### Core Institutional Workflow

1. The Service Desk receives the request through the **New Service Request** page.
2. The system suggests a classification and priority using safety risk, affected users, operational impact, estimated cost, and key words.
3. The concerned personnel validates the request through **RAPID Assessment**.
4. Approved work is moved to **Workforce Deployment** for team assignment, PPE, tools, materials, and target completion.
5. Completed work is closed through **PRIME Completion Report**.
6. Emergency events are handled through **READY Emergency** and may create a follow-up work order.
7. Vehicle assignments, fuel use, and utilization are recorded under **Transportation Log**.
8. Printable forms may be downloaded under **Records & Export**.

### Classification Rules

**Emergency**  
Danger to people or property, exposed wires, flooding, blocked road, no water, no power, unsafe condition, or operations disruption.

**Routine**  
Daily, recurring, minor, scheduled, or quick-response work using available manpower and materials.

**Special Project**  
Work requiring planning, budget, procurement, approval, technical drawings, estimates, or programmed implementation.

### Current Prototype Coverage

- Work Order / Service Request
- RAPID Risk Assessment
- READY Emergency Response
- WDS Workforce Deployment
- PRIME Completion Report
- Transportation Log
- Dashboard
- CSV Export
- Printable PDF Institutional Forms

### Recommended Next Development

- Add user login and role-based access.
- Add official CSU logo upload in the PDF header.
- Add email notification to requestor, unit head, and director.
- Add file upload for photos, letters, safety permits, and cost estimates.
- Add PostgreSQL database for full deployment.
- Add public requestor portal and internal GSO management portal.
""")
