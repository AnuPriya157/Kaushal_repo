# =========================================================
# IMPORT LIBRARIES
# =========================================================
import streamlit as st
import pandas as pd
import joblib
import sqlite3
import os
import matplotlib.pyplot as plt
import base64

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "username" not in st.session_state:
    st.session_state.username = ""

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "grade" not in st.session_state:
    st.session_state.grade = None

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect(
    "students.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    username TEXT PRIMARY KEY,
    name TEXT,
    password TEXT,
    dob TEXT,
    age INTEGER,
    gender TEXT,
    class TEXT,
    school TEXT,
    photo TEXT
)
""")

conn.commit()

# =========================================================
# AUTO LOGIN
# =========================================================
if os.path.exists("current_user.txt"):

    with open("current_user.txt", "r") as f:

        saved_user = f.read().strip()

        if saved_user and not st.session_state.logged_in:

            st.session_state.logged_in = True
            st.session_state.username = saved_user

            if st.session_state.page == "Home":
                st.session_state.page = "App"

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* MAIN APP */

.stApp {
    background: #F5F7FB;
}

/* REMOVE SPACE */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #243BDE 0%,
        #1D4ED8 40%,
        #0F2EA6 100%
    );

    border-top-right-radius: 25px;
    border-bottom-right-radius: 25px;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* PROFILE */

.profile-pic {

    width: 120px;
    height: 120px;

    border-radius: 50%;

    object-fit: cover;

    border: 5px solid rgba(255,255,255,0.2);

    margin-bottom: 15px;
}

/* TITLE */

.dashboard-title {

    font-size: 52px;

    font-weight: 700;

    color: #111827;

    margin-bottom: 5px;
}

.dashboard-subtitle {

    color: #6B7280;

    font-size: 18px;

    margin-bottom: 35px;
}

/* SCORE CARD */

.main-score-card {

    background: linear-gradient(
        135deg,
        #315CFD 0%,
        #1E88E5 100%
    );

    border-radius: 30px;

    padding: 45px;

    color: white;

    box-shadow:
        0px 10px 30px rgba(37,99,235,0.25);
}

.main-score-title {

    font-size: 34px;

    font-weight: 600;

    margin-bottom: 30px;
}

.main-score {

    font-size: 120px;

    font-weight: 700;

    line-height: 1;
}

.score-total {

    font-size: 40px;

    font-weight: 500;
}

.progress-container {

    margin-top: 30px;

    background: rgba(255,255,255,0.18);

    border-radius: 20px;

    overflow: hidden;

    height: 16px;
}

.progress-fill {

    height: 100%;

    background: white;

    border-radius: 20px;
}

/* INSIGHT BOX */

.insight-box {

    margin-top: 30px;

    background: rgba(0,0,0,0.12);

    padding: 20px;

    border-radius: 18px;

    font-size: 18px;
}

/* SMALL CARDS */

.small-card {

    background: white;

    border-radius: 28px;

    padding: 35px;

    text-align: center;

    min-height: 320px;

    box-shadow:
        0px 5px 20px rgba(0,0,0,0.05);
}

.small-title {

    font-size: 28px;

    font-weight: 600;

    color: #111827;

    margin-bottom: 30px;
}

.grade-circle {

    width: 140px;
    height: 140px;

    margin: auto;

    border-radius: 50%;

    background: linear-gradient(
        135deg,
        #22C55E,
        #16A34A
    );

    display: flex;
    align-items: center;
    justify-content: center;

    color: white;

    font-size: 75px;
    font-weight: 700;

    margin-bottom: 20px;
}

.performance-pill {

    display: inline-block;

    background: #E8F5E9;

    color: #16A34A;

    padding: 10px 25px;

    border-radius: 20px;

    font-size: 16px;

    font-weight: 500;
}

/* SECTION CARD */

.section-card {

    background: white;

    border-radius: 28px;

    padding: 30px;

    margin-top: 25px;

    box-shadow:
        0px 5px 20px rgba(0,0,0,0.05);
}

.section-title {

    font-size: 32px;

    font-weight: 600;

    color: #111827;

    margin-bottom: 25px;
}

/* BUTTONS */

div.stButton > button {

    width: 100%;

    border: none;

    border-radius: 18px;

    padding: 14px;

    background: linear-gradient(
        135deg,
        #315CFD,
        #1E88E5
    );

    color: white;

    font-size: 17px;

    font-weight: 600;

    transition: 0.3s;
}

div.stButton > button:hover {

    transform: scale(1.02);
}

div.stDownloadButton > button {

    width: 100%;

    border: none;

    border-radius: 18px;

    padding: 14px;

    background: linear-gradient(
        135deg,
        #315CFD,
        #1E88E5
    );

    color: white;

    font-size: 17px;

    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📚 Student Dashboard")

if not st.session_state.logged_in:

    if st.sidebar.button("🏠 Home"):
        st.session_state.page = "Home"

    if st.sidebar.button("🔐 Login"):
        st.session_state.page = "Login"

    if st.sidebar.button("📝 Sign Up"):
        st.session_state.page = "Sign Up"

else:

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (st.session_state.username,)
    )

    data = cursor.fetchone()

    user_data = {
        "username": data[0],
        "name": data[1],
        "class": data[6],
        "school": data[7],
        "photo": data[8]
    }

    st.sidebar.markdown("## 👤 Student Profile")

    if user_data["photo"] and os.path.exists(user_data["photo"]):

        with open(user_data["photo"], "rb") as image_file:

            encoded = base64.b64encode(
                image_file.read()
            ).decode()

        st.sidebar.markdown(
            f"""
            <center>
                <img src="data:image/png;base64,{encoded}"
                     class="profile-pic">
            </center>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown(
        f"""
        <center>

        <h2>{user_data['name']}</h2>

        <p>Class {user_data['class']}</p>

        <p>{user_data['school']}</p>

        </center>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("📊 Dashboard"):
        st.session_state.page = "Result"

    if st.sidebar.button("📝 New Prediction"):
        st.session_state.page = "App"

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Login"

        if os.path.exists("current_user.txt"):
            os.remove("current_user.txt")

        st.rerun()

# =========================================================
# HOME PAGE
# =========================================================
if st.session_state.page == "Home" and not st.session_state.logged_in:

    st.title("🎓 Student Performance Dashboard")

    st.write(
        "AI Powered Academic Performance Analysis System"
    )

# =========================================================
# LOGIN PAGE
# =========================================================
elif st.session_state.page == "Login" and not st.session_state.logged_in:

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "App"

            with open("current_user.txt", "w") as f:
                f.write(username)

            st.success("Login Successful")

            st.rerun()

        else:

            st.error("Invalid Username or Password")

# =========================================================
# SIGNUP PAGE
# =========================================================
elif st.session_state.page == "Sign Up" and not st.session_state.logged_in:

    st.title("📝 Create Account")

    name = st.text_input("Full Name")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    dob = st.date_input("Date of Birth")

    age = st.number_input(
        "Age",
        5,
        100
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    student_class = st.selectbox(
        "Class",
        ["1","2","3","4","5","6","7","8","9","10","11","12"]
    )

    school = st.text_input("School Name")

    photo = st.file_uploader(
        "Upload Profile Photo",
        type=["jpg","png","jpeg"]
    )

    if st.button("Create Account"):

        if password != confirm_password:

            st.error("Passwords do not match")

        else:

            cursor.execute(
                "SELECT * FROM users WHERE username=?",
                (username,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                st.error("Username already exists")

            else:

                photo_path = ""

                if photo:

                    photo_path = f"{username}_{photo.name}"

                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                cursor.execute("""
                INSERT INTO users
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username,
                    name,
                    password,
                    str(dob),
                    age,
                    gender,
                    student_class,
                    school,
                    photo_path
                ))

                conn.commit()

                st.success("Account Created Successfully")

                st.session_state.page = "Login"

                st.rerun()

