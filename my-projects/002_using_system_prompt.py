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

def chat(messages, system=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text

messages = []
system = """
You are an expert in Python coding.
You always give the most concise and to the point solution to every probelm.
We don't care how u might've gotten to the solution as long as it's the right one, so no fluff needed.
Structure and format your response so that it would be easy to copy. 
"""

add_user_message(messages, "Write a Python function that checks a string for duplicate chartacters")
answer = chat(messages, system=system)

answer

"""def has_duplicates(s):
    return len(s) != len(set(s))

print(has_duplicates("hello"))  # True
print(has_duplicates("world"))  # True
print(has_duplicates("abc"))    # False"""