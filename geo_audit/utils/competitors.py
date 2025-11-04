"""
Competitor detection and industry-specific competitor lists
"""

from typing import List, Dict, Set


# Industry-specific competitor databases
COMPETITOR_DB = {
    'sunscreen': [
        'Supergoop', 'ColorScience', 'Peter Thomas Roth', 'EltaMD',
        'La Roche-Posay', 'Neutrogena', 'CeraVe', 'Blue Lizard',
        'Coola', 'Sun Bum', 'Black Girl Sunscreen', 'Unseen Sunscreen',
        'Australian Gold', 'Coppertone', 'Banana Boat'
    ],
    'furniture': [
        'Pottery Barn', 'West Elm', 'Arhaus', 'Room & Board',
        'Crate and Barrel', 'CB2', 'Williams Sonoma Home',
        'Ethan Allen', 'Mitchell Gold', 'Four Hands',
        'Design Within Reach', 'Article', 'Joybird', 'Burrow'
    ],
    'skincare': [
        'CeraVe', 'Cetaphil', 'La Roche-Posay', 'Neutrogena',
        'The Ordinary', 'Paula\'s Choice', 'Drunk Elephant',
        'Skinceuticals', 'Sunday Riley', 'Glossier'
    ]
}


# Brand-to-industry mappings
BRAND_INDUSTRY_MAP = {
    'brush on block': 'sunscreen',
    'bob': 'sunscreen',
    'restoration hardware': 'furniture',
    'rh': 'furniture',
    'pottery barn': 'furniture',
    'west elm': 'furniture',
}


def detect_industry(brand_name: str) -> str:
    """
    Detect industry based on brand name

    Args:
        brand_name: Brand name to classify

    Returns:
        Industry name or 'general' if unknown
    """
    brand_lower = brand_name.lower()

    # Check direct mapping
    if brand_lower in BRAND_INDUSTRY_MAP:
        return BRAND_INDUSTRY_MAP[brand_lower]

    # Check if brand name contains industry keywords
    if any(term in brand_lower for term in ['sunscreen', 'spf', 'sun protection']):
        return 'sunscreen'

    if any(term in brand_lower for term in ['furniture', 'home', 'furnishings']):
        return 'furniture'

    if any(term in brand_lower for term in ['skincare', 'skin care', 'beauty']):
        return 'skincare'

    return 'general'


def get_competitors(brand_name: str, industry: str = None) -> List[str]:
    """
    Get competitor list for a brand

    Args:
        brand_name: Brand name
        industry: Industry (auto-detected if not provided)

    Returns:
        List of competitor brands
    """
    if not industry:
        industry = detect_industry(brand_name)

    return COMPETITOR_DB.get(industry, [])


def detect_competitors_mentioned(text: str, competitors: List[str]) -> List[str]:
    """
    Detect which competitors are mentioned in text

    Args:
        text: Text to search
        competitors: List of competitor names

    Returns:
        List of mentioned competitors
    """
    text_lower = text.lower()
    mentioned = []

    for competitor in competitors:
        if competitor.lower() in text_lower:
            mentioned.append(competitor)

    return mentioned


def add_custom_competitor(industry: str, competitor_name: str) -> None:
    """
    Add a custom competitor to an industry

    Args:
        industry: Industry name
        competitor_name: Competitor to add
    """
    if industry not in COMPETITOR_DB:
        COMPETITOR_DB[industry] = []

    if competitor_name not in COMPETITOR_DB[industry]:
        COMPETITOR_DB[industry].append(competitor_name)


def get_all_industries() -> List[str]:
    """
    Get list of all available industries

    Returns:
        List of industry names
    """
    return list(COMPETITOR_DB.keys())
