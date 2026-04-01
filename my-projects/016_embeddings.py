#%%
from dotenv import load_dotenv
import voyageai
import re

load_dotenv()

client = voyageai.Client()

#%%# Chunk by section
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)