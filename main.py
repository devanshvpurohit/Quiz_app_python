import streamlit as st
import random
import time

# Set the title of the application
st.title("Quiz Application")

# List of quiz questions, each with a question, multiple options, and the correct answer
questions = [
    {
        "question": "What is the capital of Pakistan?",
        "options": ["Karachi", "Lahore", "Islamabad", "Peshawar"],
        "answer": "Islamabad"
    },
    {
        "question": "Which is the national language of Pakistan?",
        "options": ["Punjabi", "Urdu", "Sindhi", "Pashto"],
        "answer": "Urdu"
    },
    {
        "question": "What is the currency of Pakistan?",
        "options": ["Rupee", "Dollar", "Euro", "Dinar"],
        "answer": "Rupee"
    },
    {
        "question": "Who is the founder of Pakistan?",
        "options": ["Allama Iqbal", "Liaquat Ali Khan", "Quaid-e-Azam", "Benazir Bhutto"],
        "answer": "Quaid-e-Azam"
    },
    {
        "question": "Which is the largest province of Pakistan by area?",
        "options": ["Punjab", "Sindh", "Balochistan", "KPK"],
        "answer": "Balochistan"
    }
]

# Initialize session state to store the current question
if "current_question" not in st.session_state:
    st.session_state.current_question = random.choice(questions)  # Select a random question at the start

# Fetch the current question from session state
question = st.session_state.current_question

# Display the question as a subheader
st.subheader(question["question"])

# Create a radio button selection for answer choices
selected_option = st.radio("Choose your answer", question["options"], key="answer")

# When the "Submit Answer" button is clicked
if st.button("Submit Answer"):
    if selected_option == question["answer"]:
        st.success("Correct!")  # Show success message if the answer is correct
        st.balloons()
    else:
        st.error(f"Incorrect! The correct answer is {question['answer']}.")  # Show error message if incorrect

# Wait for 5 seconds before loading the next question
time.sleep(5)

# Select a new random question for the next round
st.session_state.current_question = random.choice(questions)

# Rerun the app to update the displayed question
st.rerun()
