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
        #"output_config": {"format": {"type": "json_object"}},
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text


messages = []
add_user_message(messages, "Generate a very short event bridge rule as json")
response = chat(messages, system= "Output only json")
print(response)



# """ output_config={
# "format": {
#    "type": "json_schema",
#    "schema": {
#        "type": "object",
#        "additionalProperties": False,
#        "properties": {
#            "result": {"type": "string"}
#        },
#        "required": ["result"]
#        }
#    }
# } """