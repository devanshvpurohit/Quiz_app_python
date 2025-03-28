import streamlit as st
import random
import time
import json
import threading

# Load questions from JSON file
def load_questions():
    try:
        with open("quiz_data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# Thread lock for safe operations
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
    
    available_questions = [q for q in questions if q.get("id") not in st.session_state.answered_questions]
    if not available_questions:
        st.write("🎉 You've answered all questions!")
        return
    
    if st.session_state.current_question is None or st.session_state.current_question.get("id") not in [q.get("id") for q in available_questions]:
        st.session_state.current_question = random.choice(available_questions)
        st.session_state.answered_questions.add(st.session_state.current_question.get("id"))
    
    question = st.session_state.current_question
    st.subheader(question.get("question", "No question available"))
    selected_option = st.radio("🤔 Choose your answer", question.get("options", []), key=f"answer_{question.get('id')}")
    
    if st.button("Submit Answer"):
        if selected_option == question.get("answer"):
            st.success("🎉 Correct!")
            st.balloons()
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect! The correct answer is {question.get('answer')}")
        time.sleep(1)
        st.rerun()

# Page selection
page = st.sidebar.radio("📌 Select Mode", ["🎓 Student Quiz"])
if page == "🎓 Student Quiz":
    student_quiz()
