from anthropic import Anthropic
from dotenv import load_dotenv
from statistics import mean
import json

load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5-20251001"

#helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages, system=None, temperature=1.0):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text

#this is where we tell CLAUDE to create us the prompt evaluation dataset - so going with OPTION 3 in the course to create this prompt 
def generate_dataset():
    prompt="""
Generate an evaluation dataset for a prompt evaluation.
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks.
Generate an array of JSON objects, each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
{
    "task": "Description of task",
},
...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""
    messages = []
    add_user_message(messages, prompt)
    text = chat(messages, system= "Output only the json")
    return text

dataset = generate_dataset()

################################### PARSING JSON ##########################################

#after the dataset has been created we fix it up and parse it as json
clean_dataset = dataset.strip().removeprefix("```json").removesuffix("```").strip()
parsed = json.loads(clean_dataset)

############################# JSON DUMP to NEW FILE #######################################
with open("dataset.json", "w") as f:
    json.dump(parsed, f, indent=2)
###########################################################################################




#defining new functions to help us grade the prompt evaluation dataset

def grade_by_model(test_case, output):
    eval_prompt = f"""
You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON. Keep your response concise and direct.
Example response shape:
{{
    "strengths": string[],
    "weaknesses": string[],
    "reasoning": string,
    "score": number
}}
    """

    messages = []
    add_user_message(messages, eval_prompt)
    eval_text = chat(messages, system="output raw json only as specified in the prompt")
    return eval_text



##### ORIGINAL 3 functions ############
### 3 ###
def run_prompt(test_case):
    """Merges the prompt and test case input, then returns the result"""
    prompt=f"""
Please solve the following task:

{test_case["task"]}
"""
    messages = []
    add_user_message(messages, prompt)
    output = chat(messages)
    return output
### 2 ###
def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)
    
    eval_text = grade_by_model(test_case, output)
    clean_eval = eval_text.strip().removeprefix("```json").removesuffix("```").strip()
    #print(clean_eval)
    try:
        parsed_eval = json.loads(clean_eval)
    except TypeError as e:
        print(f"TYPE: {type(parsed_eval)}")
        print(f"VALUE: {repr(parsed_eval)}")
        raise

    score = parsed_eval["score"]
    reasoning = parsed_eval["reasoning"]

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning,
    }
### 1 ###
def run_eval(parsed):
    """Loads dataset and calls run_test_case with each case"""
    results = []
    for test_case in parsed:
        result = run_test_case(test_case)
        results.append(result)
    average_score = mean([result["score"] for result in results])
    print(f"Average score: {average_score}")
    return results



############################ LOAD the JSON DATASET ############################################

with open("dataset.json", "r") as f:
    dataset = json.load(f)

#################### STARTING the SEQUENCE ####################
results = run_eval(dataset)
# long time to run



################### SEE END RESULT ###################
print(json.dumps(results, indent=2))