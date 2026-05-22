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

.student-card {

    background: #111827;
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 25px;
    margin-bottom: 25px;

}

.rank-badge {

    width: 55px;
    height: 55px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 22px;
    font-weight: bold;

    color: white;

    position: absolute;
    top: -10px;
    right: -10px;

    border: 4px solid #0f172a;

}

.gold {
    background: linear-gradient(135deg, #FFD700, #FFA500);
}

.silver {
    background: linear-gradient(135deg, #C0C0C0, #808080);
}

.bronze {
    background: linear-gradient(135deg, #CD7F32, #8B4513);
}

.normal {
    background: #334155;
}

.student-photo {

    border-radius: 50%;
    width: 130px;
    height: 130px;

    object-fit: cover;

    border: 5px solid #334155;

}

.photo-wrapper {

    position: relative;
    width: 130px;
    margin: auto;

}

[data-testid="stMetric"] {

    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 10px;
    border-radius: 15px;

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

        # SAVE DATABASE

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

        # =====================================
        # PHOTO
        # =====================================

        safe_name = name.lower().replace(" ", "_")

        photo_path_jpg = f"photos/{safe_name}.jpg"
        photo_path_png = f"photos/{safe_name}.png"

        if os.path.exists(photo_path_jpg):

            photo_path = photo_path_jpg

        elif os.path.exists(photo_path_png):

            photo_path = photo_path_png

        else:

            photo_path = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        # =====================================
        # RANK
        # =====================================

        rank = index + 1

        if rank == 1:

            badge = "🥇"

        elif rank == 2:

            badge = "🥈"

        elif rank == 3:

            badge = "🥉"

        else:

            badge = "🏅"

        # =====================================
        # CARD CONTAINER
        # =====================================

        with st.container():

            # CENTER PHOTO

            c1, c2, c3 = st.columns([1,2,1])

            with c2:

                st.image(
                    photo_path,
                    width=130
                )

            # RANK BADGE

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

            # NAME

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

            # METRICS

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

            # PROGRESS BAR

            progress = min(
                max(details["Score"], 0),
                100
            )

            st.progress(progress)

            # LEVEL BADGE

            if details["Score"] >= 100:

                st.success("🏆 English Master")

            elif details["Score"] >= 70:

                st.success("⭐ Super Speaker")

            elif details["Score"] >= 40:

                st.info("🔥 Improving Fast")

            else:

                st.warning("💪 Keep Practicing")

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

st.divider()

# ========================================
# RESET SCORES
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

        # ADD MAIN FILES

        files_to_backup = [

            "app.py",
            "english_class.db",
            "requirements.txt"

        ]

        for file in files_to_backup:

            if os.path.exists(file):

                zipf.write(file)

        # ADD PHOTOS FOLDER

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
