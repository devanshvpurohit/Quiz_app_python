import streamlit as st
import random
import time
import sqlite3
import pandas as pd

# Initialize database
conn = sqlite3.connect("quiz.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    answer TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leaderboard (
    user TEXT,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

# Admin credentials
ADMIN_USERS = {"ECELL": "admin123", "ADMINISECELL": "pass456"}

# Function to load questions from DB
def load_questions():
    cursor.execute("SELECT * FROM questions")
    return cursor.fetchall()

# Function to update leaderboard
def update_leaderboard(user):
    cursor.execute("SELECT * FROM leaderboard WHERE user = ?", (user,))
    if cursor.fetchone():
        cursor.execute("UPDATE leaderboard SET score = score + 1 WHERE user = ?", (user,))
    else:
        cursor.execute("INSERT INTO leaderboard (user, score) VALUES (?, 1)", (user,))
    conn.commit()

# Streamlit session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_admin = False

# Login Section
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username in ADMIN_USERS and ADMIN_USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = True
        st.sidebar.success("Admin Login Successful")
    else:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_admin = False
        st.sidebar.success("Student Login Successful")

if st.session_state.logged_in:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = False
        st.rerun()

    # Admin Dashboard
    if st.session_state.is_admin:
        st.title("Admin Dashboard")
        st.subheader("Add New Question")
        new_question = st.text_input("Question")
        option1 = st.text_input("Option 1")
        option2 = st.text_input("Option 2")
        option3 = st.text_input("Option 3")
        option4 = st.text_input("Option 4")
        correct_answer = st.selectbox("Correct Answer", [option1, option2, option3, option4])

        if st.button("Add Question"):
            cursor.execute("INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                           (new_question, option1, option2, option3, option4, correct_answer))
            conn.commit()
            st.success("Question Added Successfully")

        st.subheader("Existing Questions")
        questions = load_questions()
        for q in questions:
            st.write(f"{q[0]}. {q[1]}")
            if st.button(f"Delete {q[0]}", key=f"delete_{q[0]}"):
                cursor.execute("DELETE FROM questions WHERE id = ?", (q[0],))
                conn.commit()
                st.success("Question Deleted")
                st.rerun()
    
    else:
        # Student Quiz
        st.title("Live Quiz")
        questions = load_questions()
        if questions:
            if "current_question" not in st.session_state:
                st.session_state.current_question = random.choice(questions)

            question = st.session_state.current_question
            st.subheader(question[1])
            selected_option = st.radio("Choose your answer", [question[2], question[3], question[4], question[5]], key="answer")
            
            if st.button("Submit Answer"):
                if selected_option == question[6]:
                    st.success("Correct!")
                    update_leaderboard(st.session_state.username)
                    st.balloons()
                else:
                    st.error(f"Incorrect! The correct answer is {question[6]}.")

                time.sleep(3)
                st.session_state.current_question = random.choice(questions)
                st.rerun()
        else:
            st.warning("No questions available. Please contact the admin.")

    # Live Leaderboard
    st.sidebar.subheader("Leaderboard")
    leaderboard = pd.read_sql("SELECT * FROM leaderboard ORDER BY score DESC", conn)
    st.sidebar.table(leaderboard)
