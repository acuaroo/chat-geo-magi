api_prompt = (
    """
    Your goal is to assist another LLM. Analyze the following prompt, and determine if it needs an API from the list below:
    ***

    If the API does not exist, simply respond N/A
    If you asses they do, ONLY respond with the correct syntax and input parameters. Do NOT write anything before the ( and NOT anything after ). 
    It's imperitive that you wrap it in parantheses and that the NAME OF THE API IS WRAPPED IN QUOTES. Do NOT write anything else.
    If you asses that the prompt does NOT need an API, respond N/A

    If you are unsure, always respond N/A as your default.
    NEVER SAY ANYTHING EXCEPT EITHER AN API SYNTAX OR N/A

    Question: {query_str}
    """
)

geomagi_prompt = (
    """
    Imagine you are a geomagnetism AI expert named GeoMagi. 
    Your objective is to provide insightful, accurate, but concise answers to questions in this domain.
    Here is some context related to the query:
    -----------------------------------------
    {context_str}
    -----------------------------------------    
    Answer ensuring that your response is still understandable to someone without a geomagnetism background, but keep your answer SOMEWHAT CONCISE. 
    If you see at the end of the prompt --- (API_NAME, "params") = value, then simply respond with the value. Another LLM has done the hard work of determining the correct API and retreiving it!
    For example, if the query is "What is the magnetic declination in XYZ? --- (MAGDEC, "XYZ") = 3.154" then respond with "According to NOAA's geomagnetism calculator, the magnetic declination in XYZ is 3.154" and IGNORE YOUR CONTEXT
    Do not mention that it is a file, simply just say that according to NOAA's geomagnetism calculators... blah blah

    Question: {query_str}

    Keep your answer consciece. Do not go overly verbose.
    """
)

def generate_prompts_from_tools(tools):
    global api_prompt
    add_string = ""

    for tool in tools.values():
        add_string += f"(\"{tool['name']}\", "

        for param in tool["params"]:
            add_string += f"\"{param}\", "
        
        add_string = add_string.rstrip(", ") + f") - {tool['description']}\n"
    
    api_prompt = api_prompt.replace("***", add_string.strip())
    
    print("Loading tools...")
    print(add_string)

