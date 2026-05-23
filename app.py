import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import zipfile

# ========================================
# PAGE CONFIG
# ========================================

st.set_page_config(
    page_title="Family English Dashboard",
    page_icon="🏆",
    layout="wide"
)

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
# DATABASE CONNECTION
# ========================================

conn = sqlite3.connect(
    "english_class.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ========================================
# STUDENTS TABLE
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
# SUBJECT PERFORMANCE TABLE
# ========================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS activity_scores (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_name TEXT,
    category TEXT,

    correct INTEGER DEFAULT 0,
    wrong INTEGER DEFAULT 0,

    score INTEGER DEFAULT 0

)

""")

conn.commit()

# ========================================
# DEFAULT STUDENTS
# ========================================

default_students = [

    "Nisha",
    "Regina",
    "Shahe meeran",
    "Farvin",
    "Jasir"

]

# ========================================
# INSERT DEFAULT STUDENTS
# ========================================

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

        """, (

            student,
            0,
            0,
            0,
            0

        ))

conn.commit()

# ========================================
# DELETE DUPLICATE STUDENT
# ========================================

cursor.execute("""

DELETE FROM students
WHERE name='Shahe_meeran'

""")

conn.commit()

# ========================================
# LOAD DATABASE
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
    border: 1px solid #334155;
    padding: 10px;
    border-radius: 15px;

}

.subject-box {

    background-color:#1e293b;
    padding:10px;
    margin-bottom:8px;
    border-radius:10px;
    border:1px solid #334155;

}

</style>

""", unsafe_allow_html=True)

# ========================================
# TITLE
# ========================================

st.title("🏆 FAMILY ENGLISH CLASS DASHBOARD")

st.caption(
    "Interactive English learning performance tracker"
)

# ========================================
# DATAFRAME
# ========================================

student_data = []

for name, details in students.items():

    student_data.append({

        "Student": name,
        "Score": details["Score"],
        "Correct": details["Correct"],
        "Wrong": details["Wrong"],
        "Voice": details["Voice"]

    })

df = pd.DataFrame(student_data)

# ========================================
# CLASS OVERVIEW
# ========================================

st.subheader("📊 Class Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "👨‍🎓 Total Students",
        len(df)
    )

with c2:

    st.metric(
        "⭐ Total Points",
        int(df["Score"].sum())
    )

with c3:

    st.metric(
        "✅ Correct Answers",
        int(df["Correct"].sum())
    )

with c4:

    st.metric(
        "🏆 Highest Score",
        int(df["Score"].max())
    )

st.divider()

# ========================================
# UPDATE SCORE
# ========================================

st.subheader("➕ Update Student Performance")

u1, u2, u3 = st.columns([2,2,1])

with u1:

    selected_student = st.selectbox(
        "Select Student",
        list(students.keys())
    )

with u2:

    activity = st.selectbox(

        "Select Activity",

        [

            "Correct Answer (+10)",
            "Wrong Answer (-5)",
            "Voice Message (+5)",
            "Extra Mark (+5)"

        ]

    )

with u3:

    st.write("")
    st.write("")

    if st.button(
        "ADD SCORE",
        use_container_width=True
    ):

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

        st.success(
            f"{selected_student} updated successfully!"
        )

        st.rerun()

st.divider()

# ========================================
# SUBJECT PERFORMANCE TRACKER
# ========================================

st.subheader("📚 Subject-wise Performance Tracker")

s1, s2, s3, s4 = st.columns([2,2,2,1])

with s1:

    selected_student_subject = st.selectbox(

        "Select Student",

        list(students.keys()),

        key="subject_student"

    )

with s2:

    selected_category = st.selectbox(

        "Select Subject",

        [

            "Grammar",
            "Vocabulary",
            "Tenses",
            "Speaking",
            "Translation",
            "Reading",
            "Writing",
            "Pronunciation",
            "Conversation",
            "Memory Test"

        ]

    )

with s3:

    subject_result = st.selectbox(

        "Result",

        [

            "Correct (+10)",
            "Wrong (-5)"

        ]

    )

with s4:

    st.write("")
    st.write("")

    if st.button("ADD SUBJECT SCORE"):

        cursor.execute("""

        SELECT * FROM activity_scores

        WHERE student_name=?
        AND category=?

        """, (

            selected_student_subject,
            selected_category

        ))

        existing = cursor.fetchone()

        if existing:

            if subject_result == "Correct (+10)":

                cursor.execute("""

                UPDATE activity_scores

                SET

                    correct = correct + 1,
                    score = score + 10

                WHERE student_name=?
                AND category=?

                """, (

                    selected_student_subject,
                    selected_category

                ))

            else:

                cursor.execute("""

                UPDATE activity_scores

                SET

                    wrong = wrong + 1,
                    score = score - 5

                WHERE student_name=?
                AND category=?

                """, (

                    selected_student_subject,
                    selected_category

                ))

        else:

            if subject_result == "Correct (+10)":

                cursor.execute("""

                INSERT INTO activity_scores

                (

                    student_name,
                    category,
                    correct,
                    wrong,
                    score

                )

                VALUES (?, ?, ?, ?, ?)

                """, (

                    selected_student_subject,
                    selected_category,
                    1,
                    0,
                    10

                ))

            else:

                cursor.execute("""

                INSERT INTO activity_scores

                (

                    student_name,
                    category,
                    correct,
                    wrong,
                    score

                )

                VALUES (?, ?, ?, ?, ?)

                """, (

                    selected_student_subject,
                    selected_category,
                    0,
                    1,
                    -5

                ))

        conn.commit()

        st.success("Subject performance updated!")

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

        safe_name = name.lower().replace(" ", "_")

        photo_path_jpg = f"photos/{safe_name}.jpg"
        photo_path_png = f"photos/{safe_name}.png"

        if os.path.exists(photo_path_jpg):

            photo_path = photo_path_jpg

        elif os.path.exists(photo_path_png):

            photo_path = photo_path_png

        else:

            photo_path = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        rank = index + 1

        if rank == 1:
            badge = "🥇"

        elif rank == 2:
            badge = "🥈"

        elif rank == 3:
            badge = "🥉"

        else:
            badge = "🏅"

        c1, c2, c3 = st.columns([1,2,1])

        with c2:

            st.image(
                photo_path,
                width=130
            )

        st.markdown(

            f"""

            <div style='
                text-align:center;
                margin-top:-15px;
                margin-bottom:10px;
                font-size:28px;
                font-weight:bold;
            '>

            {badge} Rank #{rank}

            </div>

            """,

            unsafe_allow_html=True

        )

        st.markdown(

            f"""

            <h2 style='
                text-align:center;
                color:white;
            '>

            👤 {name}

            </h2>

            """,

            unsafe_allow_html=True

        )

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

        progress = min(
            max(details["Score"], 0),
            100
        )

        st.progress(progress)

        if details["Score"] >= 100:

            st.success("🏆 English Master")

        elif details["Score"] >= 70:

            st.success("⭐ Super Speaker")

        elif details["Score"] >= 40:

            st.info("🔥 Improving Fast")

        else:

            st.warning("💪 Keep Practicing")

        # ========================================
        # SUBJECT PERFORMANCE DISPLAY
        # ========================================

        cursor.execute("""

        SELECT

            category,
            score

        FROM activity_scores

        WHERE student_name=?

        ORDER BY score DESC

        """, (name,))

        subject_scores = cursor.fetchall()

        if subject_scores:

            st.markdown("### 📚 Subject-wise Performance")

            for subject in subject_scores:

                category = subject[0]
                score = subject[1]

                st.markdown(

                    f"""

                    <div class='subject-box'>

                    <b>{category}</b>

                    <span style='float:right;'>

                    ⭐ {score}

                    </span>

                    </div>

                    """,

                    unsafe_allow_html=True

                )

st.divider()

# ========================================
# ANALYTICS
# ========================================

st.subheader("📈 Student Score Analytics")

chart = px.bar(

    df,
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
# ========================================
# SUBJECT SCORE COMPARISON
# ========================================

st.subheader("📚 Subject-wise Student Comparison")

# LOAD SUBJECT DATA

subject_chart_df = pd.read_sql_query("""

