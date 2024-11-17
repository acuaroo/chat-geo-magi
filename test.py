from apis.noaa_apis import magnetic_inclination

def custom_parse_tuple(api_response):
    stripped_response = api_response.strip("()").strip().replace(",", "")
    print(stripped_response)
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

# print(magnetic_inclination("Boulder, CO", ""))

thing = custom_parse_tuple('(TOTINT, "Boulder, CO", now)')
print(thing[0], thing[1:])