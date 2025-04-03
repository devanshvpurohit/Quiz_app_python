import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/1csaETbJIYJPW9amvGB9rq0uYEK7sH83Ueq8UUjpp0GU/edit#gid=0"

# Authenticate and fetch data
def fetch_questions():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def main():
    st.title("IPL Quiz")
    
    # Fetch questions from Google Sheet
    df = fetch_questions()
    
    if df.empty:
        st.error("No questions found. Please check the Google Sheet.")
        return
    
    score = 0
    total_questions = len(df)
    
    # Quiz
    for index, row in df.iterrows():
        question = row["Question"]
        options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
        correct_answer = row["Answer"]
        
        user_answer = st.radio(question, options, key=index)
        
        if user_answer == correct_answer:
            score += 1
    
    # Submit button
    if st.button("Submit Quiz"):
        st.write(f"Your Score: {score}/{total_questions}")

if __name__ == "__main__":
    main()
