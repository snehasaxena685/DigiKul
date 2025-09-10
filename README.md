# DigiKul: Smart Digital Gurukul Prototype

## 🌟 Overview
DigiKul is a Streamlit-based AI/ML prototype for training and evaluation in Food Science & Technology.  
It integrates **facial biometrics, attendance tracking, trainee task evaluation, digital feedback, and automatic notes generation** — all in one system.  

Designed as an **X-factor prototype** for Project Assistant-II interviews, this project shows how **Computer Science can empower food processing training** in India.  

---

## ⚙️ Features
- 👩‍🎓 **Student Login** – Upload face, mark attendance, view progress & notes.  
- 👨‍🏫 **Admin Login** – Manage students, track attendance, view feedback, download reports.  
- 📸 **Facial Biometric Attendance** – Uses AI-powered face recognition (OpenCV + face_recognition).  
- 🥖 **Task Evaluation (Demo)** – Mediapipe-based activity detection to check if task is performed correctly.  
- 📝 **Feedback Forms** – Collects responses digitally and stores in SQLite database.  
- 📊 **Dashboards** – Track student performance & attendance.  
- 📚 **Auto Notes** – Generates reference notes for trainees after sessions.  

---

## 📂 File Structure
DigiKul/
│── SFDA_streamlit_prototype.py # Main Streamlit app
│── requirements.txt # Python dependencies
│── README.md # Setup + usage instructions
│
├── data/
│ ├── sfda_prototype.db # SQLite database
│ └── registered_faces/ # Saved student face images
│
├── assets/
│ ├── logo.png # App logo (optional)
│ └── demo_samples/ # Sample food/task images/videos
│
└── docs/
├── prototype_overview.pdf # For demo explanation
└── pitch_script.txt # Interview pitch backup