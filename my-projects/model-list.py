from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

models = client.models.list()

for model in models.data:
    print(model.id)