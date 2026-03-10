import streamlit as st
import base64
import os
import requests
import pandas as pd
from datetime import date, datetime
import google.generativeai as genai

# 1. PAGE SETUP
st.set_page_config(
    page_title="M-FLO | Clinical Workspace", 
    page_icon="⚕️", 
    layout="wide"
)

# 2. AI CONFIGURATION (SECURE)
try:
    # On Streamlit Cloud, add GEMINI_API_KEY to 'Settings > Secrets'
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # For local testing, replace with your actual key string
    API_KEY = "YOUR_API_KEY_HERE"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_actual_ai_insight(title, content):
    """Function to generate a real-time AI clinical insight"""
    try:
        prompt = f"""
        You are a senior medical AI consultant. 
        A colleague posted: "{title}"
        Content: "{content}"
        Provide a professional, clinical insight or a relevant research-based follow-up question. 
        Keep it under 50 words.
        """
        response = model.generate_content(prompt)
        return f"[🤖 AI ASSISTANT]: {response.text}"
    except Exception as e:
        return f"[🤖 AI ASSISTANT]: Analysis paused. Error: {str(e)}"

# 3. GLOBAL DATA & VARIABLES
user_name = "Dr. John Doe"
user_role = "Consultant Physician" 

GITHUB_RAW_URL = "https://raw.githubusercontent.com/your-username/your-repo/main/doctor_profile.jpg" 

DOCTOR_BIO = {
    "title": user_role,
    "specialty": "Internal Medicine & Diagnostics",
    "desc": """Dr. John Doe is a world-renowned specialist in structural heart disease with over 15 years of clinical excellence. 
    He pioneered the use of minimally invasive valve replacements at M-FLO General and currently serves as the Head of Cardiovascular Research.""",
    "certs": ["MD, Harvard Medical School", "Board Certified in Cardiovascular Disease", "FACC Fellowship", "European Society of Cardiology (ESC) Member"],
    "stats": [
        {"label": "Consultations", "value": "1,200+"},
        {"label": "Research Papers", "value": "84"},
        {"label": "Patient Rating", "value": "4.9/5"}
    ]
}

# ------------------------------
# DOCTOR CSV DATABASE
# ------------------------------

DOCTOR_DB_FILE = "doctors.csv"

def init_doctor_db():
    if not os.path.exists(DOCTOR_DB_FILE):

        df = pd.DataFrame([
            {
                "username": "doctor1",
                "password": "mediflow2026",
                "following": ""
            },
            {
                "username": "doctor2",
                "password": "password123",
                "following": ""
            }
        ])

        df.to_csv(DOCTOR_DB_FILE, index=False)


def load_doctors():
    return pd.read_csv(DOCTOR_DB_FILE)


def save_doctors(df):
    df.to_csv(DOCTOR_DB_FILE, index=False)


init_doctor_db()

# Initial Post Database
if "community_posts" not in st.session_state:
    st.session_state.community_posts = [
        {"user": "Dr. Phang Lee You", "role": "Senior Consultant Cardiologist", "title": "Hypertension resistance protocols", "content": "Recent studies suggest that double-blocking RAAS might be more effective in Stage 2 patients...", "likes": 42, "comments": ["Very insightful!", "What about ACEi side effects?"]},
        {"user": "Dr. Sarah Smith", "role": "Head of Radiology", "title": "M-FLO v2.1 Beta Feedback", "content": "The new UI is much cleaner. I love the heartbeat animation on the alerts.", "likes": 15, "comments": ["Agreed!", "Can we get a dark mode?"]},
        {"user": "Dr. Robert Chen", "role": "Internal Medicine Specialist", "title": "AI in Chest X-Rays", "content": "New algorithm for detecting small pleural effusions showing 98% accuracy.", "likes": 89, "comments": ["Is this FDA approved?"]}
    ]

# Notifications Database
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"type": "community", "text": "Dr. Sarah Smith has replied on your post in community", "time": "2 mins ago", "unread": True},
        {"type": "clinical", "text": "Patient James Wilson has completed their X-ray", "time": "15 mins ago", "unread": True},
        {"type": "clinical", "text": "Patient Maria Garcia has claimed their medications from pharmacy", "time": "1 hour ago", "unread": False},
        {"type": "clinical", "text": "Lab Results: Patient Robert Chen did their blood test", "time": "3 hours ago", "unread": False}
    ]

