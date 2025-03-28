import streamlit as st
import random
import time
import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect("quiz.db", check_same_thread=False)
    cursor = conn.cursor()
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            username TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    return conn, cursor

conn, cursor = init_db()

# Admin authentication
admin_credentials = {"ECELL": "admin123", "ADMINISECELL": "securepass"}

# Page selection
page = st.sidebar.radio("Select Mode", ["Student Quiz", "Admin Panel"])

if page == "Admin Panel":
    st.title("Admin Panel")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if admin_user in admin_credentials and admin_credentials[admin_user] == admin_pass:
            st.success("Login successful!")
            
            action = st.radio("Manage Questions", ["Add Question", "Remove Question", "View Leaderboard"])
            
            if action == "Add Question":
                q = st.text_input("Enter Question")
                op1 = st.text_input("Option 1")
                op2 = st.text_input("Option 2")
                op3 = st.text_input("Option 3")
                op4 = st.text_input("Option 4")
                answer = st.selectbox("Correct Answer", [op1, op2, op3, op4])
                
                if st.button("Add Question"):
                    cursor.execute("INSERT INTO questions (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                                   (q, op1, op2, op3, op4, answer))
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
            
        else:
            st.error("Invalid credentials")

else:
    st.title("Quiz Application")
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = random.choice(questions) if questions else None
    
    if st.session_state.current_question:
        question = st.session_state.current_question
        st.subheader(question[1])
        selected_option = st.radio("Choose your answer", [question[2], question[3], question[4], question[5]], key="answer")
        
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
    else:
        st.write("No questions available. Please ask admin to add questions.")
