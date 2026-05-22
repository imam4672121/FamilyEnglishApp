import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sqlite3
import streamlit as st

# ========================================
# PASSWORD PROTECTION
# ========================================

APP_PASSWORD = st.secrets["APP_PASSWORD"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🏠 Family English Learning System")

    password = st.text_input(
        "🔐 Enter Family Password",
        type="password"
    )

    if st.button("LOGIN"):

        if password == APP_PASSWORD:

            st.session_state.logged_in = True
            st.rerun()

        else:

            st.error("❌ Wrong Password")

    st.stop()
# ========================================
# PAGE CONFIG
# ========================================

st.set_page_config(
    page_title="Family English Dashboard",
    page_icon="🏆",
    layout="wide"
)

# ========================================
# DATABASE CONNECTION
# ========================================

conn = sqlite3.connect(
    "english_class.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ========================================
# CREATE TABLE
# ========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (

    name TEXT PRIMARY KEY,
    score INTEGER,
    correct INTEGER,
    wrong INTEGER,
    voice INTEGER

)
""")

conn.commit()

# ========================================
# DEFAULT STUDENTS
# ========================================

default_students = [
    "Nisha",
    "Regina",
    "Shahe_meeran",
    "Farvin",
    "Jasir"
]

for student in default_students:

    cursor.execute(
        "SELECT * FROM students WHERE name=?",
        (student,)
    )

    existing = cursor.fetchone()

    if not existing:

        cursor.execute("""
        INSERT INTO students
        VALUES (?, ?, ?, ?, ?)
        """, (student, 0, 0, 0, 0,))

conn.commit()

# ========================================
# LOAD STUDENTS FROM DATABASE
# ========================================

cursor.execute("SELECT * FROM students")

rows = cursor.fetchall()

students = {}

for row in rows:

    students[row[0]] = {

    "Score": row[1],
    "Correct": row[2],
    "Wrong": row[3],
    "Voice": row[4]

    }

# ========================================
# CUSTOM CSS
# ========================================

st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

h1, h2, h3 {
    color: white;
}

[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #334155;
}

.student-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #334155;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# ========================================
# TITLE
# ========================================

st.title("🏆 FAMILY ENGLISH CLASS DASHBOARD")
st.caption("Interactive English learning performance tracker")

# ========================================
# CONVERT TO DATAFRAME
# ========================================

student_data = []

for name, details in students.items():

    student_data.append({
        "Student": name,
        "Score": details["Score"],
        "Correct": details["Correct"],
        "Wrong": details["Wrong"],
        "Voice": details["Voice"],
    })

df = pd.DataFrame(student_data)

# ========================================
# TOP METRICS
# ========================================

st.subheader("📊 Class Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👨‍🎓 Total Students",
        len(df)
    )

with col2:
    st.metric(
        "⭐ Total Points",
        int(df['Score'].sum())
    )

with col3:
    st.metric(
        "✅ Correct Answers",
        int(df['Correct'].sum())
    )

with col4:
    st.metric(
        "🏆 Highest Score",
        int(df['Score'].max())
    )

st.divider()

# ========================================
# UPDATE SECTION
# ========================================

st.subheader("➕ Update Student Performance")

c1, c2, c3 = st.columns([2,2,1])

with c1:

    selected_student = st.selectbox(
        "Select Student",
        list(students.keys())
    )

with c2:

    activity = st.selectbox(
        "Select Activity",
        [
          "Correct Answer (+10)",
          "Wrong Answer (-5)",
          "Voice Message (+5)",
          "Extra Mark (+5)"
        ]
    )

with c3:

    st.write("")
    st.write("")

    if st.button("ADD SCORE", use_container_width=True):

        if activity == "Correct Answer (+10)":

           students[selected_student]["Score"] += 10
           students[selected_student]["Correct"] += 1

        elif activity == "Wrong Answer (-5)":

            students[selected_student]["Score"] -= 5
            students[selected_student]["Wrong"] += 1

        elif activity == "Voice Message (+5)":

            students[selected_student]["Score"] += 5
            students[selected_student]["Voice"] += 1
            
        elif activity == "Extra Mark (+5)":

            students[selected_student]["Score"] += 5

        # SAVE TO DATABASE
        cursor.execute("""

        UPDATE students

        SET
             score=?,
             correct=?,
             wrong=?,
             voice=?

         WHERE name=?

        """, (

            students[selected_student]["Score"],
            students[selected_student]["Correct"],
            students[selected_student]["Wrong"],
            students[selected_student]["Voice"],
            selected_student

        ))

        conn.commit()

        st.success(f"{selected_student} updated successfully!")

        st.rerun()

st.divider()

# ========================================
# STUDENT CARDS
# ========================================

st.subheader("👨‍🎓 Student Performance Cards")

sorted_students = sorted(
    students.items(),
    key=lambda x: x[1]["Score"],
    reverse=True
)

cols = st.columns(3)

for index, (name, details) in enumerate(sorted_students):

    with cols[index % 3]:

        st.markdown(
            "<div class='student-card'>",
            unsafe_allow_html=True
        )

        # PHOTO PATH
        safe_name = name.lower().replace(" ", "_")

        photo_path_jpg = f"photos/{safe_name}.jpg"
        photo_path_png = f"photos/{safe_name}.png"

        # SHOW PHOTO
        if os.path.exists(photo_path_jpg):

            st.image(photo_path_jpg, width=120)

        elif os.path.exists(photo_path_png):

            st.image(photo_path_png, width=120)

        else:

            st.image(
                "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                width=120
            )

        # NAME
        st.markdown(f"### 👤 {name}")
        # SINGLE ROW METRICS
# =====================================

        m1, m2, m3, m4 = st.columns(4)

        with m1:
                st.metric(
                        "⭐ Score",
                        details["Score"]
                    )

        with m2:
                st.metric(
                        "✅ Correct",
                        details["Correct"]
                    )

        with m3:
                st.metric(
                        "❌ Wrong",
                        details["Wrong"]
                    )

        with m4:
                st.metric(
                        "🎤 Voice",
                        details["Voice"]
                    )

        # SCORE
        # =====================================


            

        # PROGRESS BAR
        progress = min(details["Score"], 100)

        st.progress(progress)

        # BADGES
        if details["Score"] >= 100:
            st.success("🏆 English Master")

        elif details["Score"] >= 70:
            st.success("⭐ Super Speaker")

        elif details["Score"] >= 40:
            st.info("🔥 Improving Fast")

        else:
            st.warning("💪 Keep Practicing")

        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ========================================
# SCORE CHART
# ========================================

st.subheader("📈 Student Score Analytics")

chart_df = pd.DataFrame(student_data)

chart = px.bar(
    chart_df,
    x="Student",
    y="Score",
    text="Score",
    color="Score"
)

chart.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    chart,
    use_container_width=True
)

st.divider()

# ========================================
# DOWNLOAD DATABASE
# ========================================

st.subheader("💾 Backup Database")

with open("english_class.db", "rb") as file:

    st.download_button(

        label="📥 Download Database Backup",

        data=file,

        file_name="english_class_backup.db",

        mime="application/octet-stream"

    )

# ========================================
# RESET BUTTON
# ========================================

st.subheader("⚙️ Controls")

if st.button("🔄 Reset Weekly Scores"):

    for student in students:

        cursor.execute("""

        UPDATE students

        SET
            score=0,
            correct=0,
            wrong=0,
            voice=0,

        WHERE name=?

        """, (student,))

    conn.commit()

    st.warning("Weekly scores reset successfully")

    st.rerun()
