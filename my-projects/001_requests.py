#import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

#models_list = client.models.list()
# for model in models_list:
#     print(f"Model ID: {model.id}")

client = Anthropic()
model = "claude-sonnet-4-6"

# helper functions to maintain chat history - conversation
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages
    )
    return message.content[0].text

#start python in terminal and run the commands as we go:

#make a starting list
messages = []

#FIRST EXERCISE


#Initial question to the api
add_user_message(messages, "What does ASML represent in the chip manufacturing world? Answer in one sentence")


#now we pass the list of messages into 'chat' to get the answer like before
answer = chat(messages)

#now we take the answer we got from claude and append it in our assitant messages function so that it remembers the AIs resposnes
add_assistant_message(messages, answer)

#let's add now the follow up question
add_user_message(messages, "Write another sentance")


#now let's call the chat function with now a list of all messages
answer = chat(messages)
answer


# SECOND EXERCISE

# creating a user input functionality to mimic talking to Ai in a chat box
while True:
    #get user input directly from the py terminal
    user_input = input("> ")
    #print(">", user_input)

    #we add the user inputs message to the list of messages
    add_user_message(messages, user_input)
    #call the api with the chat funtion
    answer = chat(messages)
    #save the AI's response to the appropriate function for this
    add_assistant_message(messages, answer)
    #print out the response in the terminal
    print(f"---\n{answer}\n---")


# THIRD EXERCISE

