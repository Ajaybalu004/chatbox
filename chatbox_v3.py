import json

with open("responses.json") as file:
    responses = json.load(file)

print("chatbox started.Type 'bye' to exit.")

while True:
    user_input = input("you: ").lower()

    if user_input == "bye":
        print("Bot: ", responses["bye"])
        break

    reply = responses.get(user_input,"Sorry, I didn't understand.")

    print("Bot: ", reply)