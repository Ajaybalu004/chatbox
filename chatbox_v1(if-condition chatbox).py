print ("Hello! I am your personal chatbox.type 'bye' to exit.")

while True:
    user_input = input("you: ").lower()

    if user_input == "hello":
        print("Bot: Hello, I am your personal chatbox")
    elif user_input == "how are you":
        print("Bot: I am fine. how about you?")
    elif user_input == "your name?":
        print("Bot: Hello, I am chatbox")
    elif user_input == "bye":
        print("Bot: Goodbye!")
        break
    else:
        print("Bot: I don't understand that")