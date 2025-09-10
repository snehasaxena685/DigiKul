import streamlit as st
import sqlite3, os, cv2
from datetime import datetime
from PIL import Image
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

print("All modules loaded successfully!")
# ---------------------------
# DB Setup
# ---------------------------
DB_PATH = "data/sfda_prototype.db"
os.makedirs("data/registered_faces", exist_ok=True)
os.makedirs("data/attendance_photos", exist_ok=True)
os.makedirs("data/resources", exist_ok=True)

PDF_PATH = "data/resources/grains_basics.pdf"

# ---------------------------
# Generate Sample Knowledge PDF
# ---------------------------
def generate_pdf():
    if not os.path.exists(PDF_PATH):
        c = canvas.Canvas(PDF_PATH, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Basics of Grains & Cooking")

        c.setFont("Helvetica", 12)
        text = [
            "Grains are staple foods and provide essential carbohydrates, fiber, and nutrients.",
            "",
            "Types of Grains:",
            "- Rice: Common in Asian diets, rich in carbohydrates.",
            "- Wheat: Used in bread, chapati, pasta, bakery products.",
            "- Maize (Corn): Consumed boiled, roasted, or ground into flour.",
            "- Millets: High in fiber and minerals (Ragi, Jowar, Bajra).",
            "",
            "Cooking Basics:",
            "- Wash grains before cooking to remove dust and excess starch.",
            "- Soak grains to reduce cooking time and improve digestibility.",
            "- Proper storage prevents pest infestation.",
            "",
            "Nutritional Value:",
            "- Rich source of energy.",
            "- Provide dietary fiber for digestion.",
            "- Contain vitamins (B-complex) and minerals.",
            "",
            "Food Science Insight:",
            "- Fermentation improves nutrient absorption.",
            "- Mixing grains with legumes enhances protein quality.",
        ]

        y = 720
        for line in text:
            c.drawString(50, y, line)
            y -= 20

        c.save()

# ---------------------------
# Initialize DB
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    # --- Add face_registered column if missing ---
    try:
        c.execute("ALTER TABLE users ADD COLUMN face_registered INTEGER DEFAULT 0")
    except:
        pass

    # Attendance table
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        timestamp TEXT,
        photo_path TEXT
    )""")

    # Feedback table
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        feedback TEXT,
        timestamp TEXT
    )""")

    # Curriculum / Notice Board
    c.execute("""CREATE TABLE IF NOT EXISTS curriculum (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        timestamp TEXT
    )""")

    conn.commit()
    conn.close()

    # Default users
    add_user("sneha@123456789", "123456789", "admin")
    add_user("student1", "123456", "student")

def add_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password,role,face_registered) VALUES (?,?,?,0)",
                  (username, password, role))
        conn.commit()
    except:
        pass
    conn.close()

def get_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

def list_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT username, face_registered FROM users WHERE role='student'", conn)
    conn.close()
    return df

