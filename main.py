import streamlit as st
import json
import hashlib
from datetime import datetime
import pandas as pd

class QuizAuthApp:
    def __init__(self, 
                 users_path='users.json', 
                 quiz_data_path='quiz_data.json', 
                 leaderboard_path='leaderboard.json'):
        self.users_path = users_path
        self.quiz_data_path = quiz_data_path
        self.leaderboard_path = leaderboard_path
        self.load_users()
        self.load_quiz_data()
        
    def load_users(self):
        with open(self.users_path, 'r') as f:
            self.users_data = json.load(f)
    
    def load_quiz_data(self):
        with open(self.quiz_data_path, 'r') as f:
            self.quiz_data = json.load(f)
    
    def hash_password(self, password):
        """Create a hash of the password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        """Verify user credentials."""
        for user in self.users_data.get('users', []):
            if (user['username'] == username and 
                user['password'] == self.hash_password(password)):
                return True
        return False
    
    def register_user(self, username, password, email):
        """Register a new user."""
        # Check if username already exists
        for user in self.users_data.get('users', []):
            if user['username'] == username:
                return False
        
        # Add new user
        new_user = {
            'username': username,
            'password': self.hash_password(password),
            'email': email
        }
        
        self.users_data['users'].append(new_user)
        
        # Save updated users
        with open(self.users_path, 'w') as f:
            json.dump(self.users_data, f, indent=4)
        
        return True
    
    def load_leaderboard(self):
        """Load leaderboard data."""
        try:
            with open(self.leaderboard_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_leaderboard(self, leaderboard):
        """Save leaderboard data."""
        with open(self.leaderboard_path, 'w') as f:
            json.dump(leaderboard, f, indent=4)
    
    def login_page(self):
        """Login page with registration option."""
        st.title("Quiz App Login")
        
        # Login form
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login"):
                if self.verify_login(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        
        with col2:
            if st.button("Register New Account"):
                st.session_state['registering'] = True
                st.experimental_rerun()
    
    def registration_page(self):
        """User registration page."""
        st.title("Register New Account")
        
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        email = st.text_input("Email Address")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Register"):
                # Validate inputs
                if not new_username or not new_password or not email:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Attempt to register
                    if self.register_user(new_username, new_password, email):
                        st.success("Registration successful! Please log in.")
                        st.session_state['registering'] = False
                        st.experimental_rerun()
                    else:
                        st.error("Username already exists")
        
        with col2:
            if st.button("Back to Login"):
                st.session_state['registering'] = False
                st.experimental_rerun()
    
    def run_quiz(self, username):
        """Quiz implementation."""
        st.title(f"Quiz for {username}")
        
        # Quiz logic
        score = 0
        questions = self.quiz_data['questions']
        
        for i, q in enumerate(questions, 1):
            st.write(f"Question {i}: {q['question']}")
            user_answer = st.radio(
                "Select your answer:", 
                options=q['options'], 
                key=f"q{i}"
            )
            
            if user_answer == q['correct_answer']:
                score += 1
        
        # Submit quiz
        if st.button("Submit Quiz"):
            # Save to leaderboard
            leaderboard = self.load_leaderboard()
            leaderboard.append({
                "name": username,
                "score": score,
                "total_questions": len(questions),
                "timestamp": datetime.now().isoformat()
            })
            
            # Sort leaderboard by score (descending)
            leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
            
            # Save updated leaderboard
            self.save_leaderboard(leaderboard)
            
            # Display results
            st.success(f"Quiz completed! Your score: {score}/{len(questions)}")
            
            # Show leaderboard
            st.header("Leaderboard")
            leaderboard_df = pd.DataFrame(leaderboard)
            st.dataframe(leaderboard_df[['name', 'score', 'total_questions']])
    
    def view_leaderboard(self):
        """View leaderboard without taking the quiz."""
        st.title("Leaderboard")
        leaderboard = self.load_leaderboard()
        leaderboard_df = pd.DataFrame(leaderboard)
        
        if not leaderboard_df.empty:
            st.dataframe(leaderboard_df[['name', 'score', 'total_questions']])
        else:
            st.info("No scores yet!")
    
    def main(self):
        """Main application flow."""
        # Initialize session state
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        
        if 'registering' not in st.session_state:
            st.session_state['registering'] = False
        
        # Navigation
        if not st.session_state['logged_in']:
            if st.session_state['registering']:
                self.registration_page()
            else:
                self.login_page()
        else:
            # Logged-in user menu
            menu = st.sidebar.radio(
                "Menu", 
                ["Take Quiz", "View Leaderboard", "Logout"]
            )
            
            if menu == "Take Quiz":
                self.run_quiz(st.session_state['username'])
            elif menu == "View Leaderboard":
                self.view_leaderboard()
            elif menu == "Logout":
                st.session_state['logged_in'] = False
                st.session_state['username'] = None
                st.experimental_rerun()

def main():
    quiz_app = QuizAuthApp()
    quiz_app.main()

if __name__ == "__main__":
    main()
