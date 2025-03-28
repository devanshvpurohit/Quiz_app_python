import streamlit as st
import json
from datetime import datetime

class QuizApp:
    def __init__(self, quiz_data_path='quiz_data.json', leaderboard_path='leaderboard.json'):
        self.quiz_data_path = quiz_data_path
        self.leaderboard_path = leaderboard_path
        self.load_quiz_data()
        
    def load_quiz_data(self):
        with open(self.quiz_data_path, 'r') as f:
            self.quiz_data = json.load(f)
        
    def load_leaderboard(self):
        try:
            with open(self.leaderboard_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_leaderboard(self, leaderboard):
        with open(self.leaderboard_path, 'w') as f:
            json.dump(leaderboard, f, indent=4)
    
    def run_quiz(self):
        st.title("Quiz Application")
        
        # User details
        username = st.text_input("Enter your name")
        
        if not username:
            st.warning("Please enter your name to start the quiz")
            return
        
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

def main():
    quiz_app = QuizApp()
    quiz_app.run_quiz()

if __name__ == "__main__":
    main()
