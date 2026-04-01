#%%
from anthropic import Anthropic
import typing
from dotenv import load_dotenv
import inspect
load_dotenv()

client = Anthropic()

#$$
models = client.models.list()
# once u've found the place, this is how u list it
for model in models.data:
    print(model.id)

#%%
print(dir(client.messages))
# %%
print(inspect.signature(client.messages.stream))

# %%
help(client.messages.stream)
# %%
hints = typing.get_type_hints(client.messages.stream)
print(hints["tools"])

# %%
print(typing.get_args(hints["tools"]))
#%%

print(dir(client.messages))

# %%
