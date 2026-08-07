import json
import os
import numpy as np
from dotenv import load_dotenv
from groq import Groq

from deep_translator import GoogleTranslator
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

stemmer = PorterStemmer()

def stem_text(text):
    words = text.split()
    return " ".join(stemmer.stem(word) for word in words)

with open("responses.json", "r") as file:
    responses = json.load(file)

question = list(responses.keys())
answers = list(responses.values())

stemmed_questions = [stem_text(q) for q in question]

custom_stopwords = ['what', 'is', 'you', 'are', 'your', 'the', 'a', 'an','who']
vectorizer = TfidfVectorizer(stop_words=custom_stopwords)
question_vectors = vectorizer.fit_transform(stemmed_questions)

def ask_llm(conversation_history):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I couldn't reach the AI service. {e}"

def get_response(user_input, conversation_history):
    try:
        if len(user_input.strip()) > 15:
            detected_lang = detect(user_input)
        else:
            detected_lang = "en"
    except Exception:
        detected_lang = "en"

    translated_input = GoogleTranslator(source='auto', target='en').translate(user_input)

    stemmed_input = stem_text(translated_input)
    user_vector = vectorizer.transform([stemmed_input])
    similarity = cosine_similarity(user_vector, question_vectors)
    best_match_index = np.argmax(similarity)
    best_score = similarity[0][best_match_index]

    if best_score < 0.65:
        conversation_history.append({"role": "user", "content": translated_input})
        answer = ask_llm(conversation_history)
        conversation_history.append({"role": "assistant", "content": answer})
    else:
        answer = answers[best_match_index]

    if detected_lang != 'en':
        answer = GoogleTranslator(source='en', target=detected_lang).translate(answer)

    return answer

if __name__ == "__main__":
    history = [
        {"role": "system", "content": "You are Chatbox AI, a helpful, knowledgeable assistant. Answer clearly and concisely. If you don't know something, say so honestly. Keep a friendly, professional tone."}
    ]
    print("Chatbox AI ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        print("Bot:", get_response(user_input, history))