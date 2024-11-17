colors = {
    "red": ["!!!", "\033[91m"],
    "blue": [">>>", "\033[96m"],
    "green": [">>>", "\033[92m"],
    "normal": [">>>", "\033[0m"],
}

def cprint(message, color="normal"):
    starter = colors[color][0]
    color_code = colors[color][1]

    print(f"{starter} {color_code}{message}\033[0m")
