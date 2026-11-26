
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "code_patterns.json"

def load_patterns():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Support both dictionary and list formats
    if isinstance(data, dict):
        patterns = data.get("patterns", [])
    else:
        patterns = data

    if not isinstance(patterns, list):
        raise ValueError("Invalid code patterns format")

    return patterns
