import json
import random
from typing import Dict, Any

def load_entries(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


def weighted_random_entry(entries: Dict[str, Any]) -> str:
    total_weight = sum(entry["quantity"] for entry in entries.values())

    r = random.random() * total_weight
    cumulative = 0.0

    for entry_name, entry_data in entries.items():
        cumulative += entry_data["quantity"]
        if r <= cumulative:
            return entry_name

    raise RuntimeError("Failed to select a weighted random entry")
