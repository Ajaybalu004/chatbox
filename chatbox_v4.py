import json
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open ("responses.json","r") as file:
    responses = json.load(file)

questions = list(responses.keys())
print("Loaded questions:", questions)
print("Total count:", len(questions))
answers = list(responses.values())

custom_stopwords = ['what', 'is', 'are', 'you', 'your', 'the', 'a', 'an']
vectorizer = TfidfVectorizer(stop_words=custom_stopwords)
question_vectors = vectorizer.fit_transform(questions)
print("Vocabulary:", vectorizer.get_feature_names_out())

def get_responses(user_input):
    user_vector = vectorizer.transform([user_input])
    print("User vector sum:", user_vector.sum())
    similarities = cosine_similarity(user_vector,question_vectors)
    best_match_index = similarities.argmax()
    best_score = similarities[0][best_match_index]

    print (f"[debug] score: {best_score:.3f}, matched : '{questions[best_match_index]}'")

    if  best_score<0.5:
        return "Sorry , I don't understand that."

    return answers[best_match_index]

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        print("Bot:",get_responses(user_input))