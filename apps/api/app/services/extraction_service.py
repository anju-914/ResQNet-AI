import re
import json
import logging
from ..schemas.extraction import ExtractionResult

logger = logging.getLogger(__name__)

# Hindi numeral mappings
HINDI_NUMERALS = {
    '०': 0, '१': 1, '२': 2, '३': 3, '४': 4,
    '५': 5, '६': 6, '७': 7, '८': 8, '९': 9
}

HINDI_WORDS_TO_NUM = {
    'ek': 1, 'do': 2, 'teen': 3, 'tin': 3, 'chaar': 4, 'char': 4, 'paanch': 5, 'panch': 5,
    'chhah': 6, 'chhe': 6, 'saat': 7, 'sat': 7, 'aath': 8, 'ath': 8, 'nau': 9, 'das': 10,
    'gyarah': 11, 'barah': 12, 'bees': 20, 'pachees': 25, 'pachaas': 50, 'sau': 100,
    'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5, 'पाँच': 5, 'छह': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10
}

KNOWN_LANDMARKS = [
    "Yamuna Khadar", "Kashmere Gate", "Sector 62", "Sector 14", "Sector 5", "Mayur Vihar",
    "Laxmi Nagar", "Civil Lines", "Yamuna Bazaar", "Shastri Park", "Akshardham", "Sarita Vihar",
    "Okhla", "ITO", "Narela", "Karol Bagh", "Rohini Sector 3", "Dwarka Sector 10", "Boat Club",
    "यमुना खादर", "कश्मीरी गेट", "सिविल लाइंस", "चांदनी चौक", "रोहिणी", "मयूर विहार", "द्वारका", "यमुना बाजार"
]

SPAM_KEYWORDS = [
    'test', 'testing', 'hello world', 'ignore', 'promo', 'offer', 'win', 'lottery', 'free recharge',
    'trial', 'just checking'
]

def detect_language(text: str) -> str:
    """Detects whether text is Hindi (Devanagari), Hinglish (Roman with Indic keywords), or English."""
    if any('\u0900' <= char <= '\u097F' for char in text):
        return "Hindi"
    
    hinglish_markers = [
        r'\bhai\b', r'\bpaani\b', r'\bchhat\b', r'\blog\b', r'\bmadad\b', r'\bbachao\b',
        r'\bkaro\b', r'\bphasa\b', r'\bfasa\b', r'\bphase\b', r'\bkhana\b', r'\bchahiye\b', r'\bpar\b',
        r'\bme\b', r'\bmein\b', r'\bke\b', r'\bpaas\b', r'\bpass\b', r'\bghar\b', r'\bbhookhe\b',
        r'\bbhookh\b', r'\bbahut\b', r'\bho\b', r'\bgaya\b', r'\brahe\b', r'\braha\b', r'\bkripya\b',
        r'\bdawai\b', r'\bnaale\b', r'\btez\b', r'\bbhej\b'
    ]
    lower = text.lower()
    if any(re.search(marker, lower) for marker in hinglish_markers):
        return "Hinglish"
        
    return "English"

def extract_people_count(text: str) -> int | None:
    """Extracts number of people stranded/affected without confusing package counts or sector IDs."""
    lower = text.lower()
    
    # Check for single person emergency phrases: "an elderly woman", "pregnant woman", "patient", "diabetic patient"
    if re.search(r'\b(an\s+elderly\s+woman|pregnant\s+woman|heart\s+attack\s+patient|diabetic\s+patient|single\s+person)\b', lower):
        return 1

    # Check "family of X"
    fam_match = re.search(r'\bfamily\s+of\s+(\d+)\b', lower)
    if fam_match:
        return int(fam_match.group(1))

    # Pattern: X people / log / workers / passengers / travelers / commuters / bache
    # Examples: "5 log", "12 लोग", "15 workers", "20 stranded commuters", "25 यात्री", "2 elderly people"
    match = re.search(r'(\d+)\s*(?:people|persons|members|log|bache|bachhe|jan|vyakti|workers|laborers|commuters|यात्री|लोग|मरीज|cars?|patients?|elderly\s+people)', lower)
    if match:
        return int(match.group(1))

    # Pattern: "X log chhat par"
    chhat_match = re.search(r'(\d+)\s*log\b', lower)
    if chhat_match:
        return int(chhat_match.group(1))

    # Check Hindi numerals (e.g. ५ लोग)
    for hindi_char, digit in HINDI_NUMERALS.items():
        if re.search(f"{hindi_char}\\s*(?:लोग|व्यक्ति|मरीज|यात्री)?", text):
            return digit

    # Check for spelled-out Hindi/English number before log/bache (skip 'do' if part of 'bhej do' or 'madad do')
    if not re.search(r'\b(?:bhej|kar|madad)\s+do\b', lower):
        word_pattern = r'\b(' + '|'.join(HINDI_WORDS_TO_NUM.keys()) + r')\s*(?:people|log|members|bache|family|families)\b'
        match_word = re.search(word_pattern, lower)
        if match_word:
            word = match_word.group(1)
            if word in HINDI_WORDS_TO_NUM:
                return HINDI_WORDS_TO_NUM[word]

    # Look for standalone digits representing people (ignoring phone numbers, feet, food packets, bungalow numbers)
    cleaned = re.sub(r'\b(?:bungalow\s+number|\d+\s*ft|\d+\s*feet|\d+\s*packets|\d+\s*food|\d+\s*liters)\b', '', lower)
    # Also ignore sector numbers e.g. "sector 62", "sector 5"
    cleaned = re.sub(r'sector\s*\d+', '', cleaned)
    
    match_gen = re.search(r'\b(\d{1,3})\s+(?:trapped|stranded|injured|phase|fasa)\b', cleaned)
    if match_gen:
        return int(match_gen.group(1))

    return None

