# Quiz Application

This is a simple **Quiz Application** built using **Streamlit** and **Python**. The app presents random quiz questions to the user and checks their answers.

## Features
✅ Randomly selects a quiz question
✅ Provides multiple-choice options
✅ Displays whether the answer is correct or incorrect
✅ Loads a new question automatically after submission

## Installation

1. **Clone the Repository**
   ```sh
   git clone https://github.com/Huzaifaabdulrab/Quiz_app_python
   cd quiz-app
   ```

2. **Create a Virtual Environment (Optional but Recommended)**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # For macOS/Linux
   .venv\Scripts\activate    # For Windows
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the application using Streamlit:
```sh
streamlit run main.py
```

## Dependencies
- **Python 3.x**
- **Streamlit**
- **Random** (built-in module)
- **Time** (built-in module)

## How It Works
1. The app selects a random question from a predefined list.
2. The user selects an answer from the provided options.
3. On clicking "Submit Answer":
   - If correct, a success message appears.
   - If incorrect, the correct answer is displayed.
4. After a short delay, a new random question is loaded.

## Contributing
Feel free to fork this repository and contribute by submitting a pull request.

## License
This project is licensed under the **MIT License**.

---
🚀 Built with ❤️ using Python & Streamlit.

