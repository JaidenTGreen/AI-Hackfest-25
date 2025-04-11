import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use API key from .env
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Initial system message to define assistant behavior
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("ChatGPT: Hello! How can I help you today? (type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("ChatGPT: Goodbye!")
        break

    # Add user message to the conversation history
    messages.append({"role": "user", "content": user_input})

    try:
        # Make a chat completion request
        response = client.chat.completions.create(
            model="gpt-4o",  # Or "gpt-3.5-turbo"
            messages=messages
        )

        # Extract the assistant's reply
        reply = response.choices[0].message.content.strip()
        print(f"ChatGPT: {reply}")

        # Add assistant reply to the conversation history
        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print(f"Error: {e}")
