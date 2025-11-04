"""
Brand keyword generation and detection utilities
"""

from typing import List


def generate_brand_keywords(brand_name: str) -> List[str]:
    """
    Generate search keywords for brand detection

    Args:
        brand_name: The brand name (e.g., "Brush On Block", "Restoration Hardware")

    Returns:
        List of keyword variations for detection
    """
    keywords = [brand_name.lower()]

    # Add version without spaces
    no_spaces = brand_name.lower().replace(' ', '')
    if no_spaces != brand_name.lower():
        keywords.append(no_spaces)

    # Add acronym if multi-word
    words = brand_name.split()
    if len(words) > 1:
        acronym = ''.join([w[0] for w in words]).lower()
        keywords.append(acronym)

    # Add common variations
    # Remove "the" if present
    if brand_name.lower().startswith('the '):
        without_the = brand_name[4:].lower()
        keywords.append(without_the)

    return keywords


def detect_brand_mention(text: str, brand_keywords: List[str]) -> bool:
    """
    Check if text contains any brand keywords

    Args:
        text: Text to search
        brand_keywords: List of brand keyword variations

    Returns:
        True if brand is mentioned
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in brand_keywords)


def extract_mention_context(text: str, brand_keywords: List[str], context_chars: int = 100) -> str:
    """
    Extract context around brand mention

    Args:
        text: Full text
        brand_keywords: List of brand keyword variations
        context_chars: Characters to include before/after mention

    Returns:
        Context string around the mention
    """
    text_lower = text.lower()

    for keyword in brand_keywords:
        if keyword in text_lower:
            pos = text_lower.find(keyword)
            start = max(0, pos - context_chars)
            end = min(len(text), pos + len(keyword) + context_chars)

            context = text[start:end]

            # Add ellipsis if truncated
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."

            return context.strip()

    return ""
