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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


APP_TITLE = "CSU General Services Office Digital Operations Platform"
DB_PATH = Path("gso_operations.db")

CSU_GREEN = "#0f3d2e"
CSU_GOLD = "#d4a017"
LIGHT_GREEN = "#e7f3ec"

DIRECTOR_NAME = "ENGR. MARIEL M. DELO"
FMU_HEAD = "ENGR. MA. ZYLPHADELLE G. VALDUHUEZA"
RESIDENT_ENGINEER = "ENGR. JOHN SALABE"

UNITS = [
    "Facility Maintenance Unit",
    "Landscaping Unit",
    "Transportation Unit",
    "GSO Admin / Service Desk"
]

WORK_CLASSIFICATIONS = [
    "Preventive Maintenance",
    "Corrective Maintenance",
    "Emergency Repair",
    "Minor Repair",
    "Major Repair",
    "Renovation / Improvement",
    "Grounds Maintenance",
    "Hauling / Clearing",
    "Fabrication",
    "Special Project"
]

REQUEST_TYPES = [
    "Electrical Works",
    "Plumbing Works",
    "Civil Works",
    "Carpentry",
    "Masonry",
    "Welding / Hotworks",
    "Electronics",
    "Vehicle",
    "Aircon / HVAC",
    "Grounds Maintenance",
    "Drafting / Estimates",
    "Program of Works",
    "Janitorial / Utility",
    "Solid Waste & Sustainability",
    "Data Request",
    "Procurement / Service Request",
    "Others"
]

PPE = [
    "Hard Hat",
    "Safety Shoes",
    "Gloves",
    "Goggles",
    "Harness",
    "Mask",
    "Reflectorized Vest",
    "Face Shield"
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
        work_classification TEXT,
        request_type TEXT,
        system_classification TEXT,
        priority TEXT,
        status TEXT,
        purpose TEXT,
        description TEXT,
        schedule_from TEXT,
        schedule_to TEXT,
        working_hours TEXT,
        access_condition TEXT,
        docs TEXT,
        safety_risk INTEGER,
        users_affected INTEGER,
        operational_impact INTEGER,
        complexity_level INTEGER,
        ai_score INTEGER,
        ai_narrative TEXT,
        recommended_action TEXT,
        special_project_note TEXT
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
        team_leader TEXT,
        slippage TEXT,
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
        team_leader TEXT,
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


def update_request_status(req_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE requests SET status=?, updated_at=? WHERE id=?",
        (status, now(), req_id)
    )
    conn.commit()
    conn.close()


def calc_ai_assessment(safety, affected, impact, complexity, text):
    text_l = (text or "").lower()

    emergency_terms = [
        "fire", "exposed wire", "flood", "fallen tree", "overflow",
        "no water", "no electricity", "collapse", "accident",
        "hazard", "blocked road", "emergency", "unsafe", "danger",
        "septic", "leak near electrical", "electrical spark"
    ]

    special_terms = [
        "renovation", "construction", "program of works", "estimate",
        "procurement", "upgrade", "development", "design", "budget",
        "multiple buildings", "campus-wide", "minor construction",
        "installation", "improvement", "redevelopment", "facility upgrade",
        "landscape development", "equipment procurement", "infrastructure"
    ]

    score = safety * 25 + affected * 15 + impact * 20 + complexity * 15

    emergency_trigger = safety >= 4 or any(term in text_l for term in emergency_terms)
    special_trigger = complexity >= 4 or any(term in text_l for term in special_terms)

    if emergency_trigger:
        system_classification = "Emergency"
    elif special_trigger:
        system_classification = "Special Project"
    else:
        system_classification = "Routine"

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

    if system_classification == "Emergency":
        narrative = (
            "The system classified this request as Emergency because the concern indicates possible danger, "
            "service interruption, or operational disruption. The score was generated using safety risk, number "
            "of affected users, operational impact, and complexity of response. Immediate validation and deployment "
            "by the concerned GSO unit is recommended."
        )
        action = "Immediate inspection, hazard control, and deployment subject to Unit Head and Director approval."
        special_note = ""

    elif system_classification == "Special Project":
        narrative = (
            "The system classified this request as Special Project because the concern appears to involve planned "
            "improvement, upgrading, development, installation, procurement, infrastructure-related work, or activity "
            "requiring programming beyond routine service. This type of request may need technical assessment, scope "
            "validation, program of works, budget allocation, and VP or executive-level approval before implementation."
        )
        action = "Endorse for technical assessment, planning, budget review, and executive approval as applicable."
        special_note = (
            "Special Projects are planned activities involving improvement, upgrading, or development of facilities "
            "and services. They may be short- to long-term, program-based, and may require funding allocation, VP or "
            "executive approval, procurement, or inclusion in the office work and financial plan."
        )

    else:
        narrative = (
            "The system classified this request as Routine because the concern appears to be regular, recurring, "
            "minor, or manageable within normal GSO operations. The request may be scheduled based on manpower, "
            "materials, urgency, and availability of the concerned unit."
        )
        action = "Queue for regular scheduling and deployment by the concerned unit."
        special_note = ""

    return system_classification, priority, min(score, 200), narrative, action, special_note


def checkbox(label, selected):
    return f"☑ {label}" if label in selected else f"☐ {label}"


def pdf_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CSUTitle",
        parent=styles["Title"],
        fontSize=13,
        alignment=1,
        textColor=colors.HexColor(CSU_GREEN),
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name="CSUSubtitle",
        parent=styles["Normal"],
        fontSize=8,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        name="FormTitle",
        parent=styles["Title"],
        fontSize=11,
        alignment=1,
        textColor=colors.HexColor(CSU_GREEN),
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["Normal"],
        fontSize=7.2,
        leading=9
    ))

    styles.add(ParagraphStyle(
        name="SmallCenter",
        parent=styles["Normal"],
        fontSize=7.2,
        leading=9,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontSize=8.5,
        textColor=colors.white,
        backColor=colors.HexColor(CSU_GREEN),
        leftIndent=4,
        spaceBefore=5,
        spaceAfter=4
    ))

    return styles


