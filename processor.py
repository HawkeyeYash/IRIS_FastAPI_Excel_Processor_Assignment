import json
import re
import ast
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

# === Setup ===
# This script processes Excel files using the LlamaParse library and provides functions to query the data.
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    result_type="markdown",
    spreadsheet_extract_sub_tables=True
)

# Load the Excel files from the specified directory.
# The SimpleDirectoryReader reads the files and the LlamaParse parser extracts the data.
documents = SimpleDirectoryReader(input_dir="./Data", file_extractor={".xls": parser}).load_data()

# Create a vector store index from the loaded documents.
# The HuggingFaceEmbedding model is used for embedding the documents.
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
index = VectorStoreIndex.from_documents(documents)

# Create a query engine from the index.
# The Groq model is used for generating responses to queries.
llm = Groq(
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

# The query engine is set up with the LLM and the index.
# The Groq model is used for generating responses to queries.
query_engine = index.as_query_engine(llm=llm)

# === Helper functions ===
# This function extracts a JSON object from a string.
def extract_json(text):
    matches = re.findall(r'\{.*?\}', str(text), re.DOTALL)
    for match in reversed(matches):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    return {}

# This function extracts a Python list from a string.
# It uses ast.literal_eval to safely evaluate the string as a Python literal.
def extract_python_list(text):
    try:
        return ast.literal_eval(text.strip())
    except Exception:
        return []
    
# === API functions ===

# List all tables
# This function returns a list of all table names in the document.
def list_tables():
    query = "Just print all the tables names in an array format. Don't include any other text in your response."
    response = query_engine.query(query)
    return {"tables": extract_python_list(str(response))}

# Get table details
# This function returns the names of all rows in a specified table.
def get_table_details(table_name: str):
    query = f"""Return the row names from table "{table_name}" that appear in the first column.
Return only JSON as: {{"row_names": ["Row A", "Row B"]}}."""
    response = query_engine.query(query)
    return {"table_name": table_name, "row_names": extract_json(str(response)).get("row_names", [])}

# Get row sum
# This function sums all numeric values in a specified row of a specified table.
def row_sum(table_name: str, row_name: str):
    query = f"""
In the table named "{table_name}", locate the row titled "{row_name}" and sum all numeric values.
Return only JSON: {{"table_name": "{table_name}", "row_name": "{row_name}", "sum": [SUM_HERE]}}"""
    response = query_engine.query(query)
    return extract_json(str(response))