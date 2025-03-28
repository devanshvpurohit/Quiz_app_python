import streamlit as st
import random
import time
import sqlite3
import threading

# Initialize database connection
def init_db():
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

# Admin authentication
ADMIN_CREDENTIALS = {"ECELL": "admin123", "ADMINISECELL": "securepass"}

def admin_login():
    st.title("Admin Panel")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        if ADMIN_CREDENTIALS.get(admin_user) == admin_pass:
            st.session_state["admin_authenticated"] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def manage_questions():
    conn = init_db()
    cursor = conn.cursor()
    action = st.radio("Manage Questions", ["Add Question", "Remove Question", "View Leaderboard"])
    
    if action == "Add Question":
        with st.form("add_question"):
            q = st.text_input("Enter Question")
            options = [st.text_input(f"Option {i+1}") for i in range(4)]
            answer = st.selectbox("Correct Answer", options)
            if st.form_submit_button("Add Question"):
                with lock:
                    cursor.execute("INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                                   (q, *options, answer))
                    conn.commit()
                st.success("Question Added Successfully!")
    
    elif action == "Remove Question":
        cursor.execute("SELECT id, question FROM questions")
        questions = cursor.fetchall()
        if questions:
            question_dict = {q[1]: q[0] for q in questions}
            selected_q = st.selectbox("Select Question to Remove", list(question_dict.keys()))
            if st.button("Remove Question"):
                with lock:
                    cursor.execute("DELETE FROM questions WHERE id = ?", (question_dict[selected_q],))
                    conn.commit()
                st.success("Question Removed Successfully!")
        else:
            st.write("No questions available to remove.")
    
    elif action == "View Leaderboard":
        st.subheader("Leaderboard")
        try:
            cursor.execute("SELECT username, score FROM leaderboard ORDER BY score DESC LIMIT 10")
            data = cursor.fetchall()
            if data:
                for i, (user, score) in enumerate(data, 1):
                    st.write(f"{i}. {user}: {score} points")
            else:
                st.write("No leaderboard data available.")
        except sqlite3.OperationalError as e:
            st.error("Error fetching leaderboard: " + str(e))
    conn.close()

def student_quiz():
    conn = init_db()
    cursor = conn.cursor()
    st.title("Quiz Application")
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    if not questions:
        st.write("No questions available. Please ask admin to add questions.")
        return
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "answered_questions" not in st.session_state:
        st.session_state.answered_questions = set()
    available_questions = [q for q in questions if q[0] not in st.session_state.answered_questions]
    if available_questions:
        st.session_state.current_question = random.choice(available_questions)
        st.session_state.answered_questions.add(st.session_state.current_question[0])
    question = st.session_state.current_question
    st.subheader(question[1])
    selected_option = st.radio("Choose your answer", question[2:6], key="answer")
    if st.button("Submit Answer"):
        if selected_option == question[6]:
            st.success("Correct!")
            st.balloons()
            st.session_state.score += 1
        else:
            st.error(f"Incorrect! The correct answer is {question[6]}.")
        time.sleep(1)
        st.rerun()
    username = st.text_input("Enter your name for leaderboard")
    if st.button("Submit Score") and username:
        with lock:
            cursor.execute("INSERT INTO leaderboard (username, score) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET score=score+?", (username, st.session_state.score, st.session_state.score))
            conn.commit()
        st.success("Score Submitted!")
    conn.close()

# Page selection
page = st.sidebar.radio("Select Mode", ["Student Quiz", "Admin Panel"])
if page == "Admin Panel":
    if not st.session_state.get("admin_authenticated"):
        admin_login()
    else:
        manage_questions()
else:
    student_quiz()
