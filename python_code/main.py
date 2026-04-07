import json
import os
import random
from datetime import datetime

import nltk
import numpy as np
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.keras import layers, models

stemmer = LancasterStemmer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')
ENCOURAGEMENT_FILE = os.path.join(BASE_DIR, 'encouragement.json')
KB_FILE = os.path.join(BASE_DIR, 'chat_kb.json')
INTENTS_FILE = os.path.join(BASE_DIR, 'intents.json')

BANNER = """
============================================================
PolyU SPEED SEHS4678 (23048495S)
Python Learner Support Chatbot
============================================================
"""

labels = []
words = []
docs_x = []
docs_y = []
data = {}
model = None


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data_obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data_obj, f, indent=2, ensure_ascii=False)


def pause():
    input("\nPress Enter to continue...")


def normalize(text):
    return text.strip().lower()


# ------------------------------
# Tutorial 09 required functions
# ------------------------------
def login(users):
    print(BANNER)
    print("Login required")
    print("Examples: Emp001 / Emp001, SpvrB01 / SpvrB01\n")

    for _ in range(3):
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

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

        print(f"Welcome, {username}!")
        print(f"Display name: {user.get('display_name', username)}")
        if user['login_count'] > 1:
            print(f"Welcome back. This is your login number {user['login_count']}.")
        else:
            print("This is your first login. Good start.")
        if last_login:
            print(f"Your previous login was: {last_login}")
        return username, user

    return None, None


def quiz(user=None, questions=None):
    print("\nQuiz me")

    if questions:
        topics = list(questions.keys())
        print("Quiz topics")
        for i, topic in enumerate(topics, start=1):
            print(f"{i}. {topic}")
        print(f"{len(topics) + 1}. All topics")

        choice = input("Choose a topic: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(topics):
                selected_topics = [topics[choice - 1]]
            elif choice == len(topics) + 1:
                selected_topics = topics
            else:
                print("Invalid choice. Defaulting to all topics.")
                selected_topics = topics
        else:
            print("Invalid choice. Defaulting to all topics.")
            selected_topics = topics

        total = 0
        correct = 0
        topic_scores = {}

        for topic in selected_topics:
            print(f"\n--- Topic: {topic} ---")
            topic_correct = 0
            topic_total = len(questions[topic])
            for q in questions[topic]:
                print(f"\n{q['question']}")
                for i, option in enumerate(q['options'], start=1):
                    print(f"{i}. {option}")

                while True:
                    ans = input("Your answer (1-4): ").strip()
                    if ans in {'1', '2', '3', '4'}:
                        ans = int(ans) - 1
                        break
                    print("Please enter 1, 2, 3, or 4.")

                total += 1
                if ans == q['answer_index']:
                    print("Correct!")
                    correct += 1
                    topic_correct += 1
                else:
                    correct_option = q['options'][q['answer_index']]
                    print(f"Not correct. Answer: {correct_option}")
                    print(f"Explanation: {q['explanation']}")

            topic_scores[topic] = {'correct': topic_correct, 'total': topic_total}

        print("\nQuiz finished.")
        print(f"Score: {correct}/{total}")
        for topic, result in topic_scores.items():
            print(f"- {topic}: {result['correct']}/{result['total']}")

        if correct == total:
            print("Excellent. You answered all questions correctly.")
        elif total > 0 and correct / total >= 0.7:
            print("Good job. You understand most of the ideas.")
        else:
            print("Keep going. Review the explanations and try again.")

        if user is not None:
            user['quiz_attempts'] = user.get('quiz_attempts', 0) + 1
            user['last_score'] = correct
            user['last_total'] = total
            user['topic_scores'] = topic_scores
    else:
        print("Question: Which Python data structure stores key-value pairs?")
        answer = input("Your answer: ").strip().lower()
        if 'dictionary' in answer or answer == 'dict':
            print("Correct! A dictionary stores key-value pairs.")
        else:
            print("Suggested answer: dictionary")


# ---------------------------------
# Tutorial 09 NLP chatbot functions
# ---------------------------------
def read_intent():
    global labels, words, docs_x, docs_y, data

    with open(INTENTS_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    words = [stemmer.stem(w.lower()) for w in words if w != '?']
    words = sorted(list(set(words)))
    labels = sorted(labels)
    return labels, words, docs_x, docs_y, data


def make_BOW(labels, words, docs_x, docs_y):
    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)

    return np.array(training), np.array(output)


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)


