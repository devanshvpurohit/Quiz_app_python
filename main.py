import streamlit as st
import pandas as pd
import time
import socket
from io import StringIO

# === CONFIG ===
ZOHO_SHEET_CSV_URL = "https://sheet.zohopublic.in/sheet/published/45a1p3273242b4e624babae2470ec234ac962.csv"

# === QUIZ QUESTIONS ===
questions = [
    {
        "question": "Who won the IPL 2023?",
        "options": ["Gujarat Titans", "CSK", "RCB", "MI"],
        "answer": "CSK"
    },
    {
        "question": "Who has the most runs in IPL history?",
        "options": ["Virat Kohli", "Rohit Sharma", "David Warner", "Suresh Raina"],
        "answer": "Virat Kohli"
    },
    {
        "question": "Who took the first hat-trick in IPL?",
        "options": ["Amit Mishra", "Makhaya Ntini", "Lakshmipathy Balaji", "Shane Warne"],
        "answer": "Lakshmipathy Balaji"
    }
]

# === IP Helper ===
def get_ip():
    return socket.gethostbyname(socket.gethostname())

# === Leaderboard Loader ===
@st.cache_data(ttl=60)
def load_leaderboard():
    df = pd.read_csv(ZOHO_SHEET_CSV_URL)
    df = df.sort_values(by="Score", ascending=False).head(10)
    return df

# === Streamlit App ===
st.set_page_config(page_title="IPL Quiz", layout="centered")
st.title("🏏 IPL Quiz App")

menu = st.sidebar.radio("Navigation", ["Take Quiz", "Leaderboard", "Export My Result"])

# === QUIZ PAGE ===
if menu == "Take Quiz":
    name = st.text_input("Enter your full name")
    if name:
        if st.button("Start Quiz"):
            score = 0
            start_time = time.time()

            for idx, q in enumerate(questions):
                st.subheader(f"Q{idx + 1}. {q['question']}")
                answer = st.radio("Your Answer:", q["options"], key=idx)
                if answer == q["answer"]:
                    score += 1

            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            ip = get_ip()

            st.success(f"✅ Score: {score}/{len(questions)}")
            st.info(f"⏱️ Time Taken: {time_taken} sec")

            if "results" not in st.session_state:
                st.session_state.results = []

            if st.button("Save My Result"):
                st.session_state.results.append({
                    "Name": name,
                    "Score": score,
                    "IP": ip,
                    "TimeTaken": time_taken
                })
                st.success("Result saved locally. Go to 'Export My Result' to download it.")

# === LEADERBOARD PAGE ===
elif menu == "Leaderboard":
    st.subheader("🏆 Top 10 Performers")
    try:
        leaderboard = load_leaderboard()
        st.dataframe(leaderboard)
    except Exception as e:
        st.error("Failed to load leaderboard. Please check the sheet URL.")

# === EXPORT RESULTS ===
elif menu == "Export My Result":
    st.subheader("📤 Export Your Score")
    if "results" in st.session_state and st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        csv = df.to_csv(index=False)
        st.download_button("Download Your Result CSV", csv, "my_ipl_quiz_result.csv", "text/csv")
    else:
        st.info("No result found in session. Take the quiz first.")
