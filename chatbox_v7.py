import json
import os
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

from deep_translator import GoogleTranslator
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

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

def search_realtime(query):
    try:
        results = tavily_client.search(
            query,
            max_results=3,
            search_depth="basic"
        )

        if not results.get('results'):
            return None
        # Trim each result's content to avoid exceeding token limits
        context_parts = []
        for r in results['results']:
            content = r['content'][:500]  # limit each result to 500 characters
            context_parts.append(f"{r['title']}: {content}")
        context = "\n\n".join(context_parts)
        return context
    except Exception as e:
        return None

REALTIME_KEYWORDS = ["latest", "current", "today", "now", "recent", "news", "score", "update", "2026", "this year", "right now"]

def needs_realtime_search(query):
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in REALTIME_KEYWORDS)

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

    if best_score < 0.5:
        # ===== NEW: check if real-time search is needed =====
        if needs_realtime_search(translated_input):
            search_context = search_realtime(translated_input)
            if search_context:
                augmented_input = f"Using this current information:\n{search_context}\n\nAnswer this question: {translated_input}"
            else:
                augmented_input = translated_input
        else:
            augmented_input = translated_input
        # ========================================================

        conversation_history.append({"role": "user", "content": augmented_input})

        # Keep only the system prompt + last 6 messages to avoid token limit issues
        trimmed_history = [conversation_history[0]] + conversation_history[-6:]

        answer = ask_llm(trimmed_history)
        conversation_history.append({"role": "assistant", "content": answer})
    else:
        answer = answers[best_match_index]

    if detected_lang != 'en' and not answer.startswith("Sorry, I couldn't reach"):
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