def build_and_train_model():
    global model, labels, words, docs_x, docs_y, data

    nltk.download('punkt', quiet=True)
    try:
        nltk.download('punkt_tab', quiet=True)
    except Exception:
        pass

    labels, words, docs_x, docs_y, data = read_intent()
    training, output = make_BOW(labels, words, docs_x, docs_y)

    model = models.Sequential()
    model.add(layers.Input(shape=(len(training[0]),)))
    model.add(layers.Dense(8, activation='relu'))
    model.add(layers.Dense(8, activation='relu'))
    model.add(layers.Dense(len(output[0]), activation='softmax'))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # Tutorial 09 required modification: epochs changed from 10 to 500
    model.fit(training, output, epochs=500, batch_size=8, verbose=1)


def get_response_tag(inp):
    ip = bag_of_words(inp, words)
    ip = np.array(ip).reshape(1, -1)
    results = model.predict(ip, verbose=0)
    results_index = np.argmax(results)
    tag = labels[results_index]
    return tag


def get_response_from_tag(tag):
    for tg in data['intents']:
        if tg['tag'] == tag:
            return random.choice(tg['responses'])
    return 'I am not sure how to answer that.'


def chat():
    print("\nStart talking with the bot!")
    print("Try these inputs for testing: hi, name, hours, goodbye")

    while True:
        inp = input("You: ").strip()
        tag = get_response_tag(inp)
        response = get_response_from_tag(tag)
        print("Bot:", response)

        # Tutorial 09 required modification:
        # stop when the detected intent tag is goodbye
        if tag == 'goodbye':
            print('Chatbot stopped because goodbye intent was detected.')
            break


# -------------------
# Project extra parts
# -------------------
def encouragement_message(user, messages):
    login_count = user.get('login_count', 0)
    last_score = user.get('last_score', 0)
    last_total = user.get('last_total', 0)
    mood = user.get('last_mood', 'neutral')

    ratio = (last_score / last_total) if last_total > 0 else None

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


def chat_with_learning_support(user, kb):
    print("\nPython learning support chat")
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
        print("3. NLP Chatbot")
        print("4. Python learning support chat")
        print("5. View progress")
        print("6. Change password")
        print("7. Logout")
        choice = input("Choose 1-7: ").strip()

        if choice == '1':
            quiz(user, questions)
            save_json(USERS_FILE, users)
            pause()
        elif choice == '2':
            encourage_user(user, messages)
            save_json(USERS_FILE, users)
            pause()
        elif choice == '3':
            chat()
            save_json(USERS_FILE, users)
            pause()
        elif choice == '4':
            chat_with_learning_support(user, kb)
            save_json(USERS_FILE, users)
            pause()
        elif choice == '5':
            show_progress(user)
            pause()
        elif choice == '6':
            new_pw = input('Enter new password: ').strip()
            if new_pw:
                user['password'] = new_pw
                save_json(USERS_FILE, users)
                print('Password updated.')
            else:
                print('Password not changed.')
            pause()
        elif choice == '7':
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

    build_and_train_model()

    username, user = login(users)
    if not user:
        print('Too many failed attempts. Program ends.')
        save_json(USERS_FILE, users)
        return

    save_json(USERS_FILE, users)

    # Tutorial 09 requires login and quiz before chatbot starts.
    # This keeps that requirement visible while preserving the project menu.
    quiz(user, questions)
    save_json(USERS_FILE, users)

    main_menu(username, user, users, questions, messages, kb)


if __name__ == '__main__':
    main()
