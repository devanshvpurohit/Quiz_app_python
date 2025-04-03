import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔥 Fully Hardcoded Google Service Account Credentials
creds_json = {
    "type": "service_account",
    "project_id": "ecell-455715",
    "private_key_id": "abc1234567890xyz",  # 🔹 Replace with actual private_key_id
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0B...\n-----END PRIVATE KEY-----\n",  # 🔹 Replace with actual private_key
    "client_email": "service-account@ecell-455715.iam.gserviceaccount.com",  # 🔹 Replace with actual client_email
    "client_id": "111134701029860426257",  # ✅ Hardcoded Client ID
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account@ecell-455715.iam.gserviceaccount.com"  # ✅ Hardcoded Cert URL
}

# ✅ Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(credentials)

# ✅ Fetch IPL Quiz Questions from Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1csaETbJIYJPW9amvGB9rq0uYEK7sH83Ueq8UUjpp0GU/edit#gid=0"
sheet = client.open_by_url(SHEET_URL).sheet1
df = pd.DataFrame(sheet.get_all_records())

# ✅ Streamlit Quiz App
st.title("🏏 IPL Quiz")

if df.empty:
    st.error("⚠️ No questions found in the Google Sheet!")
else:
    score = 0
    total_questions = len(df)

    for index, row in df.iterrows():
        question = row["Question"]
        options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
        correct_answer = row["Answer"]

        user_answer = st.radio(question, options, key=index)

        if user_answer == correct_answer:
            score += 1

    if st.button("Submit Quiz"):
        st.success(f"✅ Your Score: {score}/{total_questions}")
