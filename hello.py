import streamlit as st
import sqlite3
import pandas as pd

# -------------------------
# DATABASE
# -------------------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

conn.commit()

# default users
cursor.execute("SELECT COUNT(*) FROM doctors")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO doctors (username,password) VALUES (?,?)",
        ("doctor22","mediflow2026")
    )

cursor.execute("SELECT COUNT(*) FROM admins")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO admins (username,password) VALUES (?,?)",
        ("admin01","hospital2026")
    )

conn.commit()

# -------------------------
# DOCTOR PROFILE DATA
# -------------------------
DOCTOR_PROFILE = {
    "name": "Dr. John Doe",
    "specialty": "Consultant Physician",

    "description": """
Dr. John Doe is a consultant physician specializing in internal medicine 
with over 12 years of clinical experience in diagnostics and patient care.
""",

    "education": [
        "MD – Harvard Medical School",
        "Bachelor of Medicine – University of Oxford",
        "Board Certified Internal Medicine"
    ],

    "stats": {
        "Patients Treated": "1200+",
        "Research Papers": "34",
        "Rating": "⭐ 4.9"
    },

    "photo": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d"
}

# -------------------------
# SESSION
# -------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if "role" not in st.session_state:
    st.session_state.role = None

if "show_form" not in st.session_state:
    st.session_state.show_form = False