# Patient Database (Mock) - Updated with new schema
if "patient_db" not in st.session_state:
    st.session_state.patient_db = {
        "950101-10-5543": {"name": "Alice Tan", "dob": "1995-01-01", "age": 31, "height": 162.0, "weight": 55.0, "history": "Asthma", "last_visit": "2026-01-12"},
        "880520-14-6678": {"name": "Bob Smith", "dob": "1988-05-20", "age": 37, "height": 175.0, "weight": 82.0, "history": "Type 2 Diabetes", "last_visit": "2026-02-28"}
    }

if "following_list" not in st.session_state:
    st.session_state.following_list = set()

RESERVATIONS_DB = [
    {"Time": "09:00 AM", "Patient": "Alice Tan", "Status": "Confirmed"},
    {"Time": "11:30 AM", "Patient": "Bob Smith", "Status": "Pending"}
]

# 4. FILE ENCODING
def get_base64_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except: return ""
    return ""

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64("logo_medical.png")
doctor_b64 = get_base64_from_url(GITHUB_RAW_URL)
if not doctor_b64:
    doctor_b64 = get_base64("doctor_profile.jpg")

# 5. SESSION STATE
if "auth" not in st.session_state:
    st.session_state.auth = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Homepage"
if "show_alerts" not in st.session_state:
    st.session_state.show_alerts = False

if "urgent_patients" not in st.session_state:
    st.session_state.urgent_patients = [
        {"Room": "302", "Name": "James Wilson", "Issue": "Respiratory Distress / Low O2"},
        {"Room": "415", "Name": "Maria Garcia", "Issue": "Diabetic Ketoacidosis (DKA)"},
        {"Room": "209", "Name": "Robert Chen", "Issue": "Hypertensive Crisis (190/110)"}
    ]

if "daily_tasks" not in st.session_state:
    st.session_state.daily_tasks = {str(date.today()): []}
if "completed_counts" not in st.session_state:
    st.session_state.completed_counts = {}

# 6. CSS (STYLING)
st.markdown(f"""
    <style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes slideRight {{ from {{ opacity: 0; transform: translateX(-30px); }} to {{ opacity: 1; transform: translateX(0); }} }}
    @keyframes heartbeat {{ 0% {{ transform: scale(1); }} 15% {{ transform: scale(1.08); }} 30% {{ transform: scale(1); }} 45% {{ transform: scale(1.08); }} 100% {{ transform: scale(1); }} }}

    [data-testid="stForm"], .profile-card, .stat-box, .reddit-card {{ animation: fadeIn 0.8s ease-out forwards; }}
    .pulse-alert {{ animation: heartbeat 1.5s ease-in-out infinite; box-shadow: 0 0 15px rgba(229, 115, 115, 0.4); }}
    .todo-item, .alert-card {{ animation: slideRight 0.5s ease-out forwards; }}

    [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; color: #124D41 !important; }}
    [data-testid="stAppViewContainer"] {{ background: radial-gradient(circle at top right, #F9FFF9, #FDFDFD) !important; }}
    
    .reddit-card {{
        background: white; border: 1px solid #EDEFF1; border-radius: 10px; padding: 15px; margin-bottom: 12px;
        transition: border 0.2s ease;
    }}
    .reddit-card:hover {{ border-color: #93C572; }}
    .reddit-user {{ font-size: 13px; color: #124D41; font-weight: 700; }}
    .reddit-title {{ font-size: 18px; font-weight: 600; color: #1A1A1B; margin: 5px 0; }}
    .reddit-content {{ font-size: 14px; color: #1A1A1B; line-height: 1.5; margin-bottom: 10px; }}
    .reddit-meta {{ font-size: 13px; color: #878A8C; font-weight: 700; display: flex; gap: 15px; }}
    .comment-bubble {{ background: #F6F7F8; padding: 8px 12px; border-radius: 8px; margin-top: 5px; font-size: 13px; }}

    .stat-box {{ background: #F1F8E9; border-radius: 20px; padding: 20px; text-align: center; border: 1px solid #E1EDD8; height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: transform 0.3s ease; }}
    .stat-box:hover {{ transform: scale(1.05); }}
    .stat-val {{ font-size: 24px; font-weight: 800; color: #124D41; margin: 0; }}
    .stat-lbl {{ font-size: 12px; color: #666; text-transform: uppercase; margin: 0; }}
    .profile-card {{ background: white; padding: 40px; border-radius: 35px; border: 1px solid #E0E0E0; box-shadow: 0 15px 50px rgba(0,0,0,0.05); margin-top: 10px; }}
    .profile-img {{ width: 140px; height: 140px; border-radius: 30px; object-fit: cover; border: 4px solid #93C572; }}
    .cert-tag {{ background: #E8F5E9; color: #2E7D32; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 4px; display: inline-block; border: 1px solid #C8E6C9; }}
    .alert-card {{ background: #FFF5F5; border-left: 5px solid #E57373; padding: 15px; border-radius: 12px; margin-bottom: 10px; }}
    .todo-item {{ background:#F1F8E9; padding:12px; border-radius:12px; border-left:5px solid #93C572; margin-bottom:10px; }}

    .notif-card {{
        background: white; border-radius: 12px; padding: 15px; margin-bottom: 10px;
        border-left: 5px solid #E0E0E0; display: flex; align-items: center; gap: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.2s ease;
    }}
    .notif-card:hover {{ transform: translateX(5px); }}
    .notif-unread {{ border-left-color: #93C572 !important; background: #F9FFF9; }}
    .notif-icon {{ font-size: 20px; }}
    .notif-text {{ flex-grow: 1; font-size: 14px; color: #333; }}
    .notif-time {{ font-size: 11px; color: #888; }}
    
    .ai-comment {{ border-left: 4px solid #2196F3 !important; background: #E3F2FD !important; color: #0D47A1 !important; }}
    </style>
    """, unsafe_allow_html=True)

