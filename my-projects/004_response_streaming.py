from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-6"

#helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

# initially trying out stream
messages = []
add_user_message(messages, "Write a 1 sentence description of a fake database")
stream = client.messages.create(
    model=model,
    max_tokens=1000,
    messages= messages,
    stream=True
)
for event in stream:
    print(event)
####

## better way of using stream through some SDK magic
messages = []
add_user_message(messages, "Write a 1 sentence description of a fake database")

with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=messages
) as stream:
    for text in stream.text_stream:
        #print(text, end="")
        pass 
stream.get_final_message()