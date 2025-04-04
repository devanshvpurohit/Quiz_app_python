import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import requests

# Page setup
st.set_page_config(page_title="IPL Quiz 2025", page_icon="🏏", layout="centered")
st.title("🏏 IPL Quiz 2025")

# Connect to Google Sheets
conn = st.experimental_connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="Responses", usecols=list(range(8)), ttl=5)
existing_data = existing_data.dropna(how="all")

# IPL Quiz Questions & Answers
QUESTIONS = [
    {
        "question": "Which team won the IPL in 2024?",
        "options": ["Chennai Super Kings", "Mumbai Indians", "Kolkata Knight Riders", "Gujarat Titans"],
        "answer": "Kolkata Knight Riders"
    },
    {
        "question": "Who was the highest run scorer in IPL 2024?",
        "options": ["Virat Kohli", "Shubman Gill", "Jos Buttler", "David Warner"],
        "answer": "Shubman Gill"
    },
    {
        "question": "Who took the most wickets in IPL 2024?",
        "options": ["Jasprit Bumrah", "Yuzvendra Chahal", "Mohammed Shami", "Rashid Khan"],
        "answer": "Mohammed Shami"
    },
    {
        "question": "Which stadium hosted the final match?",
        "options": ["Wankhede", "Narendra Modi Stadium", "Chinnaswamy", "Eden Gardens"],
        "answer": "Narendra Modi Stadium"
    }
]

# Session state init
if "step" not in st.session_state:
    st.session_state.step = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "name" not in st.session_state:
    st.session_state.name = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "ip_address" not in st.session_state:
    try:
        st.session_state.ip_address = requests.get("https://api.ipify.org").text
    except:
        st.session_state.ip_address = "Unavailable"

# Start page
if st.session_state.step == 0:
    name = st.text_input("Enter your full name to start the quiz*")

    if st.button("Start Quiz"):
        if not name.strip():
            st.warning("Please enter your name.")
        elif existing_data["Name"].str.lower().str.strip().eq(name.strip().lower()).any():
            st.error("You have already submitted the quiz.")
        else:
            st.session_state.name = name.strip()
            st.session_state.step = 1
            st.session_state.start_time = time.time()

# Question loop
elif 1 <= st.session_state.step <= len(QUESTIONS):
    q_idx = st.session_state.step - 1
    question = QUESTIONS[q_idx]

    st.subheader(f"Question {st.session_state.step}:")
    answer = st.radio(question["question"], question["options"], index=None)

    if st.button("Next"):
        if answer is None:
            st.warning("Please select an answer.")
        else:
            st.session_state.responses.append(answer)
            st.session_state.step += 1

# Submit results
else:
    end_time = time.time()
    time_taken = round(end_time - st.session_state.start_time, 2)

    score = sum(
        user_ans == q["answer"]
        for user_ans, q in zip(st.session_state.responses, QUESTIONS)
    )

    new_row = pd.DataFrame([{
        "Name": st.session_state.name,
        "Q1": st.session_state.responses[0],
        "Q2": st.session_state.responses[1],
        "Q3": st.session_state.responses[2],
        "Q4": st.session_state.responses[3],
        "Score": score,
        "IP": st.session_state.ip_address,
        "TimeTakenSeconds": time_taken,
    }])

    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
    conn.update(worksheet="Responses", data=updated_df)

    st.success(f"🎉 Quiz Submitted! You scored {score}/4.")
    st.info(f"⏱ Time Taken: {time_taken} seconds")
    st.balloons()

    # Reset session state
    for key in ["step", "responses", "name", "start_time", "ip_address"]:
        del st.session_state[key]