# -------------------------
# CSS FOR LAYERS
# -------------------------
st.markdown("""
<style>

.layer1{
background:#E8F5E9;
padding:25px;
border-radius:15px;
margin-bottom:20px;
}

.layer2{
background:#E3F2FD;
padding:25px;
border-radius:15px;
margin-bottom:20px;
}

.layer3{
background:#FFF3E0;
padding:25px;
border-radius:15px;
margin-bottom:20px;
}

.badge{
background:#4CAF50;
color:white;
padding:6px 12px;
border-radius:20px;
margin-right:6px;
font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.auth:

    st.title("⚕️ M-FLO Clinical System")

    with st.form("login"):

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login = st.form_submit_button("Login")

        if login:

            if username.startswith("doctor"):

                cursor.execute(
                    "SELECT * FROM doctors WHERE username=? AND password=?",
                    (username,password)
                )

                if cursor.fetchone():
                    st.session_state.auth = True
                    st.session_state.role = "doctor"
                    st.rerun()
                else:
                    st.error("Invalid doctor login")

            elif username.startswith("admin"):

                cursor.execute(
                    "SELECT * FROM admins WHERE username=? AND password=?",
                    (username,password)
                )

                if cursor.fetchone():
                    st.session_state.auth = True
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Invalid admin login")

            else:
                st.error("Username must start with doctor or admin")

# -------------------------
# DOCTOR SYSTEM
# -------------------------
if st.session_state.auth and st.session_state.role == "doctor":

    st.sidebar.title("M-FLO Navigation")

    page = st.sidebar.radio(
        "Menu",
        ["Homepage","Tasks","Reservations","Alerts","Community"]
    )

    # -------------------------
    # HOMEPAGE PROFILE
    # -------------------------
    if page == "Homepage":

        st.title("Doctor Profile")

        # Layer 1
        st.markdown('<div class="layer1">', unsafe_allow_html=True)

        col1, col2 = st.columns([1,3])

        with col1:
            st.image(DOCTOR_PROFILE["photo"], width=180)

        with col2:
            st.subheader(DOCTOR_PROFILE["name"])
            st.write(DOCTOR_PROFILE["specialty"])

            st.markdown("### Description")
            st.write(DOCTOR_PROFILE["description"])

        st.markdown('</div>', unsafe_allow_html=True)

        # Layer 2
        st.markdown('<div class="layer2">', unsafe_allow_html=True)

        st.markdown("### 🎓 Educational Background")

        for edu in DOCTOR_PROFILE["education"]:
            st.write("•", edu)

        st.markdown('</div>', unsafe_allow_html=True)

        # Layer 3
        st.markdown('<div class="layer3">', unsafe_allow_html=True)

        st.markdown("### 🏆 Research & Experience")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Research Papers", DOCTOR_PROFILE["stats"]["Research Papers"])
            st.metric("Patients Treated", DOCTOR_PROFILE["stats"]["Patients Treated"])

        with col2:
            st.metric("Experience", "12 Years")
            st.metric("Rating", DOCTOR_PROFILE["stats"]["Rating"])

        st.markdown("### Badges")

        st.markdown("""
<span class="badge">Top Physician</span>
<span class="badge">Research Leader</span>
<span class="badge">Cardiology Expert</span>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # TASKS
    # -------------------------
    elif page == "Tasks":

        st.title("Daily Tasks")

        if "tasks" not in st.session_state:
            st.session_state.tasks = []

        task = st.text_input("Add new task")

        if st.button("Add Task") and task:
            st.session_state.tasks.append(task)

        for t in st.session_state.tasks:
            st.write("•", t)

    # -------------------------
    # RESERVATIONS
    # -------------------------
    elif page == "Reservations":

        st.title("Patient Reservations")

        if "reservations" not in st.session_state:
            st.session_state.reservations = [
                {"Time":"09:00","Patient":"Alice Tan","Status":"Confirmed"},
                {"Time":"11:30","Patient":"Bob Smith","Status":"Pending"}
            ]

        if st.button("➕ Add Reservation"):
            st.session_state.show_form = True

        if st.session_state.show_form:

            with st.form("reservation_form"):

                patient = st.text_input("Patient Name")
                time = st.text_input("Time")
                status = st.selectbox(
                    "Status",
                    ["Confirmed","Pending","Cancelled"]
                )

                submit = st.form_submit_button("Create Reservation")

                if submit:

                    new_reservation = {
                        "Time": time,
                        "Patient": patient,
                        "Status": status
                    }

                    st.session_state.reservations.append(new_reservation)
                    st.session_state.show_form = False

                    st.success("Reservation added")

        df = pd.DataFrame(st.session_state.reservations)
        st.dataframe(df, use_container_width=True)

    # -------------------------
    # ALERTS
    # -------------------------
    elif page == "Alerts":

        st.title("Urgent Alerts")

        alerts = [
            {"Room":"302","Patient":"James Wilson","Issue":"Low Oxygen"},
            {"Room":"415","Patient":"Maria Garcia","Issue":"DKA"},
            {"Room":"209","Patient":"Robert Chen","Issue":"High BP"}
        ]

        df = pd.DataFrame(alerts)
        st.dataframe(df,use_container_width=True)

    # -------------------------
    # COMMUNITY
    # -------------------------
    elif page == "Community":

        st.title("Doctor Community")

        if "posts" not in st.session_state:
            st.session_state.posts = []

        new_post = st.text_area("Share medical insight")

        if st.button("Post") and new_post:
            st.session_state.posts.append(new_post)

        for p in st.session_state.posts[::-1]:
            st.write("🩺", p)

# -------------------------
# ADMIN SYSTEM
# -------------------------
if st.session_state.auth and st.session_state.role == "admin":

    st.title("Admin Doctor Database")

    st.write("Admin can create doctor accounts but cannot change passwords.")

    df = pd.read_sql("SELECT username FROM doctors",conn)

    st.subheader("Doctor Accounts")
    st.dataframe(df,use_container_width=True)

    st.subheader("Create Doctor Account")

    new_user = st.text_input("Doctor Username")
    new_pw = st.text_input("Initial Password")

    if st.button("Create Doctor"):

        try:
            cursor.execute(
                "INSERT INTO doctors (username,password) VALUES (?,?)",
                (new_user,new_pw)
            )

            conn.commit()

            st.success("Doctor created")

        except:
            st.error("Username already exists")