# =========================================================
# PREDICTION PAGE
# =========================================================
elif st.session_state.logged_in and st.session_state.page == "App":

    st.title("📊 Student Score Predictor")

    model = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    col1, col2 = st.columns(2)

    with col1:

        hours = st.slider("Hours Studied", 0, 12, 5)

        attendance = st.slider("Attendance %", 0, 100, 75)

        previous = st.slider("Previous Score", 0, 100, 60)

    with col2:

        sleep = st.slider("Sleep Hours", 0, 12, 7)

        motivation = st.selectbox(
            "Motivation",
            ["Low","Medium","High"]
        )

        internet = st.selectbox(
            "Internet Access",
            ["Yes","No"]
        )

    if st.button("🚀 Predict Score"):

        input_data = pd.DataFrame([{

            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Sleep_Hours": sleep,
            "Motivation_Level": motivation,
            "Internet_Access": internet

        }])

        input_data = pd.get_dummies(input_data)

        input_data = input_data.reindex(
            columns=columns,
            fill_value=0
        )

        prediction = model.predict(input_data)[0]

        score = int(round(prediction))

        if score >= 90:
            grade = "A+"

        elif score >= 80:
            grade = "A"

        elif score >= 70:
            grade = "B"

        elif score >= 60:
            grade = "C"

        else:
            grade = "D"

        st.session_state.prediction_result = score
        st.session_state.grade = grade
        st.session_state.page = "Result"

        st.rerun()

