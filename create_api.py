from generate_code import *

def deploy_code(user_prompt):
    code = extract_code(get_api_code(user_prompt))

    with open("main.py", "w") as f:
        f.write(code)
