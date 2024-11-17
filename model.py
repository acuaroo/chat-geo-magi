from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, \
        StorageContext, PromptTemplate, Settings

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent

import chromadb
import os
import prompts
import ast

from printer import cprint
from apis.noaa_apis import magnetic_declination, magnetic_inclination, total_intensity

tools = {
    "magnetic_declination": {
        "name": "MAGDEC",
        "params": ["location_string", "date OR now"],
        "description": "Magnetic declination at a location, at a specific time. If unspecified, set the date to 'now'",
        "fn": magnetic_declination,
    },

    "magnetic_inclination": {
        "name": "MAGINC",
        "params": ["location_string", "date OR now"],
        "description": "Magnetic inclination at a location, at a specific time. If unspecified, set the date to 'now'",
        "fn": magnetic_inclination,
    },

    "total_intensity": {
        "name": "TOTINT",
        "params": ["location_string", "date OR now"],
        "description": "The total strength/intensity of the magnetic field at a location, at a specific time. If unspecified, set the date to 'now'",
        "fn": total_intensity,
    },
}

prompts.generate_prompts_from_tools(tools)

llm = Ollama(model="llama3", request_timeout=300.0)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.llm = llm
Settings.embed_model = embed_model

reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
documents = reader.load_data()

print(f"Index creating with {len(documents)} documents")

chroma_db_dir = "./chroma_db"
existing_db = os.path.exists(chroma_db_dir) and os.listdir(chroma_db_dir)

chroma_client = chromadb.PersistentClient(path=chroma_db_dir)
chroma_collection = chroma_client.get_or_create_collection("llama_vec")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

if existing_db:
    print("Loading existing vector store")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
else:
    print("Creating vector store (this may take a while)")
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model, show_progress=True)

api_template = PromptTemplate(prompts.api_prompt)
api_engine = index.as_query_engine(text_qa_template=api_template, similarity_top_k=3)

geomagi_template = PromptTemplate(prompts.geomagi_prompt)
geomagi_engine = index.as_query_engine(text_qa_template=geomagi_template, similarity_top_k=3)

def custom_parse_tuple(api_response):
    stripped_response = api_response.strip("()").strip().replace(",", "")
    parts = []
    current_part = ""
    in_quotes = False
    
    for char in stripped_response:
        if char == '"' or char == "'":
            in_quotes = not in_quotes
            continue
        elif char == ' ' and not in_quotes:
            if current_part:
                parts.append(current_part)
                current_part = ""
            continue
        current_part += char

    if current_part:
        parts.append(current_part)
    
    parsed_tuple = tuple(part.strip('"').strip("'") for part in parts)
    return parsed_tuple

def parse_api_response(api_response):
    if "N/A" in api_response:
        return geomagi_engine.query(prompt + f" --- N/A, No API was found")
    try:
        parsed_response = custom_parse_tuple(api_response)
        
        if not isinstance(parsed_response, tuple) or len(parsed_response) < 2:
            raise ValueError("api_response is not a valid tuple")
        
        tool_name, tool_args = parsed_response[0], parsed_response[1:]
    except (ValueError, SyntaxError) as e:
        cprint(e, color="red")
        return geomagi_engine.query(prompt + f" --- N/A, No API was found! Mention you don't have the tools to answer the question!")

    tool_used = False
    for tool in tools.values():
        if tool_name == tool["name"]:
            try:
                tool_output = tool["fn"](*tool_args)
                cprint(tool_output, color="green")

                api_response += " = " + tool_output
                tool_used = True

                break
            except Exception as e:
                cprint(e, color="red")
                break
    
    if not tool_used:
        return geomagi_engine.query(prompt + f" --- API failed/is down! Mention this to the user!")
    else:
        return geomagi_engine.query(prompt + f" --- {api_response}")

while (prompt := input(">>> ")) != "q":
    api_response = api_engine.query(prompt)
    api_response = str(api_response)

    geomagi_response = parse_api_response(api_response)

    cprint(api_response, color="green")
    cprint(geomagi_response, color="blue")
    
