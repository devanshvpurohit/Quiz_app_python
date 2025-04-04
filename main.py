import streamlit as st
import pandas as pd
import datetime
import socket
import os

# ---- Hardcoded Questions ----
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["A. Berlin", "B. London", "C. Paris", "D. Madrid"],
        "answer": "C"
    },
    {
        "question": "Which number is a prime?",
        "options": ["A. 4", "B. 6", "C. 9", "D. 7"],
        "answer": "D"
    },
    {
        "question": "Who wrote Hamlet?",
        "options": ["A. Dickens", "B. Tolkien", "C. Shakespeare", "D. Rowling"],
        "answer": "C"
    }
]

# ---- Streamlit UI ----
st.set_page_config(page_title="Quiz App", layout="centered")
st.title("🧠 Real-Time Quiz App")

name = st.text_input("Enter your name to begin:")

if name:
    with st.form("quiz_form"):
        user_answers = []
        for idx, q in enumerate(questions):
            st.subheader(f"Q{idx + 1}: {q['question']}")
            choice = st.radio("Choose one:", q["options"], key=f"q_{idx}")
            user_answers.append(choice[0])  # Save only A/B/C/D

        submitted = st.form_submit_button("Submit")

        if submitted:
            correct_answers = [q["answer"] for q in questions]
            score = sum([ua == ca for ua, ca in zip(user_answers, correct_answers)])
            st.success(f"✅ {name}, your score is {score}/{len(questions)}")

            time_taken = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip_address = st.experimental_user().get("ip", "N/A")  # fallback if local IP fails

            record = {
                "Name": name,
                "Score": score,
                "Answers": str(user_answers),
                "Time": time_taken,
                "IP": ip_address
            }

            # Save record to Excel
            file = "leaderboard.xlsx"
            if os.path.exists(file):
                df = pd.read_excel(file)
                df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            else:
                df = pd.DataFrame([record])
            df.to_excel(file, index=False)

# ---- Leaderboard ----
st.markdown("### 📊 Leaderboard")
if os.path.exists("leaderboard.xlsx"):
    leaderboard = pd.read_excel("leaderboard.xlsx")
    leaderboard_sorted = leaderboard.sort_values(by="Score", ascending=False).reset_index(drop=True)
    st.dataframe(leaderboard_sorted)
else:
    st.info("No submissions yet!")
