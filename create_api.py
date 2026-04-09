import os
import socket
import threading
import subprocess
from generate_code import get_api_code, extract_code
from history_manager import save_to_history

# -------------------------------------------------------
# This file:
# 1. Gets the generated code from the AI
# 2. Saves it to main.py
# 3. Saves it to history
# 4. Runs uvicorn in a background thread (so Streamlit doesn't freeze)
# -------------------------------------------------------

# We keep track of the running uvicorn process so we can stop it later
_uvicorn_process = None


def get_local_ip() -> str:
    """
    Automatically finds the IP address of your machine.
    No more hardcoded IP addresses that only work on someone else's server!
    """
    try:
        # Trick: connect to a public address to find which local IP we use
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # fallback to localhost


def stop_existing_server() -> None:
    """
    Stops the previously running uvicorn server (if any).
    This way deploying a new API doesn't conflict with the old one.
    """
    global _uvicorn_process
    if _uvicorn_process is not None:
        try:
            _uvicorn_process.terminate()
            _uvicorn_process.wait(timeout=3)
        except Exception:
            pass
        _uvicorn_process = None


def start_server_in_background(port: int = 8000) -> None:
    """
    Starts uvicorn in a background thread.

    The old project used os.system() which BLOCKS everything —
    Streamlit would freeze and become unresponsive until uvicorn was killed.

    This version runs uvicorn as a separate subprocess in a thread,
    so Streamlit keeps working normally while your API runs.
    """
    global _uvicorn_process

    def run():
        global _uvicorn_process
        _uvicorn_process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _uvicorn_process.wait()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def deploy_code(user_prompt: str, port: int = 8000) -> dict:
    """
    Full deployment pipeline. Returns a dict with:
    - success (True/False)
    - code (the generated Python code as a string)
    - ip (the local IP address)
    - port
    - error (error message if something went wrong)
    """
    try:
        # Step 1: Ask AI to write the code
        raw_response = get_api_code(user_prompt)

        # Step 2: Clean up the AI's response — keep only Python code
        clean_code = extract_code(raw_response)

        # Step 3: Save the code to main.py on disk
        with open("main.py", "w") as f:
            f.write(clean_code)

        # Step 4: Save this generation to history
        save_to_history(prompt=user_prompt, code=clean_code)

        # Step 5: Stop any old server and start the new one
        stop_existing_server()
        start_server_in_background(port=port)

        # Step 6: Return everything the UI needs to display
        return {
            "success": True,
            "code": clean_code,
            "ip": get_local_ip(),
            "port": port,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "code": None,
            "ip": None,
            "port": port,
            "error": str(e)
        }
