import re
import nltk
from rake_nltk import Rake

STOP_PHRASES = {
    "chapter", "objectives", "algorithm", "problem", "concept",
}

def _ensure_nltk_data():
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)

def _sent_tokenize_simple(text: str):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def _word_tokenize_simple(sentence: str):
    return re.findall(r"[A-Za-z0-9'-]+", sentence)

def _is_good_phrase(p: str) -> bool:
    words = p.split()
    if len(words) < 1 or len(words) > 5:
        return False
    if any(len(w) == 1 for w in words):
        return False
    low = p.lower().strip()
    if low in STOP_PHRASES:
        return False
    if re.search(r"\d{3,}", low):
        return False
    return True

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    _ensure_nltk_data()

    rake = Rake(
        sentence_tokenizer=_sent_tokenize_simple,
        word_tokenizer=_word_tokenize_simple
    )
    rake.extract_keywords_from_text(text)
    phrases = rake.get_ranked_phrases()

    cleaned = []
    seen = set()

    for p in phrases:
        p = re.sub(r"\s+", " ", p).strip(" -_.,;:!?").strip()
        key = p.lower()

        if not p or key in seen:
            continue
        if not _is_good_phrase(p):
            continue

        seen.add(key)
        cleaned.append(p.title())

        if len(cleaned) >= top_n:
            break

    return cleaned