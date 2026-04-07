import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')
ENCOURAGEMENT_FILE = os.path.join(BASE_DIR, 'encouragement.json')
KB_FILE = os.path.join(BASE_DIR, 'chat_kb.json')

BANNER = """
============================================================
PolyU SPEED SEHS4678 
Python Learner Support Chatbot
============================================================
"""


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def pause():
    input("\nPress Enter to continue...")


def normalize(text):
    return text.strip().lower()


def login(users):
    print(BANNER)
    print("Login required")
    print("Examples: Emp001 / Emp001, SpvrB01 / SpvrB01\n")

    for _ in range(3):
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        user = users.get(username)
        if not user:
            print("Login failed: username not found.\n")
            continue

        if user['password'] != password:
            print("Login failed: wrong password.\n")
            continue

        user['login_count'] = user.get('login_count', 0) + 1
        last_login = user.get('last_login')
        user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nWelcome, {user['display_name']}!")
        if user['login_count'] > 1:
            print(f"Welcome back. This is your login number {user['login_count']}.")
        else:
            print("This is your first login. Good start.")
        if last_login:
            print(f"Your previous login was: {last_login}")
        return username, user

    return None, None


def choose_topic(questions):
    topics = list(questions.keys())
    print("\nQuiz topics")
    for i, topic in enumerate(topics, start=1):
        print(f"{i}. {topic}")
    print(f"{len(topics)+1}. All topics")

    choice = input("Choose a topic: ").strip()
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(topics):
            return [topics[choice - 1]]
        if choice == len(topics) + 1:
            return topics
    print("Invalid choice. Defaulting to all topics.")
    return topics


def ask_mcq(question):
    print(f"\n{question['question']}")
    for i, option in enumerate(question['options'], start=1):
        print(f"{i}. {option}")

    while True:
        ans = input("Your answer (1-4): ").strip()
        if ans in {'1', '2', '3', '4'}:
            return int(ans) - 1
        print("Please enter 1, 2, 3, or 4.")


def run_quiz(user, questions):
    topics = choose_topic(questions)
    total = 0
    correct = 0
    topic_scores = {}

    print("\nStarting quiz...")
    for topic in topics:
        print(f"\n--- Topic: {topic} ---")
        topic_correct = 0
        topic_total = len(questions[topic])
        for q in questions[topic]:
            total += 1
            selected = ask_mcq(q)
            if selected == q['answer_index']:
                print("Correct!")
                correct += 1
                topic_correct += 1
            else:
                correct_option = q['options'][q['answer_index']]
                print(f"Not correct. Answer: {correct_option}")
                print(f"Explanation: {q['explanation']}")
        topic_scores[topic] = {'correct': topic_correct, 'total': topic_total}

    user['quiz_attempts'] = user.get('quiz_attempts', 0) + 1
    user['last_score'] = correct
    user['last_total'] = total
    user['topic_scores'] = topic_scores

    print("\nQuiz finished.")
    print(f"Score: {correct}/{total}")
    for topic, result in topic_scores.items():
        print(f"- {topic}: {result['correct']}/{result['total']}")

    if correct == total:
        print("Excellent. You answered all questions correctly.")
    elif correct / total >= 0.7:
        print("Good job. You understand most of the ideas.")
    else:
        print("Keep going. Review the explanations and try again.")


def encouragement_message(user, messages):
    login_count = user.get('login_count', 0)
    last_score = user.get('last_score', 0)
    last_total = user.get('last_total', 0)
    mood = user.get('last_mood', 'neutral')

    if last_total > 0:
        ratio = last_score / last_total
    else:
        ratio = None

    if mood == 'stressed':
        return messages['mood_support']['stressed']
    if mood == 'confused':
        return messages['mood_support']['confused']
    if ratio == 1:
        return messages['score_based']['perfect']
    if ratio is not None and ratio >= 0.7:
        return messages['score_based']['good']
    if ratio is not None:
        return messages['score_based']['needs_practice']
    if login_count >= 3:
        return messages['login_based']['consistent']
    return messages['login_based']['new_user']


def encourage_user(user, messages):
    print("\nHow are you feeling today?")
    print("1. okay")
    print("2. confused")
    print("3. stressed")
    choice = input("Choose 1-3, or press Enter to skip: ").strip()
    mood_map = {'1': 'okay', '2': 'confused', '3': 'stressed'}
    if choice in mood_map:
        user['last_mood'] = mood_map[choice]

    print("\nEncouragement")
    print(encouragement_message(user, messages))


def find_kb_answer(question, kb):
    q = normalize(question)
    for item in kb:
        for keyword in item['keywords']:
            if keyword in q:
                return item['answer']
    return None


def chat_with_user(user, kb):
    print("\nChat with me")
    print("Ask about Python topics only. Type 'exit' to return.")
    while True:
        q = input("You: ").strip()
        if normalize(q) in {'exit', 'quit', 'back'}:
            break
        answer = find_kb_answer(q, kb)
        if answer:
            print(f"Bot: {answer}")
        else:
            print("Bot: I can help with Python learning topics such as set, dictionary, lambda, loop, function, class, and OOP.")
        if any(word in normalize(q) for word in ['difficult', 'hard', 'stress', 'confuse', 'worried']):
            user['last_mood'] = 'confused'


def show_progress(user):
    print("\nProgress summary")
    print(f"Login count: {user.get('login_count', 0)}")
    print(f"Quiz attempts: {user.get('quiz_attempts', 0)}")
    if user.get('last_total', 0) > 0:
        print(f"Latest score: {user.get('last_score', 0)}/{user.get('last_total', 0)}")
    else:
        print("Latest score: No quiz attempt yet")


def main_menu(username, user, users, questions, messages, kb):
    while True:
        print("\nMain menu")
        print("1. Quiz me")
        print("2. Encourage me")
        print("3. Chat with me")
        print("4. View progress")
        print("5. Change password")
        print("6. Logout")
        choice = input("Choose 1-6: ").strip()

        if choice == '1':
            run_quiz(user, questions)
            save_json(USERS_FILE, users)
            pause()
        elif choice == '2':
            encourage_user(user, messages)
            save_json(USERS_FILE, users)
            pause()
        elif choice == '3':
            chat_with_user(user, kb)
            save_json(USERS_FILE, users)
        elif choice == '4':
            show_progress(user)
            pause()
        elif choice == '5':
            new_pw = input('Enter new password: ').strip()
            if new_pw:
                user['password'] = new_pw
                save_json(USERS_FILE, users)
                print('Password updated.')
            else:
                print('Password not changed.')
            pause()
        elif choice == '6':
            save_json(USERS_FILE, users)
            print('Logged out. Goodbye.')
            break
        else:
            print('Invalid choice.')


def main():
    users = load_json(USERS_FILE)
    questions = load_json(QUESTIONS_FILE)
    messages = load_json(ENCOURAGEMENT_FILE)
    kb = load_json(KB_FILE)

    username, user = login(users)
    if not user:
        print('Too many failed attempts. Program ends.')
        save_json(USERS_FILE, users)
        return

    save_json(USERS_FILE, users)
    main_menu(username, user, users, questions, messages, kb)


if __name__ == '__main__':
    main()
