responses = {
    "hello": "Hi there!",
    "how are you": "I'm doing well!",
    "your name" : "I am chatbox."
}
print("chatbox started.Type 'bye' to exit.")
while True:
    user_input = input("you: ").lower()

    if user_input == "bye":
        print("Bot: Goodbye!")
        break

    response = responses.get(user_input,"I dont understand")
    print("Bot:",response)