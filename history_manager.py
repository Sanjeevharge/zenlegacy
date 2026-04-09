import json
import os
from datetime import datetime

# -------------------------------------------------------
# This file handles saving and loading the history of
# all APIs the user has ever generated.
# It saves everything into a simple JSON file.
# -------------------------------------------------------

HISTORY_FILE = "api_history.json"


def load_history() -> list:
    """
    Reads the history file and returns a list of past generated APIs.
    If no history file exists yet, returns an empty list.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or unreadable, start fresh
        return []


def save_to_history(prompt: str, code: str) -> None:
    """
    Saves a newly generated API to the history file.
    Each entry has: the user's prompt, the generated code, and the timestamp.
    """
    history = load_history()

    new_entry = {
        "id": len(history) + 1,
        "prompt": prompt,
        "code": code,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),  # e.g. "25 Jan 2025, 03:45 PM"
        "filename": f"api_{len(history) + 1}.py"
    }

    history.append(new_entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def delete_from_history(entry_id: int) -> None:
    """
    Deletes one entry from history by its ID number.
    """
    history = load_history()
    history = [entry for entry in history if entry["id"] != entry_id]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def clear_all_history() -> None:
    """
    Wipes the entire history file clean.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
