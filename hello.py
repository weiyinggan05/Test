import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

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
# SESSION
# -------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "Homepage"

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

    # Homepage
    if page == "Homepage":

        st.title("Doctor Dashboard")

        st.metric("Patients Today", "18")
        st.metric("Completed Tasks", "7")
        st.metric("Pending Alerts", "3")

        st.write("Welcome to M-FLO Clinical Workspace.")

    # Tasks
    elif page == "Tasks":

        st.title("Daily Tasks")

        if "tasks" not in st.session_state:
            st.session_state.tasks = []

        task = st.text_input("Add new task")

        if st.button("Add Task") and task:
            st.session_state.tasks.append(task)

        for t in st.session_state.tasks:
            st.write("•",t)

    # Reservations
    elif page == "Reservations":

    st.title("Patient Reservations")

    # 初始化 reservation list
    if "reservations" not in st.session_state:
        st.session_state.reservations = [
            {"Time":"09:00","Patient":"Alice Tan","Status":"Confirmed"},
            {"Time":"11:30","Patient":"Bob Smith","Status":"Pending"}
        ]

    # Add reservation button
    if st.button("➕ Add Reservation"):
        st.session_state.show_form = True

    # Form
    if st.session_state.get("show_form", False):

        with st.form("reservation_form"):

            patient = st.text_input("Patient Name")

            time = st.text_input("Time (example: 14:30)")

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

    # Show table
    df = pd.DataFrame(st.session_state.reservations)

    st.dataframe(df, use_container_width=True)

    # Alerts
    elif page == "Alerts":

        st.title("Urgent Alerts")

        alerts = [
            {"Room":"302","Patient":"James Wilson","Issue":"Low Oxygen"},
            {"Room":"415","Patient":"Maria Garcia","Issue":"DKA"},
            {"Room":"209","Patient":"Robert Chen","Issue":"High BP"}
        ]

        df = pd.DataFrame(alerts)

        st.dataframe(df,use_container_width=True)

    # Community
    elif page == "Community":

        st.title("Doctor Community")

        if "posts" not in st.session_state:
            st.session_state.posts = []

        new_post = st.text_area("Share medical insight")

        if st.button("Post") and new_post:
            st.session_state.posts.append(new_post)

        for p in st.session_state.posts[::-1]:
            st.write("🩺",p)


# -------------------------
# ADMIN SYSTEM
# -------------------------
if st.session_state.auth and st.session_state.role == "admin":

    st.title("Admin Doctor Database")

    st.write("Admin can create doctor accounts but cannot change passwords.")

    # show doctors
    df = pd.read_sql("SELECT username FROM doctors",conn)

    st.subheader("Doctor Accounts")

    st.dataframe(df,use_container_width=True)

    # add doctor
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
