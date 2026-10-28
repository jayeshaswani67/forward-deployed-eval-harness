import json
import re
from typing import List, Dict, Any

def check_schema_compliance(output_text: str, expected_schema: Dict[str, Any]) -> bool:
    """Validates if the model output conforms to target JSON structure."""
    if not expected_schema:
        return True
    try:
        data = json.loads(output_text)
        for key in expected_schema.keys():
            if key not in data:
                return False
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def check_keywords(output_text: str, expected: List[str], forbidden: List[str]) -> float:
    """Calculates keyword compliance score between 0.0 and 1.0."""
    text_lower = output_text.lower()
    
    # Severe penalty for forbidden tokens (hallucinations/leaks)
    for bad_word in forbidden:
        if bad_word.lower() in text_lower:
            return 0.0

    if not expected:
        return 1.0

    matches = sum(1 for kw in expected if kw.lower() in text_lower)
    return matches / len(expected)