import streamlit as st
import random
import time
import sqlite3
import threading
import os

# Initialize database connection
def init_db():
    # Nuke the old database file to start fresh
    if os.path.exists("quiz.db"):
        os.remove("quiz.db")
    
    conn = sqlite3.connect("quiz.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            answer TEXT
        );
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            score INTEGER
        );
    """)
    conn.commit()
    return conn

conn = init_db()
lock = threading.Lock()

# Apply Green & White Theme
st.markdown(
    """
    <style>
        body { background-color: white; }
        .stButton>button { background-color: #28a745; color: white; border-radius: 10px; }
        .stTextInput>div>div>input { border-radius: 10px; }
        .stRadio>div>label { color: #28a745; font-weight: bold; }
        .stSuccess { color: #28a745; font-weight: bold; }
        .stError { color: red; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# Admin authentication
ADMIN_CREDENTIALS = {"ECELL": "admin123", "ADMINISECELL": "securepass"}

def admin_login():
    st.title("🔐 Admin Panel")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        if ADMIN_CREDENTIALS.get(admin_user) == admin_pass:
            st.session_state["admin_authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def manage_questions():
    conn = init_db()
    cursor = conn.cursor()
    action = st.radio("⚙️ Manage Questions", ["➕ Add Question", "❌ Remove Question", "📊 View Leaderboard"])
    
    if action == "➕ Add Question":
        with st.form("add_question"):
            q = st.text_input("Enter Question")
            options = [st.text_input(f"Option {i+1}") for i in range(4)]
            answer = st.selectbox("✅ Correct Answer", options)
            if st.form_submit_button("Add Question"):
                with lock:
                    cursor.execute("INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                                   (q, *options, answer))
                    conn.commit()
                st.success("✅ Question Added Successfully!")
    
    elif action == "❌ Remove Question":
        cursor.execute("SELECT id, question FROM questions")
        questions = cursor.fetchall()
        if questions:
            question_dict = {q[1]: q[0] for q in questions}
            selected_q = st.selectbox("🗑 Select Question to Remove", list(question_dict.keys()))
            if st.button("Remove Question"):
                with lock:
                    cursor.execute("DELETE FROM questions WHERE id = ?", (question_dict[selected_q],))
                    conn.commit()
                st.success("✅ Question Removed Successfully!")
        else:
            st.write("No questions available to remove.")
    
    elif action == "📊 View Leaderboard":
        st.subheader("🏆 Leaderboard")
        try:
            cursor.execute("SELECT username, score FROM leaderboard ORDER BY score DESC LIMIT 10")
            data = cursor.fetchall()
            if data:
                for i, (user, score) in enumerate(data, 1):
                    st.write(f"**{i}. {user}: {score} points**")
            else:
                st.write("No leaderboard data available.")
        except sqlite3.OperationalError as e:
            st.error("⚠️ Error fetching leaderboard: " + str(e))
    conn.close()

def student_quiz():
    st.title("🎓 Quiz Application")
    
    # Initialize session state keys if they don’t exist
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "answered_questions" not in st.session_state:
        st.session_state.answered_questions = set()
    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    # Student Login
    if not st.session_state.logged_in:
        username_input = st.text_input("📝 Enter your username to start")
        if st.button("Start Quiz") and username_input:
            st.session_state.username = username_input
            st.session_state.logged_in = True
            st.session_state.score = 0
            st.session_state.answered_questions = set()
            st.session_state.current_question = None
            st.rerun()
        return
    
    # Database connection inside function
    conn = init_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    if not questions:
        st.write("⚠️ No questions available. Please ask admin to add questions.")
        conn.close()
        return
    
    available_questions = [q for q in questions if q[0] not in st.session_state.answered_questions]
    if not available_questions:
        st.write("🎉 You've answered all questions!")
        if st.button("Submit Score"):
            with lock:
                try:
                    cursor.execute("INSERT OR REPLACE INTO leaderboard (username, score) VALUES (?, ?)",
                                   (st.session_state.username, st.session_state.score))
                    conn.commit()
                    st.success("✅ Score Submitted!")
                    # Reset quiz state after submission
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.score = 0
                    st.session_state.answered_questions = set()
                    st.session_state.current_question = None
                    st.rerun()
                except sqlite3.OperationalError as e:
                    st.error(f"⚠️ Error submitting score: {str(e)}")
        conn.close()
        return
    
    if st.session_state.current_question is None or st.session_state.current_question[0] not in [q[0] for q in available_questions]:
        st.session_state.current_question = random.choice(available_questions)
        st.session_state.answered_questions.add(st.session_state.current_question[0])
    
    question = st.session_state.current_question
    st.subheader(question[1])
    selected_option = st.radio("🤔 Choose your answer", question[2:6], key=f"answer_{question[0]}")
    
    if st.button("Submit Answer"):
        if selected_option == question[6]:
            st.success("🎉 Correct!")
            st.balloons()
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect! The correct answer is {question[6]}.")
        time.sleep(1)
        st.rerun()
    
    if st.button("Submit Score"):
        with lock:
            try:
                cursor.execute("INSERT OR REPLACE INTO leaderboard (username, score) VALUES (?, ?)",
                               (st.session_state.username, st.session_state.score))
                conn.commit()
                st.success("✅ Score Submitted!")
                # Reset quiz state after submission
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.score = 0
                st.session_state.answered_questions = set()
                st.session_state.current_question = None
                st.rerun()
            except sqlite3.OperationalError as e:
                st.error(f"⚠️ Error submitting score: {str(e)}")
    
    conn.close()

# Page selection
page = st.sidebar.radio("📌 Select Mode", ["🎓 Student Quiz", "🔐 Admin Panel"])
if page == "🔐 Admin Panel":
    if not st.session_state.get("admin_authenticated", False):
        admin_login()
    else:
        manage_questions()
else:
    student_quiz()
