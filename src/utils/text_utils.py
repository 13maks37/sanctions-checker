import re
from rapidfuzz.fuzz import token_set_ratio
from typing import List


def normalize_company_name(companies: List[str]):
    """
    Normalizes a list of company names by removing parentheses
    and extra spaces.
    """
    normalized = []
    for name in companies:
        name = re.sub(r"\s*\([^()]*\)", "", name).strip()
        name = re.sub(r"\s+", " ", name).strip()
        normalized.append(name)
    return normalized


def is_similar(a: str, b: str, threshold: int = 85):
    """Checks whether strings are similar enough given a given threshold."""
    return token_set_ratio(a.lower(), b.lower()) >= threshold
