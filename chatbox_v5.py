import filecmp
import json
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def stem_text(text):
    words = text.split()
    return " ".join(stemmer.stem(word) for word in words)


with open("responses.json","r") as file:
    responses = json.load(file)

question = list(responses.keys())
answers = list(responses.values())

stemmed_questions = [stem_text(q) for q in question]

custom_stopwords = ['what','is','you','are','your','the','a','an']
vectorizer = TfidfVectorizer(stop_words=custom_stopwords)
questions_vectors = vectorizer.fit_transform(stemmed_questions)

print("Loaded questions:", question)
print("Vocabulary:",vectorizer.get_feature_names_out())

def get_responses(user_input):
    stemmed_input = stem_text(user_input)
    user_vector = vectorizer.transform([stemmed_input])
    similarity = cosine_similarity(user_vector, questions_vectors)
    best_match_index = similarity.argmax()
    best_score = similarity[0][best_match_index]

    print(f"[debug] score: {best_score:.3f}, matched: '{question[best_match_index]}'")

    if best_score < 0.5:
        return "Sorry, I don't understand that"

    return answers[best_match_index]

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        print("Bot: ", get_responses(user_input))
