import streamlit as st
import random
import time
import json
import pandas as pd
import threading
import os

# Load questions from JSON file
def load_questions():
    try:
        with open("quiz_data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# Load or create leaderboard file
def load_leaderboard():
    if os.path.exists("leaderboard.xlsx"):
        return pd.read_excel("leaderboard.xlsx")
    else:
        return pd.DataFrame(columns=["Username", "Score"])

def save_leaderboard(df):
    df.to_excel("leaderboard.xlsx", index=False)

# Thread lock for safe file operations
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

def view_leaderboard():
    st.subheader("🏆 Leaderboard")
    leaderboard = load_leaderboard()
    if leaderboard.empty:
        st.write("No leaderboard data available.")
    else:
        leaderboard = leaderboard.sort_values(by="Score", ascending=False).reset_index(drop=True)
        st.dataframe(leaderboard)

def student_quiz():
    st.title("🎓 Quiz Application")
    
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
    
    questions = load_questions()
    
    if not questions:
        st.write("⚠️ No questions available. Please ask admin to add questions to the JSON file.")
        return
    
    available_questions = [q for q in questions if q["id"] not in st.session_state.answered_questions]
    if not available_questions:
        st.write("🎉 You've answered all questions!")
        if st.button("Submit Score"):
            with lock:
                leaderboard = load_leaderboard()
                new_entry = pd.DataFrame([[st.session_state.username, st.session_state.score]], columns=["Username", "Score"])
                leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
                save_leaderboard(leaderboard)
                st.success("✅ Score Submitted!")
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.score = 0
                st.session_state.answered_questions = set()
                st.session_state.current_question = None
                st.rerun()
        return
    
    if st.session_state.current_question is None or st.session_state.current_question["id"] not in [q["id"] for q in available_questions]:
        st.session_state.current_question = random.choice(available_questions)
        st.session_state.answered_questions.add(st.session_state.current_question["id"])
    
    question = st.session_state.current_question
    st.subheader(question["question"])
    selected_option = st.radio("🤔 Choose your answer", question["options"], key=f"answer_{question['id']}")
    
    if st.button("Submit Answer"):
        if selected_option == question["answer"]:
            st.success("🎉 Correct!")
            st.balloons()
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect! The correct answer is {question['answer']}")
        time.sleep(1)
        st.rerun()
    
    if st.button("Submit Score"):
        with lock:
            leaderboard = load_leaderboard()
            new_entry = pd.DataFrame([[st.session_state.username, st.session_state.score]], columns=["Username", "Score"])
            leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
            save_leaderboard(leaderboard)
            st.success("✅ Score Submitted!")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.score = 0
            st.session_state.answered_questions = set()
            st.session_state.current_question = None
            st.rerun()

# Page selection
page = st.sidebar.radio("📌 Select Mode", ["🎓 Student Quiz", "🔐 Admin Panel", "📊 Leaderboard"])
if page == "🔐 Admin Panel":
    if not st.session_state.get("admin_authenticated", False):
        admin_login()
    else:
        st.write("Admin functionalities are now managed externally. Modify 'quiz_data.json' directly.")
elif page == "📊 Leaderboard":
    view_leaderboard()
else:
    student_quiz()