def extract_need_type(text: str) -> str:
    """Classifies need into standard taxonomy: Rescue, Medical, Food, Water, Shelter."""
    lower = text.lower()
    
    # Priority order: Medical > Water > Food > Rescue
    medical_keywords = ['medical', 'dawai', 'doctor', 'hospital', 'injured', 'ghayal', 'pregnant', 'heart attack', 'dawa', 'ambulance', 'bleeding', 'insulin', 'patient']
    if any(k in lower for k in medical_keywords):
        return "Medical"
        
    water_keywords = ['drinking water', 'peene ka paani', 'water shortage', 'clean water', 'drinking']
    if any(k in lower for k in water_keywords):
        return "Water"

    food_keywords = ['food', 'khana', 'ration', 'bhookhe', 'bhookh', 'hungry', 'meal', 'packet', 'भोजन']
    if any(k in lower for k in food_keywords):
        return "Food"
        
    rescue_keywords = ['rescue', 'bachao', 'chhat', 'trapped', 'phasa', 'fasa', 'phase', 'boat', 'drown', 'water level', 'water rising', 'paani bhar gaya', 'submerged', 'evacuate', 'overflow', 'डूबा', 'नाव']
    if any(k in lower for k in rescue_keywords):
        return "Rescue"
        
    return "Rescue"

def extract_location(text: str) -> str | None:
    """Extracts location string accurately using landmark catalog & regex patterns."""
    lower = text.lower()
    
    # 1. Match known landmarks first (longest match first)
    for lm in sorted(KNOWN_LANDMARKS, key=lambda x: len(x), reverse=True):
        if lm.lower() in lower:
            return lm

    # 2. Check Sector patterns (e.g., "sector 5", "sector 14")
    sec_match = re.search(r'\b(sector\s*\d+[a-zA-Z]?)\b', text, re.IGNORECASE)
    if sec_match:
        return sec_match.group(1).title()

    # 3. Look for named localities ending with Nagar, Vihar, Enclave, Colony, Gate, Bazaar, Chowk
    loc_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Nagar|Vihar|Enclave|Colony|Gate|Bazaar|Chowk|Park|Barrage|Lines))\b', text)
    if loc_match:
        return loc_match.group(1).title()

    # 4. Contextual prepositions: "near X", "at X", "ke paas X"
    prep_match = re.search(r'(?:near|at|in|ke paas|ke pass)\s+([A-Za-z0-9\s]+?)(?:[,\.]|\bneed\b|\bwater\b|\bpaani\b|\bhelp\b|\bfood\b|\bmadad\b|\bemergency\b|$)', text, re.IGNORECASE)
    if prep_match:
        candidate = prep_match.group(1).strip()
        candidate = re.sub(r'^(the|a)\s+', '', candidate, flags=re.IGNORECASE).strip()
        if 3 <= len(candidate) <= 30 and not any(w in candidate.lower() for w in ['boat', 'madad', 'light', 'water', 'doctor', 'help']):
            return candidate.title()

    return None

def calculate_spam_score(text: str) -> float:
    """Evaluates spam/test probability."""
    lower = text.strip().lower()
    if len(lower) < 6:
        return 0.95
    if any(re.search(r'\b' + re.escape(word) + r'\b', lower) for word in SPAM_KEYWORDS):
        return 0.90
    return 0.05

def extract_sos_entities(raw_text: str) -> ExtractionResult:
    """Main entity extraction pipeline with strict JSON and zero-hallucination guarantees."""
    language = detect_language(raw_text)
    need_type = extract_need_type(raw_text)
    people_count = extract_people_count(raw_text)
    location_text = extract_location(raw_text)
    spam_score = calculate_spam_score(raw_text)
    
    confidence = 0.5
    if location_text:
        confidence += 0.25
    if people_count is not None:
        confidence += 0.15
    if need_type:
        confidence += 0.10
    if spam_score > 0.8:
        confidence = 0.2

    confidence = round(min(confidence, 0.98), 2)
    
    return ExtractionResult(
        need_type=need_type,
        people_count=people_count,
        location_text=location_text,
        language=language,
        confidence=confidence,
        spam_score=spam_score
    )