def pdf_header(story, styles, office, title, ref_no):
    header = [
        [Paragraph("<b>CARAGA STATE UNIVERSITY</b>", styles["CSUTitle"])],
        [Paragraph(office, styles["CSUSubtitle"])],
        [Paragraph("Ampayon, Butuan City, Philippines", styles["CSUSubtitle"])],
        [Paragraph(f"<b>{title}</b>", styles["FormTitle"])],
        [Paragraph(f"Reference No.: {ref_no}", styles["CSUSubtitle"])]
    ]

    table = Table(header, colWidths=[7.2 * inch])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(CSU_GREEN)),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(LIGHT_GREEN)),
        ("LINEBELOW", (0, 2), (-1, 2), 1, colors.HexColor(CSU_GOLD)),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    story.append(table)
    story.append(Spacer(1, 6))


def field_table(rows, styles, widths=None):
    if widths is None:
        widths = [1.75 * inch, 1.85 * inch, 1.75 * inch, 1.85 * inch]

    data = []
    for row in rows:
        data.append([Paragraph(str(cell or ""), styles["Small"]) for cell in row])

    table = Table(data, colWidths=widths)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def signature_block(rows, styles):
    data = []
    for label, name in rows:
        data.append([
            Paragraph(
                f"<br/><br/>_____________________________________<br/>"
                f"<b>{name}</b><br/>{label}<br/>Date & Time: ___________________",
                styles["SmallCenter"]
            )
        ])

    table = Table(data, colWidths=[7.2 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def make_pdf(title, ref_no, build_function):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=34,
        leftMargin=34,
        topMargin=28,
        bottomMargin=28
    )
    styles = pdf_styles()
    story = []
    pdf_header(story, styles, "GENERAL SERVICES OFFICE", title, ref_no)
    build_function(story, styles)
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "F-ECO-006 | Rev. 01 | System-generated institutional copy for printing, signing, routing, and approval.",
        styles["SmallCenter"]
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_work_order_pdf(r):
    selected_class = [r.get("work_classification", "")]
    selected_scope = [x.strip() for x in str(r.get("request_type", "")).split(",") if x.strip()]

    def build(story, styles):
        story.append(Paragraph("SERVICE REQUEST FORM", styles["Section"]))

        story.append(field_table([
            ["<b>WO No.</b>", r.get("id"), "<b>Date Filed</b>", r.get("created_at")],
            ["<b>Requestor</b>", r.get("requestor"), "<b>Contact No.</b>", r.get("contact")],
            ["<b>Position/Designation</b>", r.get("position"), "<b>Email Address</b>", r.get("email")],
            ["<b>Requesting Office</b>", r.get("office"), "<b>Building/Location</b>", r.get("building")],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("CLASSIFICATION AND SCOPE OF WORK", styles["Section"]))

        left = "<br/>".join([checkbox(x, selected_class) for x in WORK_CLASSIFICATIONS])
        right = "<br/>".join([checkbox(x, selected_scope) for x in REQUEST_TYPES])

        story.append(field_table([
            ["<b>Classification</b>", left, "<b>Scope of Work</b>", right]
        ], styles, widths=[1.5 * inch, 2.1 * inch, 1.5 * inch, 2.1 * inch]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("SCHEDULE AND COORDINATION", styles["Section"]))

        story.append(field_table([
            ["<b>Work Schedule / Date</b>", f"From: {r.get('schedule_from')}<br/>To: {r.get('schedule_to')}",
             "<b>Working Hours</b>", r.get("working_hours")],
            ["<b>Site Coordination / Access Condition</b>", r.get("access_condition"), "<b>Required Documents</b>", r.get("docs")],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("PURPOSE AND WORK DESCRIPTION", styles["Section"]))

        story.append(field_table([
            ["<b>Purpose</b>", r.get("purpose")],
            ["<b>Work Description</b>", r.get("description")]
        ], styles, widths=[1.7 * inch, 5.5 * inch]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("AI-ASSISTED ASSESSMENT NARRATIVE", styles["Section"]))

        story.append(field_table([
            ["<b>System Classification</b>", r.get("system_classification"), "<b>Priority Level</b>", r.get("priority")],
            ["<b>AI Score</b>", r.get("ai_score"), "<b>Recommended Action</b>", r.get("recommended_action")],
            ["<b>Assessment Narrative</b>", r.get("ai_narrative")],
            ["<b>Special Project Note</b>", r.get("special_project_note")],
        ], styles, widths=[1.7 * inch, 1.9 * inch, 1.7 * inch, 1.9 * inch]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("REQUEST CONDITIONS", styles["Section"]))
        conditions = """
        By signing below, the requestor affirms that all details provided are true and correct and that the requesting office agrees to comply with University policies, safety regulations, and applicable repair and maintenance guidelines.
        Work is allowed only on approved dates, locations, and approved scope. Any variation or additional work requires prior approval of the General Services Office. GSO personnel may access, inspect, and monitor the area as necessary for official work implementation, subject to coordination with the concerned office when sensitive documents, equipment, classes, examinations, or restricted activities are present.
        """
        story.append(Paragraph(conditions, styles["Small"]))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Signature over Printed Name of Requestor or Authorized Personnel", r.get("requestor", "")),
            ("Checked and Reviewed by", "Concerned Unit Head"),
            ("Issued / Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("SERVICE REQUEST FORM", r.get("id"), build)


def generate_rapid_pdf(r):
    safety_labels = ["Low", "Moderate", "High", "Critical"]
    affected_labels = ["Few", "Several", "Many", "Entire Building"]
    impact_labels = ["Minor", "Moderate", "Major", "Severe"]
    priority_labels = ["P1 - Critical", "P2 - High", "P3 - Moderate", "P4 - Low", "P5 - Scheduled / Programmed"]

    safety_selected = [safety_labels[int(r.get("safety_risk") or 1) - 1]]
    affected_selected = [affected_labels[int(r.get("users_affected") or 1) - 1]]
    impact_selected = [impact_labels[int(r.get("operational_impact") or 1) - 1]]
    priority_selected = [r.get("priority")]

    def build(story, styles):
        story.append(Paragraph("RISK ASSESSMENT & PRIORITY INDEX FOR DEPLOYMENT", styles["Section"]))

        story.append(field_table([
            ["<b>RAPID No.</b>", f"RAPID-{r.get('id')}", "<b>Work Order Ref. No.</b>", r.get("id")],
            ["<b>Date Assessed</b>", r.get("updated_at"), "<b>Unit</b>", r.get("unit")],
            ["<b>Facility/Location</b>", r.get("building"), "<b>Assessed by</b>", "GSO Technical Personnel"],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(field_table([
            ["<b>Nature of Concern</b>", r.get("description")]
        ], styles, widths=[1.7 * inch, 5.5 * inch]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("RISK INDEX", styles["Section"]))

        story.append(field_table([
            ["<b>Safety Risk Level</b>", "<br/>".join([checkbox(x, safety_selected) for x in safety_labels]),
             "<b>Users Affected</b>", "<br/>".join([checkbox(x, affected_selected) for x in affected_labels])],
            ["<b>Operational Impact</b>", "<br/>".join([checkbox(x, impact_selected) for x in impact_labels]),
             "<b>Priority Level</b>", "<br/>".join([checkbox(x, priority_selected) for x in priority_labels])],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("AI-ASSISTED ASSESSMENT NARRATIVE", styles["Section"]))

        story.append(field_table([
            ["<b>System Classification</b>", r.get("system_classification"), "<b>AI Score</b>", r.get("ai_score")],
            ["<b>Reason for Classification</b>", r.get("ai_narrative")],
            ["<b>Special Project / Executive Approval Context</b>", r.get("special_project_note")],
            ["<b>Recommended Action</b>", r.get("recommended_action")],
        ], styles, widths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch]))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Checked and Reviewed by", f"{FMU_HEAD}, Head, Facility Maintenance Unit"),
            ("Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("RISK ASSESSMENT & PRIORITY INDEX FOR DEPLOYMENT", f"RAPID-{r.get('id')}", build)


def generate_wds_pdf(d, r):
    selected_ppe = [x.strip() for x in str(d.get("ppe", "")).split(",") if x.strip()]

    def build(story, styles):
        story.append(Paragraph("WORKFORCE DEPLOYMENT SLIP", styles["Section"]))

        story.append(field_table([
            ["<b>WDS No.</b>", d.get("id"), "<b>Work Order Ref. No.</b>", d.get("request_id")],
            ["<b>Date Assigned</b>", d.get("created_at"), "<b>Work Location</b>", r.get("building") if r else ""],
            ["<b>Team Leader</b>", d.get("team_leader"), "<b>Start Date</b>", d.get("start_date")],
            ["<b>Target Completion</b>", d.get("target_completion"), "<b>Requesting Office</b>", r.get("office") if r else ""],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("SAFETY PPE REQUIRED", styles["Section"]))
        story.append(Paragraph("<br/>".join([checkbox(x, selected_ppe) for x in PPE]), styles["Small"]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("DEPLOYMENT DETAILS", styles["Section"]))
        story.append(field_table([
            ["<b>Tools Needed</b>", d.get("tools")],
            ["<b>Materials Needed</b>", d.get("materials")],
            ["<b>Assigned Personnel</b>", d.get("personnel")],
            ["<b>Scope of Works</b>", d.get("scope")],
            ["<b>Recommended Action</b>", d.get("action")],
        ], styles, widths=[1.7 * inch, 5.5 * inch]))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Prepared by", f"{RESIDENT_ENGINEER}, Resident Engineer"),
            ("Checked and Reviewed by", f"{FMU_HEAD}, Head, Facility Maintenance Unit"),
            ("Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("WORKFORCE DEPLOYMENT SLIP", d.get("id"), build)


def generate_prime_pdf(c, r):
    selected_work = [x.strip() for x in str(c.get("work_performed", "")).split(",") if x.strip()]
    selected_status = [x.strip() for x in str(c.get("site_status", "")).split(",") if x.strip()]
    selected_post = [x.strip() for x in str(c.get("post_requirements", "")).split(",") if x.strip()]

    def build(story, styles):
        story.append(Paragraph("PROJECT RESOLUTION, INSPECTION & MAINTENANCE EXIT REPORT", styles["Section"]))

        story.append(field_table([
            ["<b>PRIME No.</b>", c.get("id"), "<b>Work Order Ref. No.</b>", c.get("request_id")],
            ["<b>Date Completed</b>", c.get("date_completed"), "<b>Actual Completion Time</b>", c.get("actual_completion")],
            ["<b>Work Location</b>", r.get("building") if r else "", "<b>Team Leader</b>", c.get("team_leader")],
            ["<b>Slippage</b>", c.get("slippage"), "<b>Requesting Office</b>", r.get("office") if r else ""],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("WORK PERFORMED", styles["Section"]))
        work_options = ["Repair", "Renovation", "Installation", "Maintenance", "Fabrication", "Emergency Response"]
        story.append(Paragraph("<br/>".join([checkbox(x, selected_work) for x in work_options]), styles["Small"]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("COMPLETION DETAILS", styles["Section"]))

        story.append(field_table([
            ["<b>Tools Used</b>", c.get("tools_used")],
            ["<b>Materials Used</b>", c.get("materials_used")],
            ["<b>Assigned Personnel</b>", c.get("personnel")],
            ["<b>Scope of Works</b>", c.get("scope")],
            ["<b>Issues Encountered</b>", c.get("issues")],
            ["<b>Final Condition</b>", c.get("final_condition")],
            ["<b>Site Status</b>", "<br/>".join([checkbox(x, selected_status) for x in ["Cleaned", "Safe", "Operational", "Turned Over"]])],
            ["<b>Completion Rating</b>", c.get("rating")],
            ["<b>Post-Completion Requirements</b>", "<br/>".join([checkbox(x, selected_post) for x in [
                "No Further Action Needed",
                "Include in Preventive Maintenance Schedule",
                "Requires Budget",
                "Subject for Technical Reassessment"
            ]])]
        ], styles, widths=[1.8 * inch, 5.4 * inch]))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Prepared by", f"{RESIDENT_ENGINEER}, Resident Engineer"),
            ("User Acknowledgement / Requestor", c.get("user_ack", "")),
            ("Verified by", f"{FMU_HEAD}, Head, Facility Maintenance Unit"),
            ("Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("PROJECT RESOLUTION, INSPECTION & MAINTENANCE EXIT REPORT", c.get("id"), build)


def generate_ready_pdf(r):
    def build(story, styles):
        story.append(Paragraph("RAPID EMERGENCY ASSISTANCE FOR DAMAGE & YIELD RECOVERY", styles["Section"]))

        story.append(field_table([
            ["<b>READY No.</b>", r.get("id"), "<b>Date / Time Reported</b>", r.get("created_at")],
            ["<b>Reported by</b>", r.get("reported_by"), "<b>Contact No.</b>", r.get("contact")],
            ["<b>Requesting Office / Department</b>", r.get("office"), "<b>Exact Location / Building</b>", r.get("location")],
        ], styles))

        story.append(Spacer(1, 5))
        story.append(Paragraph("INCIDENT AND RESPONSE DETAILS", styles["Section"]))

        story.append(field_table([
            ["<b>Incident Category</b>", r.get("incident_category"), "<b>Priority Level</b>", r.get("priority")],
            ["<b>Nature of Emergency Concern</b>", r.get("concern")],
            ["<b>Immediate Hazard Present</b>", r.get("hazard_present"), "<b>Area Secured / Isolated</b>", r.get("area_secured")],
            ["<b>Hazard Description</b>", r.get("hazard_description")],
            ["<b>Affected Occupants / Operations</b>", r.get("affected_operations")],
            ["<b>GSO Responding Team</b>", r.get("responding_team"), "<b>Team Leader</b>", r.get("team_leader")],
            ["<b>Initial Action Taken</b>", r.get("initial_action")],
            ["<b>Temporary Corrective Measures</b>", r.get("temporary_measures")],
            ["<b>Utilities Isolated</b>", r.get("utilities_isolated"), "<b>Area Declared Safe</b>", r.get("declared_safe")],
            ["<b>Further Repair Required</b>", r.get("further_repair"), "<b>Follow-Up Work Order No.</b>", r.get("followup_wo")],
            ["<b>Estimated Restoration Time</b>", r.get("restoration_time"), "<b>Actual Completion Time</b>", r.get("actual_completion")],
            ["<b>Final Status</b>", r.get("final_status")],
            ["<b>Findings / Recommendations</b>", r.get("findings")],
        ], styles, widths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch]))

        story.append(Spacer(1, 5))
        story.append(Paragraph("RESPONSE TIME STANDARDS", styles["Section"]))
        story.append(field_table([
            ["<b>Critical</b>", "Immediate / within 15 minutes", "<b>High</b>", "Within 30 minutes"],
            ["<b>Moderate</b>", "Within 2 hours", "<b>Low</b>", "Within 24 hours"]
        ], styles))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Prepared by", f"{RESIDENT_ENGINEER}, Resident Engineer"),
            ("Verified by", f"{FMU_HEAD}, Head, Facility Maintenance Unit"),
            ("Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("READY: RAPID EMERGENCY ASSISTANCE FOR DAMAGE & YIELD RECOVERY", r.get("id"), build)


def generate_transport_pdf(r):
    try:
        distance = float(r.get("odometer_end") or 0) - float(r.get("odometer_start") or 0)
    except Exception:
        distance = ""

    def build(story, styles):
        story.append(Paragraph("TRANSPORTATION SERVICE / VEHICLE UTILIZATION FORM", styles["Section"]))

        story.append(field_table([
            ["<b>Transport Ref. No.</b>", r.get("id"), "<b>Date Created</b>", r.get("created_at")],
            ["<b>Vehicle / Plate No.</b>", r.get("vehicle"), "<b>Driver</b>", r.get("driver")],
            ["<b>Requesting Office</b>", r.get("requesting_office"), "<b>Trip Date</b>", r.get("trip_date")],
            ["<b>Destination</b>", r.get("destination"), "<b>No. of Passengers</b>", r.get("passengers")],
            ["<b>Purpose</b>", r.get("purpose")],
            ["<b>Fuel Used / Issued in Liters</b>", r.get("fuel_liters"), "<b>Distance Travelled</b>", distance],
            ["<b>Odometer Start</b>", r.get("odometer_start"), "<b>Odometer End</b>", r.get("odometer_end")],
            ["<b>Status</b>", r.get("status"), "<b>Remarks</b>", r.get("remarks")],
        ], styles, widths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch]))

        story.append(Spacer(1, 5))
        story.append(signature_block([
            ("Requested / Confirmed by", r.get("requesting_office", "")),
            ("Driver", r.get("driver", "")),
            ("Checked and Reviewed by", "Transportation Unit Head"),
            ("Approved by", f"{DIRECTOR_NAME}, Director, General Services Office")
        ], styles))

    return make_pdf("TRANSPORTATION SERVICE / VEHICLE UTILIZATION FORM", r.get("id"), build)


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
    st.caption("Prototype v3 · Actual GSO Forms · AI Narrative")


st.markdown(f"""
<div class="gso-hero">
    <h1>{APP_TITLE}</h1>
    <p>Institutional request intake, AI-assisted classification, deployment, emergency response, completion reporting, transportation monitoring, and printable GSO forms.</p>
</div>
""", unsafe_allow_html=True)


if page == "Dashboard":
    req = read_table("requests")
    ready = read_table("ready_reports")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Requests", len(req))

    if not req.empty:
        c2.metric("Active", int(req[~req["status"].isin(["Completed", "Cancelled"])].shape[0]))
        c3.metric("Emergency", int((req["system_classification"] == "Emergency").sum()))
        c4.metric("Special Projects", int((req["system_classification"] == "Special Project").sum()))
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
            st.write("System Classification")
            st.bar_chart(req["system_classification"].value_counts())
        with col4:
            st.write("Priority")
            st.bar_chart(req["priority"].value_counts())

        st.dataframe(
            req[
                [
                    "id", "created_at", "requestor", "office", "unit",
                    "work_classification", "request_type",
                    "system_classification", "priority", "status", "building"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


elif page == "New Service Request":
    st.markdown('<h3 class="section-title">Digital Service Request Form / Work Order Intake</h3>', unsafe_allow_html=True)

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
        work_classification = st.selectbox("Requested Work Classification", WORK_CLASSIFICATIONS)
        request_type = st.multiselect("Scope / Type of Work", REQUEST_TYPES)

        c7, c8, c9 = st.columns(3)
        schedule_from = c7.date_input("Preferred Start Date", value=date.today())
        schedule_to = c8.date_input("Preferred End Date", value=date.today())
        working_hours = c9.text_input("Preferred Working Hours", placeholder="Example: 8:00 AM - 5:00 PM")

        access_condition = st.selectbox(
            "Site Coordination / Access Condition",
            [
                "GSO may access the area anytime using authorized keys; requestor to be notified when needed.",
                "Coordinate with requestor before entry due to sensitive documents, equipment, class, exam, or restricted activity.",
                "Area is open/common area and may be accessed during working hours.",
                "Work requires ingress / egress coordination.",
                "Work requires delivery / pull-out coordination.",
                "Work requires temporary utility shutdown coordination.",
                "Others / specify in description."
            ]
        )

        docs = st.multiselect(
            "Attached / Required Documents",
            [
                "Letter Request",
                "Pre-Inspection Report",
                "Service Request",
                "Program of Works / Cost Estimates",
                "Material Request / Supply Availability",
                "Technical Assessment Report",
                "Safety Permit for Hotworks / Elevated Works",
                "Photos",
                "Location Sketch",
                "Other Attachments"
            ]
        )

        purpose = st.text_area("Purpose of Request")
        description = st.text_area("Work Description / Nature of Concern", height=130)

        st.markdown("#### AI-Assisted Initial Triage")

        c10, c11, c12, c13 = st.columns(4)
        safety = c10.slider("Safety Risk", 1, 4, 1, help="1 Low, 4 Critical")
        affected = c11.slider("Users Affected", 1, 4, 1, help="1 Few, 4 Entire Building / Large Group")
        impact = c12.slider("Operational Impact", 1, 4, 1, help="1 Minor, 4 Severe")
        complexity = c13.slider("Complexity / Approval Requirement", 1, 4, 1, help="1 Simple, 4 Requires planning, budget, or executive approval")

        submitted = st.form_submit_button("Submit Request")

    if submitted:
        text = f"{work_classification} {' '.join(request_type)} {purpose} {description}"
        system_classification, priority, score, narrative, action, special_note = calc_ai_assessment(
            safety, affected, impact, complexity, text
        )

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
            "work_classification": work_classification,
            "request_type": ", ".join(request_type),
            "system_classification": system_classification,
            "priority": priority,
            "status": "Submitted",
            "purpose": purpose,
            "description": description,
            "schedule_from": str(schedule_from),
            "schedule_to": str(schedule_to),
            "working_hours": working_hours,
            "access_condition": access_condition,
            "docs": ", ".join(docs),
            "safety_risk": safety,
            "users_affected": affected,
            "operational_impact": impact,
            "complexity_level": complexity,
            "ai_score": score,
            "ai_narrative": narrative,
            "recommended_action": action,
            "special_project_note": special_note
        })

        st.success(f"Request submitted: {rid}")
        st.info(f"System Classification: {system_classification} | Priority: {priority} | AI Score: {score}")
        st.write(narrative)


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
        st.write(f"**Current System Classification:** {r['system_classification']}")
        st.write(f"**Current Priority:** {r['priority']}")

        with st.form("rapid"):
            c1, c2, c3, c4 = st.columns(4)

            safety = c1.slider("Safety Risk", 1, 4, int(r["safety_risk"] or 1))
            affected = c2.slider("Users Affected", 1, 4, int(r["users_affected"] or 1))
            impact = c3.slider("Operational Impact", 1, 4, int(r["operational_impact"] or 1))
            complexity = c4.slider("Complexity / Approval Requirement", 1, 4, int(r["complexity_level"] or 1))

            status = st.selectbox(
                "Next Status",
                ["For Approval", "Approved", "Assigned", "For VP / Executive Approval", "For Budget Review", "Deferred", "Cancelled"]
            )

            go = st.form_submit_button("Save RAPID Assessment")

        if go:
            text = f"{r['work_classification']} {r['request_type']} {r['purpose']} {r['description']}"
            system_classification, priority, score, narrative, action, special_note = calc_ai_assessment(
                safety, affected, impact, complexity, text
            )

            conn = get_conn()
            cur = conn.cursor()

            cur.execute("""
                UPDATE requests
                SET safety_risk=?, users_affected=?, operational_impact=?,
                    complexity_level=?, system_classification=?, priority=?,
                    ai_score=?, ai_narrative=?, recommended_action=?,
                    special_project_note=?, status=?, updated_at=?
                WHERE id=?
            """, (
                safety, affected, impact, complexity,
                system_classification, priority, score, narrative,
                action, special_note, status, now(), req_id
            ))

            conn.commit()
            conn.close()

            st.success(f"RAPID saved. Classification: {system_classification}; Priority: {priority}; AI Score: {score}")
            st.write(narrative)


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
                "Civil/Structural",
                "Electrical",
                "Plumbing",
                "Mechanical",
                "Grounds",
                "Safety Hazard",
                "Flooding",
                "Other"
            ]
        )
        priority = c5.selectbox("Priority Level", ["Critical", "High", "Moderate", "Low"])

        concern = st.text_area("Nature of Emergency Concern")
        hazard = st.radio("Immediate Hazard Present?", ["Yes", "No"], horizontal=True)
        hazard_desc = st.text_area("Hazard Description")
        affected_ops = st.text_area("Affected Occupants / Operations")
        area_secured = st.radio("Area Secured / Isolated?", ["Yes", "No"], horizontal=True)

        responding_team = st.text_input("GSO Responding Team")
        team_leader = st.text_input("Team Leader")
        initial = st.text_area("Initial Action Taken")
        temp = st.text_area("Temporary Corrective Measures")

        utilities = st.multiselect("Utilities Isolated", ["Power", "Water", "ICT", "None"])
        safe = st.radio("Area Declared Safe?", ["Yes", "No"], horizontal=True)
        further = st.radio("Further Repair Required?", ["Yes", "No"], horizontal=True)

        restoration_time = st.text_input("Estimated Restoration Time")
        actual_completion = st.text_input("Actual Completion Time")

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
            "responding_team": responding_team,
            "team_leader": team_leader,
            "initial_action": initial,
            "temporary_measures": temp,
            "utilities_isolated": ", ".join(utilities),
            "declared_safe": safe,
            "further_repair": further,
            "followup_wo": followup,
            "restoration_time": restoration_time,
            "actual_completion": actual_completion,
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
                "work_classification": "Emergency Repair",
                "request_type": category,
                "system_classification": "Emergency",
                "priority": priority_map[priority],
                "status": "Submitted",
                "purpose": "Follow-up work order from READY emergency report",
                "description": concern,
                "schedule_from": str(date.today()),
                "schedule_to": str(date.today()),
                "working_hours": "Immediate emergency response",
                "access_condition": "GSO may access the area anytime using authorized keys; requestor to be notified when needed.",
                "docs": "READY report",
                "safety_risk": 4 if priority == "Critical" else 3,
                "users_affected": 3,
                "operational_impact": 3,
                "complexity_level": 3,
                "ai_score": 150,
                "ai_narrative": "Auto-created from emergency READY report due to further repair requirement.",
                "recommended_action": "Immediate assessment and deployment.",
                "special_project_note": ""
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
            c1, c2, c3 = st.columns(3)
            completed = c1.date_input("Date Completed", value=date.today())
            actual = c2.text_input("Actual Completion Time / Duration")
            team_leader = c3.text_input("Team Leader")

            slippage = st.text_input("Slippage, if any")

            work = st.multiselect(
                "Work Performed",
                ["Repair", "Renovation", "Installation", "Maintenance", "Fabrication", "Emergency Response"]
            )

            tools = st.text_area("Tools Used")
            materials = st.text_area("Materials Used")
            personnel = st.text_area("Assigned Personnel")
            scope = st.text_area("Actual Scope of Works Performed")
            issues = st.text_area("Issues Encountered")

            c4, c5, c6 = st.columns(3)
            condition = c4.selectbox(
                "Final Condition",
                ["Fully Completed", "Partially Completed", "Deferred", "For Rework"]
            )

            site_status = c5.multiselect(
                "Site Status",
                ["Cleaned", "Safe", "Operational", "Turned Over"]
            )

            rating = c6.selectbox(
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
                "team_leader": team_leader,
                "slippage": slippage,
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

                    rapid_pdf = generate_rapid_pdf(selected)
                    st.download_button(
                        "Download RAPID Assessment PDF",
                        data=rapid_pdf,
                        file_name=f"{selected_id}_GSO_RAPID.pdf",
                        mime="application/pdf",
                        key=f"rapid_pdf_{selected_id}"
                    )

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

                else:
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
2. The system suggests whether the request is **Routine**, **Emergency**, or **Special Project**.
3. The concerned personnel validates the risk and priority through **RAPID Assessment**.
4. Approved work proceeds to **Workforce Deployment**.
5. Completed work is closed through **PRIME Completion Report**.
6. Emergency events are handled through **READY Emergency**.
7. Vehicle use is monitored through **Transportation Log**.
8. Printable institutional PDF forms are generated under **Records & Export**.

### Revised Site Access Logic

The requestor is no longer asked whether GSO can access the site, because GSO may already have authorized keys and operational access.  
Instead, the form asks for **Site Coordination / Access Condition** so the requestor can identify if the area has sensitive documents, classes, examinations, equipment, restricted activities, utility shutdown needs, delivery, ingress, egress, or pull-out concerns.

### Special Project Rule

A request may be classified as **Special Project** when it involves planned improvement, upgrading, development of facilities and services, equipment procurement, landscape development, facility upgrades, infrastructure works, or any activity requiring technical assessment, program of works, budget allocation, VP/executive approval, procurement, or programmed implementation.

### Removed Item

Estimated cost was removed from the requestor-side form because GSO work may be handled under MOOE or internal operating resources. Budget-related review is now handled through the **Special Project / Executive Approval** logic.
""")