# =========================================================
# RESULT PAGE
# =========================================================
elif st.session_state.page == "Result":

    score = st.session_state.prediction_result
    grade = st.session_state.grade

    if score is None:
        score = 0

    if grade is None:
        grade = "N/A"

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (st.session_state.username,)
    )

    data = cursor.fetchone()

    user_data = {
        "name": data[1],
        "class": data[6],
        "school": data[7]
    }

    st.markdown(
        """
        <div class="dashboard-title">
            📊 Student Performance Dashboard
        </div>

        <div class="dashboard-subtitle">
            AI-Powered Academic Performance Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    # TOP SECTION
    left, right1, right2 = st.columns([2.2, 1, 1])

    with left:

        st.markdown(
            f"""
            <div class="main-score-card">

                <div class="main-score-title">
                    Predicted Score
                </div>

                <div class="main-score">
                    {score}
                    <span class="score-total">/100</span>
                </div>

                <div class="progress-container">

                    <div class="progress-fill"
                        style="width:{score}%;">
                    </div>

                </div>

                <div class="insight-box">
                    ⭐ Keep improving! Daily consistency
                    leads to better academic growth.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with right1:

        st.markdown(
            f"""
            <div class="small-card">

                <div class="small-title">
                    Grade
                </div>

                <div class="grade-circle">
                    {grade}
                </div>

                <div class="performance-pill">
                    Academic Grade
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with right2:

        if score >= 90:
            level = "Excellent 🚀"

        elif score >= 75:
            level = "Very Good 🎯"

        elif score >= 60:
            level = "Good 👍"

        else:
            level = "Needs Improvement 📚"

        st.markdown(
            f"""
            <div class="small-card">

                <div class="small-title">
                    Performance
                </div>

                <h1 style="
                    font-size:55px;
                    margin-top:40px;
                    color:#1D4ED8;
                ">
                    {score}%
                </h1>

                <div class="performance-pill"
                     style="margin-top:35px;">
                    {level}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # GRAPH
    st.markdown(
        """
        <div class="section-card">

            <div class="section-title">
                📈 Performance Overview
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    fig1, ax1 = plt.subplots(figsize=(12, 2))

    ax1.barh(
        ["Performance"],
        [score],
        height=0.4
    )

    ax1.set_xlim(0, 100)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)

    ax1.tick_params(axis='y', length=0)

    st.pyplot(fig1)