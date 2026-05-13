from typing import Iterable, List

DEFAULT_STOPWORDS = {
    "yang",
    "dan",
    "di",
    "ke",
    "dari",
    "ini",
    "itu",
    "untuk",
    "dengan",
    "pada",
    "adalah",
    "atau",
    "sebagai",
    "saya",
    "kamu",
    "dia",
    "kami",
    "kita",
    "oleh",
    "sebagai",
}


def remove_stopwords_tokens(tokens: Iterable[str], use_default_stopwords: bool = True, extra_stopwords: Iterable[str] | None = None) -> List[str]:
    stopwords = set()
    if use_default_stopwords:
        stopwords.update(DEFAULT_STOPWORDS)
    if extra_stopwords:
        stopwords.update({s for s in extra_stopwords})

    filtered: List[str] = []
    for t in tokens:
        if not t:
            continue
        tok = str(t).strip()
        if not tok:
            continue
        if tok.lower() in stopwords:
            continue
        filtered.append(tok)
    return filtered
