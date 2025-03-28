import streamlit as st
import random
import time
import sqlite3
import threading

# Initialize in-memory database
def init_db():
    try:
        conn = sqlite3.connect(":memory:", check_same_thread=False, timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE questions (
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
            CREATE TABLE leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                score INTEGER
            )
        """)
        conn.commit()
        return conn
    except sqlite3.OperationalError as e:
        st.error(f"Database initialization failed: {str(e)}")
        raise

# Fake persistence with session state
if "questions" not in st.session_state:
    st.session_state.questions = []  # List of tuples: (id, question, opt1, opt2, opt3, opt4, answer)
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {}  # Dict: {username: score}
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

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
    
    # Sync session state questions to DB
    for q in st.session_state.questions:
        cursor.execute("INSERT INTO questions (id, question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?, ?)", q)
    conn.commit()

    action = st.radio("⚙️ Manage Questions", ["➕ Add Question", "❌ Remove Question", "📊 View Leaderboard"])
    
    if action == "➕ Add Question":
        with st.form("add_question"):
            q = st.text_input("Enter Question")
            options = [st.text_input(f"Option {i+1}") for i in range(4)]
            answer = st.selectbox("✅ Correct Answer", options)
            if st.form_submit_button("Add Question"):
                with lock:
                    # Get next ID
                    cursor.execute("SELECT MAX(id) FROM questions")
                    max_id = cursor.fetchone()[0]
                    new_id = (max_id or 0) + 1
                    new_question = (new_id, q, *options, answer)
                    st.session_state.questions.append(new_question)
                    cursor.execute("INSERT INTO questions (id, question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?, ?)", new_question)
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
                    q_id = question_dict[selected_q]
                    cursor.execute("DELETE FROM questions WHERE id = ?", (q_id,))
                    st.session_state.questions = [q for q in st.session_state.questions if q[0] != q_id]
                    conn.commit()
                st.success("✅ Question Removed Successfully!")
        else:
            st.write("No questions available to remove.")
    
    elif action == "📊 View Leaderboard":
        st.subheader("🏆 Leaderboard")
        if st.session_state.leaderboard:
            sorted_leaderboard = sorted(st.session_state.leaderboard.items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (user, score) in enumerate(sorted_leaderboard, 1):
                st.write(f"**{i}. {user}: {score} points**")
        else:
            st.write("No leaderboard data available.")
    conn.close()

def student_quiz():
    st.title("🎓 Quiz Application")
    
    # Initialize session state keys
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
    
    conn = init_db()
    cursor = conn.cursor()
    
    # Sync session state questions to DB
    for q in st.session_state.questions:
        cursor.execute("INSERT INTO questions (id, question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?, ?)", q)
    conn.commit()

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
                st.session_state.leaderboard[st.session_state.username] = st.session_state.score
                cursor.execute("INSERT OR REPLACE INTO leaderboard (username, score) VALUES (?, ?)",
                               (st.session_state.username, st.session_state.score))
                conn.commit()
                st.success("✅ Score Submitted!")
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.score = 0
                st.session_state.answered_questions = set()
                st.session_state.current_question = None
                st.rerun()
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
            st.session_state.leaderboard[st.session_state.username] = st.session_state.score
            cursor.execute("INSERT OR REPLACE INTO leaderboard (username, score) VALUES (?, ?)",
                           (st.session_state.username, st.session_state.score))
            conn.commit()
            st.success("✅ Score Submitted!")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.score = 0
            st.session_state.answered_questions = set()
            st.session_state.current_question = None
            st.rerun()
    
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