# 7. APP FLOW
if not st.session_state.auth:
    with st.form("login_form", clear_on_submit=False):
        if logo_b64:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" style="width:110px; margin-bottom:15px;"></div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#93C572; font-weight:800; font-size:20px; text-align:center;">67+2 PODCAST</p>', unsafe_allow_html=True)
        st.markdown('<h1 style="color:#124D41; font-size:55px; font-weight:900; text-align:center; margin:0; letter-spacing:-3px;">M-FLO</h1>', unsafe_allow_html=True)
        u = st.text_input("ID", placeholder="Enter ID", label_visibility="collapsed")
        p = st.text_input("Key", type="password", placeholder="Security Key", label_visibility="collapsed")
        if st.form_submit_button("AUTHENTICATE SYSTEM"):
            if u == "doctor1" and p == "mediflow2026":
                st.session_state.auth = True; st.rerun()
else:
    today_str = date.today().strftime("%Y-%m-%d")
    current_tasks = st.session_state.daily_tasks.get(today_str, [])
    count_patients = sum(1 for task in current_tasks if any(x in task.lower() for x in ["patient", "consult"]))
    count_followups = sum(1 for task in current_tasks if any(x in task.lower() for x in ["follow", "review"]))

    with st.sidebar:
        if logo_b64: st.image(f"data:image/png;base64,{logo_b64}", use_container_width=True)
        st.divider()
        if st.button("🏠 Homepage", key="nav_h", use_container_width=True): st.session_state.current_page = "Homepage"
        if st.button("👥 Patient Search", key="nav_p", use_container_width=True): st.session_state.current_page = "Patient"
        if st.button("📅 Reservation", key="nav_r", use_container_width=True): st.session_state.current_page = "Reservation"
        
        unread_count = sum(1 for n in st.session_state.notifications if n['unread'])
        btn_label = f"🔔 Notifications ({unread_count})" if unread_count > 0 else "🔔 Notifications"
        if st.button(btn_label, key="nav_n", use_container_width=True): st.session_state.current_page = "Notifications"
        if st.button("🤝 Community", key="nav_c", use_container_width=True): st.session_state.current_page = "Community"
        
        if st.session_state.following_list:
            st.divider()
            st.markdown("👨‍⚕️ **Following**")
            for doc in st.session_state.following_list:
                st.markdown(f"• <small>{doc}</small>", unsafe_allow_html=True)
        
        st.divider()
        if st.button("🚪 Logout", key="nav_l", use_container_width=True): st.session_state.auth = False; st.rerun()

    # --- PAGE: HOMEPAGE ---
    if st.session_state.current_page == "Homepage":
        st.markdown(f'<p style="color:#124D41; font-weight:700; font-size:18px;">Hello, {user_name} 👋</p>', unsafe_allow_html=True)
        
        with st.expander("🛠️ Clinical Simulation Tools"):
            if st.button("📥 Simulate Incoming Lab Results"):
                new_notif = {
                    "type": "clinical", 
                    "text": "New Lab Results: Patient Alice Tan (Hematology Panel)", 
                    "time": "Just now", 
                    "unread": True
                }
                st.session_state.notifications.insert(0, new_notif)
                st.success("New Lab Result notification pushed!")
                st.rerun()

        s1, s2, s3, s4 = st.columns(4)
        with s1: st.markdown(f'<div class="stat-box"><p class="stat-lbl">Consultations</p><p class="stat-val">{count_patients:02d}</p></div>', unsafe_allow_html=True)
        with s2: st.markdown(f'<div class="stat-box"><p class="stat-lbl">Follow-ups</p><p class="stat-val">{count_followups:02d}</p></div>', unsafe_allow_html=True)
        with s3:
            alert_count = len(st.session_state.urgent_patients)
            color = "#E57373" if alert_count > 0 else "#93C572"
            pulse_class = "pulse-alert" if alert_count > 0 else ""
            st.markdown(f'<div class="stat-box {pulse_class}" style="border-color:{color};"><p class="stat-lbl">Urgent Alerts</p><p class="stat-val" style="color:{color};">{alert_count:02d}</p></div>', unsafe_allow_html=True)
            if st.button("Manage Alerts", key="manage_alerts", use_container_width=True):
                st.session_state.show_alerts = not st.session_state.show_alerts; st.rerun()
        with s4: st.markdown('<div class="stat-box"><p class="stat-lbl">Clinic Health</p><p class="stat-val">98%</p></div>', unsafe_allow_html=True)
        
        if st.session_state.show_alerts:
            st.markdown("#### 🚨 Active Urgent Cases")
            for idx, p_alert in enumerate(st.session_state.urgent_patients):
                ac1, ac2 = st.columns([4, 1])
                with ac1: st.markdown(f'<div class="alert-card"><strong>Room {p_alert["Room"]}</strong>: {p_alert["Name"]} | <small>{p_alert["Issue"]}</small></div>', unsafe_allow_html=True)
                with ac2: 
                    if st.button("Resolve ✅", key=f"res_{idx}", use_container_width=True):
                        st.session_state.urgent_patients.pop(idx); st.rerun()
            st.divider()

        col_main, col_plan = st.columns([2.2, 1], gap="large")
        with col_main:
            img_html = f'<img src="data:image/png;base64,{doctor_b64}" class="profile-img">' if doctor_b64 else '👨‍⚕️'
            stats_html = "".join([f'<div class="mini-stat"><span class="mini-stat-val">{s["value"]}</span><span class="mini-stat-lbl">{s["label"]}</span></div>' for s in DOCTOR_BIO['stats']])
            certs_html = "".join([f'<span class="cert-tag">{c}</span>' for c in DOCTOR_BIO['certs']])
            st.markdown(f"""
                <div class="profile-card">
                    <div style="display:flex; align-items:flex-start; gap:35px;">{img_html}
                        <div style="flex-grow:1;">
                            <h1 style="margin:0; color:#124D41; font-size:32px;">{user_name}</h1>
                            <p style="color:#93C572; font-weight:700; margin-bottom:15px; font-size:18px;">{DOCTOR_BIO['title']}</p>
                            <div style="display:flex; gap:30px; border-top: 1px solid #f0f0f0; border-bottom: 1px solid #f0f0f0; padding: 15px 0; margin-bottom:15px;">{stats_html}</div>
                            <p style="color:#555; line-height:1.6; font-size:15px; margin-bottom:20px;">{DOCTOR_BIO['desc']}</p>
                            <h5 style="color:#124D41; margin-bottom:10px;">Board Certifications & Memberships</h5>
                            <div style="margin-left:-4px;">{certs_html}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_plan:
            st.markdown("### 📅 Calendar")
            selected_date = str(st.date_input("Schedule", label_visibility="collapsed"))
            if selected_date not in st.session_state.daily_tasks: st.session_state.daily_tasks[selected_date] = []
            if selected_date not in st.session_state.completed_counts: st.session_state.completed_counts[selected_date] = 0
            st.divider()
            st.markdown(f"### 📝 Planning: {selected_date}")
            new_task = st.text_input("Add task", key=f"input_{selected_date}")
            if st.button("Add", key=f"btn_{selected_date}"):
                if new_task: st.session_state.daily_tasks[selected_date].append(new_task); st.rerun()
            curr_tasks = st.session_state.daily_tasks[selected_date]
            comp_count = st.session_state.completed_counts[selected_date]
            total = len(curr_tasks) + comp_count
            st.progress(comp_count / total if total > 0 else 0)
            for i, task in enumerate(curr_tasks):
                c1, c2 = st.columns([5, 1])
                with c1: st.markdown(f'<div class="todo-item">{task}</div>', unsafe_allow_html=True)
                with c2:
                    if st.button("✔️", key=f"d_{selected_date}_{i}"):
                        st.session_state.daily_tasks[selected_date].pop(i)
                        st.session_state.completed_counts[selected_date] += 1; st.rerun()

    # --- PAGE: PATIENT SEARCH ---
    elif st.session_state.current_page == "Patient":
        st.title("👥 Patient Clinical Records")
        st.markdown("Search the hospital database to begin a new consultation session.")
        
        # Adding columns for search layout
        ps_col1, ps_col2 = st.columns([3, 1])
        with ps_col1:
            ic_input = st.text_input("🔍 Enter Patient IC Number", placeholder="XXXXXX-XX-XXXX")
        with ps_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear Search", use_container_width=True):
                st.rerun()

        if ic_input:
            if ic_input in st.session_state.patient_db:
                p_data = st.session_state.patient_db[ic_input]
                st.success(f"✅ Record Found for {p_data['name']}")
                
                # --- UPDATED: Vitals & BMI Calculation ---
                h_m = p_data.get('height', 0) / 100
                w_kg = p_data.get('weight', 0)
                bmi = round(w_kg / (h_m**2), 1) if h_m > 0 else 0
                
                c_data1, c_data2 = st.columns([1, 2])
                with c_data1:
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:15px; border:1px solid #E0E0E0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <h4 style="color:#124D41; margin-top:0;">Patient Info</h4>
                        <p><strong>Name:</strong> {p_data['name']}<br>
                        <strong>Age:</strong> {p_data['age']} yrs<br>
                        <strong>DOB:</strong> {p_data.get('dob', 'N/A')}<br>
                        <strong>IC:</strong> {ic_input}</p>
                        <hr>
                        <p style="margin-bottom:5px;"><strong>Vitals & Physical:</strong></p>
                        <div style="display:flex; justify-content:space-between; background:#F1F8E9; padding:10px; border-radius:10px; font-size:13px;">
                            <span>H: <b>{p_data.get('height', '--')} cm</b></span>
                            <span>W: <b>{p_data.get('weight', '--')} kg</b></span>
                            <span style="color:#2E7D32;">BMI: <b>{bmi}</b></span>
                        </div>
                        <hr>
                        <p><strong>Medical History:</strong><br><small>{p_data['history']}</small></p>
                        <p><strong>Last Visit:</strong> {p_data.get('last_visit', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with c_data2:
                    st.subheader("Consultation Notes")
                    consult_text = st.text_area("Observations, Symptoms & Plan", height=200)
                    if st.button("Save & Sync to Server"):
                        if consult_text:
                            st.session_state.patient_db[ic_input]['last_visit'] = str(date.today())
                            st.balloons()
                            st.success("Clinical notes have been encrypted and saved to the patient's record.")
                        else:
                            st.warning("Please enter notes before saving.")
            
            else:
                st.error("❌ No record found for this IC. Please register the new patient below.")
                
                # --- UPDATED: Registration Form with Auto-Age & Birthdate ---
                with st.form("registration_form"):
                    st.subheader("New Patient Registration")
                    reg_name = st.text_input("Full Name (as per IC)")
                    
                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        reg_dob = st.date_input("Birthdate", min_value=date(1900, 1, 1), max_value=date.today(), value=date(2000, 1, 1))
                        # Logic: Age calculation
                        today = date.today()
                        calc_age = today.year - reg_dob.year - ((today.month, today.day) < (reg_dob.month, reg_dob.day))
                        st.caption(f"System will record age as: {calc_age}")
                        
                    with r_col2:
                        reg_gender = st.selectbox("Gender", ["Male", "Female", "Other"])

                    r_col3, r_col4 = st.columns(2)
                    with r_col3:
                        reg_height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0, step=0.1)
                    with r_col4:
                        reg_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)

                    reg_history = st.text_area("Known Allergies & Medical History")
                    
                    if st.form_submit_button("Create Patient Record"):
                        if reg_name:
                            st.session_state.patient_db[ic_input] = {
                                "name": reg_name, 
                                "dob": str(reg_dob),
                                "age": calc_age, 
                                "height": reg_height,
                                "weight": reg_weight,
                                "history": reg_history, 
                                "last_visit": "Registered Today"
                            }
                            st.success(f"Account for {reg_name} created successfully! Re-enter IC to begin consultation.")
                            st.rerun()

    # --- PAGE: NOTIFICATIONS ---
    elif st.session_state.current_page == "Notifications":
        st.title("🔔 Notifications")
        n_col1, n_col2 = st.columns([1.5, 4])
        with n_col1:
            if st.button("✔️ Mark All as Read", use_container_width=True):
                for n in st.session_state.notifications: n['unread'] = False
                st.rerun()
        with n_col2:
            if st.button("🗑️ Clear Read Notifications", use_container_width=True):
                st.session_state.notifications = [n for n in st.session_state.notifications if not (n['unread'] == False)]
                st.rerun()
        st.divider()
        for idx, n in enumerate(st.session_state.notifications):
            unread_class = "notif-unread" if n['unread'] else ""
            icon = "💬" if n['type'] == "community" else "🩺"
            st.markdown(f"""
                <div class="notif-card {unread_class}">
                    <div class="notif-icon">{icon}</div>
                    <div class="notif-text">{n['text']}</div>
                    <div class="notif-time">{n['time']}</div>
                </div>
            """, unsafe_allow_html=True)
            if n['unread']:
                if st.button(f"Mark as read", key=f"read_{idx}"):
                    n['unread'] = False; st.rerun()

    # --- PAGE: COMMUNITY ---
    elif st.session_state.current_page == "Community":
        st.title("🤝 Medical Community")
        c_left, c_right = st.columns([2.5, 1], gap="large")
        with c_left:
            search_query = st.text_input("🔍 Search medical discussions...", placeholder="e.g. Hypertension, UI, AI")
            
            with st.expander("➕ Create New Post"):
                new_title = st.text_input("Title")
                new_content = st.text_area("What's on your mind, Doctor?")
                if st.button("Post to Community"):
                    if new_title and new_content:
                        with st.spinner("AI is analyzing post content..."):
                            ai_comment = get_actual_ai_insight(new_title, new_content)
                        
                        new_post = {
                            "user": user_name, 
                            "role": user_role, 
                            "title": new_title, 
                            "content": new_content, 
                            "likes": 0, 
                            "comments": [ai_comment]
                        }
                        st.session_state.community_posts.insert(0, new_post)
                        st.success("Post published! AI Assistant has analyzed the content.")
                        st.rerun()

            filtered_posts = [p for p in st.session_state.community_posts if search_query.lower() in p['title'].lower() or search_query.lower() in p['content'].lower()]
            for idx, post in enumerate(filtered_posts):
                st.markdown(f"""
                    <div class="reddit-card">
                        <div class="reddit-user">{post['user']} ({post.get('role', 'Fellow')}) • Posted by Colleague</div>
                        <div class="reddit-title">{post['title']}</div>
                        <div class="reddit-content">{post['content']}</div>
                        <div class="reddit-meta">
                            <span>⬆️ {post['likes']} Engagement</span>
                            <span>💬 {len(post['comments'])} Comments</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                b1, b2, b3, b4 = st.columns([1, 2, 1, 1])
                with b1:
                    if st.button(f"Push ⬆️", key=f"like_{idx}"):
                        post['likes'] += 1; st.rerun()
                with b2:
                    with st.expander(f"View {len(post['comments'])} Comments"):
                        for c in post['comments']:
                            ai_style = 'class="comment-bubble ai-comment"' if "[🤖 AI ASSISTANT]" in c else 'class="comment-bubble"'
                            st.markdown(f'<div {ai_style}>{c}</div>', unsafe_allow_html=True)
                        
                        new_com = st.text_input("Add comment...", key=f"com_in_{idx}", label_visibility="collapsed")
                        if st.button("Post", key=f"com_btn_{idx}"):
                            if new_com: 
                                post['comments'].append(f"{user_name}: {new_com}")
                                st.rerun()

                if post['user'] == user_name:
                    with b3:
                        if st.button("Edit 📝", key=f"edit_btn_{idx}"):
                            st.session_state[f"editing_{idx}"] = True
                    with b4:
                        if st.button("Delete 🗑️", key=f"del_btn_{idx}"):
                            st.session_state[f"confirm_del_{idx}"] = True
                    
                    if st.session_state.get(f"confirm_del_{idx}", False):
                        st.warning("⚠️ Are you sure you want to delete this post?")
                        col_y, col_n = st.columns([1, 4])
                        with col_y:
                            if st.button("Yes", key=f"conf_y_{idx}"):
                                st.session_state.community_posts.remove(post)
                                del st.session_state[f"confirm_del_{idx}"]; st.rerun()
                        with col_n:
                            if st.button("Cancel", key=f"conf_n_{idx}"):
                                del st.session_state[f"confirm_del_{idx}"]; st.rerun()

                    if st.session_state.get(f"editing_{idx}", False):
                        with st.form(f"edit_form_{idx}"):
                            edit_title = st.text_input("New Title", value=post['title'])
                            edit_content = st.text_area("New Content", value=post['content'])
                            if st.form_submit_button("Update Post"):
                                post['title'], post['content'] = edit_title, edit_content
                                st.session_state[f"editing_{idx}"] = False; st.rerun()

        with c_right:
            st.markdown("### 🔥 Trending Topics")
            trending = ["#Cardiology2026", "#AI_Diagnostics", "#MFLO_Updates"]
            for tag in trending: st.button(tag, use_container_width=True)
            st.divider()
            
            st.markdown("### 🏆 Top Contributors")
            contributors = [
                {"name": "Dr. Phang Lee You", "role": "Senior Consultant Cardiologist", "karma": "2.4k", "bio": "Expert in Percutaneous Coronary Intervention (PCI)."},
                {"name": "Dr. Sarah Smith", "role": "Head of Radiology", "karma": "1.8k", "bio": "Specializes in neuroimaging and AI-driven screening."},
                {"name": "Dr. Robert Chen", "role": "Internal Medicine Specialist", "karma": "950", "bio": "Focuses on geriatric chronic care and diabetes management."}
            ]
            
            for i, person in enumerate(contributors):
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #EDEFF1; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                        <div style="font-weight: 700; color: #124D41; font-size: 14px;">{person['name']}</div>
                        <div style="font-size: 12px; color: #787C7E; font-style: italic; margin-bottom: 4px;">{person['role']}</div>
                        <div style="font-size: 11px; color: #93C572; font-weight: 800;">{person['karma']} Karma Points</div>
                    </div>
                """, unsafe_allow_html=True)
                
                fb1, fb2 = st.columns(2)
                with fb1:
                    if st.button(f"Profile", key=f"p_btn_{i}", use_container_width=True):
                        st.info(f"**Bio:** {person['bio']}")
                with fb2:
                    is_following = person['name'] in st.session_state.following_list
                    btn_label = "Unfollow" if is_following else "Follow +"
                    if st.button(btn_label, key=f"f_btn_{i}", use_container_width=True):
                        if is_following:
                            st.session_state.following_list.remove(person['name'])
                        else:
                            st.session_state.following_list.add(person['name'])
                        st.rerun()

    # --- PAGE: RESERVATION ---
    elif st.session_state.current_page == "Reservation": 
        st.title("📅 Reservations")
        
        # Creating a more structured column-based view for reservations
        r_head1, r_head2, r_head3 = st.columns([1, 2, 1])
        with r_head1: st.markdown("**Time Slot**")
        with r_head2: st.markdown("**Patient Name**")
        with r_head3: st.markdown("**Booking Status**")
        st.divider()

        for res in RESERVATIONS_DB:
            r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
            with r_col1:
                st.write(res["Time"])
            with r_col2:
                st.write(res["Patient"])
            with r_col3:
                status_color = "#2E7D32" if res["Status"] == "Confirmed" else "#EF6C00"
                st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{res['Status']}</span>", unsafe_allow_html=True)
