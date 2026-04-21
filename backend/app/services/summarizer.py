import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    # Join hyphen-broken words across line breaks: "direc-\ntion" -> "direction"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize bullets to sentence separators
    text = text.replace("•", ". ").replace("●", ". ").replace("▪", ". ")

    # Convert newlines to spaces (we’ll re-split into sentences later)
    text = re.sub(r"\n+", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_sentences(text: str) -> List[str]:
    # Basic sentence split
    raw = re.split(r"(?<=[.!?])\s+", text)
    sents = []

    for s in raw:
        s = re.sub(r"\s+", " ", s).strip(" -")
        if not s:
            continue

        # Break very long run-on sentences on semicolon/colon when helpful
        if len(s) > 260:
            parts = re.split(r"(?<=[:;])\s+", s)
            for p in parts:
                p = p.strip()
                if p:
                    sents.append(p)
        else:
            sents.append(s)

    return sents


def _is_noisy_sentence(s: str) -> bool:
    s = s.strip()
    if len(s) < 40:
        return True

    words = s.split()
    if len(words) < 6:
        return True

    # Too many symbols / low alpha ratio => likely extraction junk
    alpha = sum(ch.isalpha() for ch in s)
    if alpha / max(len(s), 1) < 0.55:
        return True

    # Many one-char tokens => broken OCR/PDF extraction
    one_char = sum(1 for w in words if len(w) == 1)
    if one_char / max(len(words), 1) > 0.35:
        return True

    # Repetitive token noise
    low = s.lower()
    if re.search(r"\b(\w+)\s+\1\s+\1\b", low):
        return True

    return False


def _token_set(sentence: str) -> set:
    return set(re.findall(r"[a-zA-Z]{3,}", sentence.lower()))


def _too_similar(a: str, b: str, threshold: float = 0.75) -> bool:
    ta, tb = _token_set(a), _token_set(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(len(ta | tb), 1)
    return overlap >= threshold


def summarize_text(text: str, max_sentences: int = 4) -> str:
    """
    Generic extractive summarizer:
    - No domain/topic hardcoding
    - PDF-noise tolerant
    - TF-IDF scoring + diversity filtering
    """
    if not text or not text.strip():
        return "No content available for summarization."

    normalized = _normalize_text(text)
    sentences = _split_sentences(normalized)
    candidates = [s for s in sentences if not _is_noisy_sentence(s)]

    if not candidates:
        # fallback: least-bad long sentences from original split
        fallback = [s for s in sentences if len(s) > 35][:max_sentences]
        return " ".join(fallback) if fallback else "Could not generate a clean summary."

    if len(candidates) <= max_sentences:
        return " ".join(candidates)

    # TF-IDF sentence scoring
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    X = vectorizer.fit_transform(candidates)
    scores = X.sum(axis=1).A1

    # Rank high-to-low
    ranked_indices = list(scores.argsort()[::-1])

    selected = []
    for idx in ranked_indices:
        s = candidates[idx]
        # Diversity: skip near-duplicates
        if any(_too_similar(s, already) for already in selected):
            continue
        selected.append(s)
        if len(selected) >= max_sentences:
            break

    # Preserve original document order for readability
    selected_set = set(selected)
    ordered = [s for s in candidates if s in selected_set]

    return " ".join(ordered[:max_sentences])