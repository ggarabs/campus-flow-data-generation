import json
import random
from typing import Dict, Any


def load_courses(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


def weighted_random(courses: Dict[str, Any], period: str) -> Dict[str, Any]:
    weights = [
        course["periods"].get(period, 0)
        for course in courses.values()
    ]

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError(f"No courses available for period '{period}'")

    r = random.uniform(0, total_weight)
    cumulative = 0

    for course in courses.values():
        weight = course["periods"].get(period, 0)
        cumulative += weight
        if r <= cumulative:
            return course
