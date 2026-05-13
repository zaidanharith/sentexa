import re
from typing import Optional


SLANG_MAP = {
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "enggak": "tidak",
    "tdk": "tidak",
    "bgt": "banget",
    "bgtt": "banget",
    "dr": "dari",
    "yg": "yang",
    "dgn": "dengan",
    "krn": "karena",
    "udh": "sudah",
    "blm": "belum",
    "sm": "sama",
    "mantul": "mantap",
    "kereeen": "keren",
    "jelekkk": "jelek",
    "buruukk": "buruk",
}


def normalize_slang(text: str, slang_map: dict = None) -> str:
    if slang_map is None:
        slang_map = SLANG_MAP
    
    for slang, formal in slang_map.items():
        pattern = r'\b' + re.escape(slang) + r'\b'
        text = re.sub(pattern, formal, text, flags=re.IGNORECASE)
    
    return text


def normalize_repeated_characters(text: str, max_repeats: int = 2) -> str:
    pattern = r'(.)\1{' + str(max_repeats) + ',}'
    return re.sub(pattern, r'\1' * max_repeats, text)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def normalize_case(text: str, lowercase: bool = True) -> str:
    if lowercase:
        return text.lower()
    return text


def normalize_text(
    text: Optional[str],
    lowercase: bool = True,
    normalize_slang_enabled: bool = True,
    normalize_repeats: bool = True,
) -> str:
    if text is None or text == '':
        return ''
    
    if not isinstance(text, str):
        text = str(text)
    
    if lowercase:
        text = normalize_case(text, lowercase=True)
    
    if normalize_slang_enabled:
        text = normalize_slang(text)
    
    if normalize_repeats:
        text = normalize_repeated_characters(text)
    
    text = normalize_whitespace(text)
    
    return text


def normalize_texts(texts: list[str]) -> list[str]:
    return [normalize_text(text) for text in texts]
