import streamlit as st
import random
import time
import sqlite3

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
            username TEXT,
            score INTEGER
        );
    """)
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

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
    action = st.radio("Manage Questions", ["Add Question", "Remove Question", "View Leaderboard"])
    if action == "Add Question":
        with st.form("add_question"):
            q = st.text_input("Enter Question")
            options = [st.text_input(f"Option {i+1}") for i in range(4)]
            answer = st.selectbox("Correct Answer", options)
            if st.form_submit_button("Add Question"):
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
                cursor.execute("DELETE FROM questions WHERE id = ?", (question_dict[selected_q],))
                conn.commit()
                st.success("Question Removed Successfully!")
        else:
            st.write("No questions available to remove.")
    elif action == "View Leaderboard":
        st.subheader("Leaderboard")
        cursor.execute("SELECT username, score FROM leaderboard ORDER BY score DESC")
        data = cursor.fetchall()
        if data:
            for i, (user, score) in enumerate(data, 1):
                st.write(f"{i}. {user}: {score} points")
        else:
            st.write("No leaderboard data available.")

def student_quiz():
    st.title("Quiz Application")
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    if not questions:
        st.write("No questions available. Please ask admin to add questions.")
        return
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = random.choice(questions)
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
        time.sleep(2)
        st.session_state.current_question = random.choice(questions)
        st.rerun()
    username = st.text_input("Enter your name for leaderboard")
    if st.button("Submit Score"):
        cursor.execute("INSERT INTO leaderboard (username, score) VALUES (?, ?)", (username, st.session_state.score))
        conn.commit()
        st.success("Score Submitted!")

# Page selection
page = st.sidebar.radio("Select Mode", ["Student Quiz", "Admin Panel"])
if page == "Admin Panel":
    if not st.session_state.get("admin_authenticated"):
        admin_login()
    else:
        manage_questions()
else:
    student_quiz()