SELECT

    student_name,
    category,
    score

FROM activity_scores

""", conn)

# CHECK DATA

if not subject_chart_df.empty:

    # CREATE GROUPED BAR CHART

    subject_chart = px.bar(

        subject_chart_df,

        x="student_name",
        y="score",

        color="category",

        barmode="group",

        text="score"

    )

    subject_chart.update_layout(

        template="plotly_dark",

        height=600,

        xaxis_title="Students",
        yaxis_title="Subject Score",

        legend_title="Subjects"

    )

    st.plotly_chart(

        subject_chart,
        use_container_width=True

    )

else:

    st.info("No subject performance data available yet.")
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
# RESET SCORES
# ========================================

st.divider()

st.subheader("⚙️ Controls")

if st.button("🔄 Reset Weekly Scores"):

    for student in students:

        cursor.execute("""

        UPDATE students

        SET

            score=0,
            correct=0,
            wrong=0,
            voice=0

        WHERE name=?

        """, (student,))

    conn.commit()

    st.warning(
        "Weekly scores reset successfully"
    )

    st.rerun()

# ========================================
# FULL PROJECT BACKUP
# ========================================

st.divider()

st.subheader("🗂️ Full Project Backup")

if st.button("📦 Create Full Backup ZIP"):

    zip_filename = "family_english_backup.zip"

    with zipfile.ZipFile(
        zip_filename,
        "w"
    ) as zipf:

        files_to_backup = [

            "app.py",
            "english_class.db",
            "requirements.txt"

        ]

        for file in files_to_backup:

            if os.path.exists(file):

                zipf.write(file)

        if os.path.exists("photos"):

            for foldername, subfolders, filenames in os.walk("photos"):

                for filename in filenames:

                    filepath = os.path.join(
                        foldername,
                        filename
                    )

                    zipf.write(filepath)

    st.success("✅ Backup ZIP Created Successfully!")

    with open(zip_filename, "rb") as f:

        st.download_button(

            label="⬇️ Download Full Backup",

            data=f,

            file_name=zip_filename,

            mime="application/zip"

        )
