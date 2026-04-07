# PolyU SPEED SEHS4678 Python Learner Support Chatbot

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

A complete Python chatbot for the SEHS4678 AI group project. Supports login, Python quiz, encouragement, and learning chat.

## Features

- **Secure login** with username/password
- **Quiz me** - 3 Python topics (Set, Dictionary, Anonymous Function) with 3 MCQs each
- **Encourage me** - Personalized messages based on quiz score, login count, and mood
- **Chat with me** - Python learning topics with keyword matching
- **Progress tracking** - Login count, quiz attempts, scores
- **External data** - JSON files for users, questions, encouragement, chat KB
- **Offline friendly** - No internet required for demo

## Test Accounts

| Username | Password | Role |
|----------|----------|------|
| Emp001   | Emp001   | Student |
| Emp002   | Emp002   | Student |
| Emp003   | Emp003   | Student |
| SpvrB01  | SpvrB01  | Teacher |
| SpvrB02  | SpvrB02  | Teacher |
| SpvrB03  | SpvrB03  | Teacher |
| SpvrB04  | SpvrB04  | Teacher |
| SpvrB05  | SpvrB05  | Teacher |

## Files

```
edu_chatbot/
├── main.py              # Main chatbot program
├── users.json           # User accounts and progress
├── questions.json       # Quiz questions and answers
├── encouragement.json   # Encouragement messages
├── chat_kb.json         # Chat knowledge base
└── README.md            # This file
```

## Quick Start

```bash
# 1. Clone or download this repo
git clone <your-repo-url>
cd edu_chatbot

# 2. Run the chatbot
python main.py
```

## Demo Test Cases (for presentation)

### Test Case 1: Login success/failure
```
Username: Emp001
Password: Emp001 → Success
Username: Emp001  
Password: wrong → Failure
```

### Test Case 2: Welcome user (back)
```
Login 1st time → "Welcome, Emp001. This is your first login."
Login 2nd time → "Welcome back. This is your login number 2."
```

### Test Case 3: All questions correct
```
Choose quiz → All correct → "Excellent. You answered all questions correctly."
```

## Project Structure

```
main()
├── login()
├── main_menu()
│   ├── run_quiz()
│   ├── encourage_user()
│   └── chat_with_user()
└── save_json()  # Persist user progress
```

## Customization

### Add new users
Edit `users.json`:
```json
"NewUser": {
  "password": "NewUser",
  "display_name": "New Student",
  "login_count": 0,
  "quiz_attempts": 0
}
```

### Add quiz questions
Edit `questions.json` → `Set` array:
```json
{
  "question": "Your question?",
  "options": ["A", "B", "C", "D"],
  "answer_index": 1,
  "explanation": "Explanation text"
}
```

### Add chat topics
Edit `chat_kb.json`:
```json
{
  "keywords": ["loop", "for loop"],
  "answer": "Your explanation here"
}
```

## Presentation Notes

✅ **Meets project brief requirements:**
- Login with test accounts (Emp001, SpvrB01)
- Quiz me → Set/Dictionary/Lambda topics
- Encourage me → Score-based + mood-based
- Chat with me → Python learning topics
- External JSON storage (bonus points)
- Offline demo ready

✅ **Demo-ready test cases:**
1. Login success/failure
2. Welcome back message
3. All-correct quiz result

