import re
import html
import unicodedata
from typing import Optional


def strip_html(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)


def remove_urls(text: str) -> str:
    return re.sub(r'https?://\S+|www\.\S+', '', text)


def remove_emails(text: str) -> str:
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)


def remove_mentions(text: str) -> str:
    return re.sub(r'@\w+', '', text)


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize('NFKD', text)


def remove_control_characters(text: str) -> str:
    return ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')


def normalize_repeated_characters(text: str, max_repeats: int = 2) -> str:
    pattern = r'(.)\1{' + str(max_repeats) + ',}'
    return re.sub(pattern, r'\1' * max_repeats, text)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def handle_emoji(text: str, remove: bool = False) -> str:
    if not remove:
        return text
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+"
    )
    return emoji_pattern.sub('', text)


def clean_text(
    text: Optional[str],
    lowercase: bool = False,
    remove_emoji: bool = False,
    normalize_repeats: bool = True,
) -> str:
    if text is None or text == '':
        return ''
    
    if not isinstance(text, str):
        text = str(text)
    
    text = strip_html(text)
    text = html.unescape(text)
    text = remove_urls(text)
    text = remove_emails(text)
    text = remove_mentions(text)
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = handle_emoji(text, remove=remove_emoji)
    
    if normalize_repeats:
        text = normalize_repeated_characters(text)
    
    text = normalize_whitespace(text)
    
    if lowercase:
        text = text.lower()
    
    return text


def clean_texts(texts: list[str]) -> list[str]:
    return [clean_text(text) for text in texts]
