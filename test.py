import chatsonic

# Create a Chatsonic instance
chat = chatsonic.Chatsonic()

# Loop to receive user inputs and generate responses
while True:
    user_input = input("You: ")
    response = chat.generate_response(user_input)
    print("Chatsonic:", response)