def mark_attendance(username, frame=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    photo_path = None
    if frame is not None:
        photo_path = f"data/attendance_photos/{username}_{int(datetime.now().timestamp())}.jpg"
        cv2.imwrite(photo_path, frame)
    c.execute("INSERT INTO attendance (username, timestamp, photo_path) VALUES (?,?,?)",
              (username, ts, photo_path))
    conn.commit()
    conn.close()

def save_feedback(username, fb):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO feedback (username, feedback, timestamp) VALUES (?,?,?)", (username, fb, ts))
    conn.commit()
    conn.close()

def update_face_registered(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET face_registered=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ---------------------------
# Curriculum Functions
# ---------------------------
def add_curriculum(title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO curriculum (title, content, timestamp) VALUES (?,?,?)", (title, content, ts))
    conn.commit()
    conn.close()

def list_curriculum():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM curriculum ORDER BY id DESC", conn)
    conn.close()
    return df

# ---------------------------
# Haar Cascade Setup
# ---------------------------
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(HAAR_PATH)

def capture_face(username):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False, None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) > 0:
        path = f"data/registered_faces/{username}.jpg"
        cv2.imwrite(path, frame)
        update_face_registered(username)
        return True, frame
    return False, frame

def detect_face_and_mark(username, max_frames=20):
    cap = cv2.VideoCapture(0)
    detected = False
    frame_out = None
    for _ in range(max_frames):
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            detected = True
            frame_out = frame
            mark_attendance(username, frame_out)
            break
    cap.release()
    return detected, frame_out

# ---------------------------
# Streamlit UI + Session
# ---------------------------
st.set_page_config(page_title="DigiKul Prototype", page_icon="📚", layout="wide")
st.title("📚 DigiKul: Smart Digital Gurukul Prototype")

# Initialize DB & PDF
init_db()
generate_pdf()

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["role"] = None

# ---------------------------
# Curriculum Notice Board (Always Visible)
# ---------------------------
with st.sidebar:
    st.subheader("📚 Curriculum / Notice Board")
    curriculum_df = list_curriculum()
    if not curriculum_df.empty:
        for _, row in curriculum_df.iterrows():
            st.markdown(f"**{row['title']}**  \n📅 {row['timestamp']}  \n{row['content']}")
            st.markdown("---")
    else:
        st.info("More updates coming soon...")

    st.download_button(
        label="📥 Download Grains Basics PDF",
        data=open(PDF_PATH, "rb").read(),
        file_name="grains_basics.pdf",
        mime="application/pdf"
    )

# ---------------------------
# Not logged in
# ---------------------------
if st.session_state["user"] is None:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("📝 Register New Student")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            if username and password:
                add_user(username, password, "student")
                st.success("✅ Registered successfully! Now capture face.")
            else:
                st.error("Please fill all fields.")

        if st.button("📷 Capture Face for Registration"):
            if username:
                ok, frame = capture_face(username)
                if ok:
                    st.success("✅ Face captured and saved!")
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Captured Face")
                else:
                    st.error("❌ No face detected. Try again.")
            else:
                st.error("Enter username first.")

    elif choice == "Login":
        st.subheader("🔐 Student/Admin Login")
        role = st.selectbox("Role", ["student", "admin"])

        if role == "student":
            students_df = list_students()
            st.write("📋 Registered Students:")
            st.dataframe(students_df)

            student_names = students_df["username"].tolist()
            selected_student = st.selectbox("Select Student", student_names)
            password = st.text_input("Password", type="password")

            if st.button("Login as Student"):
                user = get_user(selected_student, password)
                if user and user[3] == "student":
                    st.session_state["user"] = selected_student
                    st.session_state["role"] = "student"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        else:  # admin login
            username = st.text_input("Admin Username")
            password = st.text_input("Password", type="password")
            if st.button("Login as Admin"):
                user = get_user(username, password)
                if user and user[3] == "admin":
                    st.session_state["user"] = username
                    st.session_state["role"] = "admin"
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

# ---------------------------
# Logged in
# ---------------------------
else:
    username = st.session_state["user"]
    role = st.session_state["role"]
    st.success(f"Welcome {username} ({role})")

    if role == "student":
        st.subheader("🎓 Student Dashboard")

        if st.button("Mark Attendance (Face Detection)"):
            ok, frame = detect_face_and_mark(username)
            if ok:
                st.success("✅ Face detected, attendance marked!")
                if frame is not None:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Detected Face")
            else:
                st.error("❌ No face detected. Try again.")

        task = st.text_area("Write what you learned today")
        if st.button("Submit Feedback"):
            if task.strip():
                save_feedback(username, task)
                st.success("✅ Feedback submitted")
            else:
                st.error("Feedback cannot be empty.")

    elif role == "admin":
        st.subheader("👨‍🏫 Admin Dashboard")

        # Sidebar student list
        st.sidebar.subheader("📋 Registered Students")
        students_df = list_students()
        st.sidebar.dataframe(students_df)

        # Add Curriculum
        st.subheader("📚 Add Curriculum / Notice")
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.button("Post Curriculum"):
            if title.strip() and content.strip():
                add_curriculum(title, content)
                st.success("✅ Curriculum added!")
                st.rerun()
            else:
                st.error("Fill both fields.")

        conn = sqlite3.connect(DB_PATH)
        att = pd.read_sql("SELECT * FROM attendance", conn)
        fb = pd.read_sql("SELECT * FROM feedback", conn)
        conn.close()

        st.write("📊 Attendance Records (with Photos)")
        if not att.empty:
            for i, row in att.iterrows():
                cols = st.columns([2, 2, 3])
                cols[0].write(row["username"])
                cols[1].write(row["timestamp"])
                if row["photo_path"] and os.path.exists(row["photo_path"]):
                    cols[2].image(row["photo_path"], width=100)
                else:
                    cols[2].write("No photo")
        else:
            st.info("No attendance records yet.")

        st.write("📝 Feedback Records")
        st.dataframe(fb)

    if st.button("🔓 Logout"):
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.rerun()
