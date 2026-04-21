import re

def polish_summary(text: str) -> str:
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove obvious extraction garbage
    garbage_patterns = [
        r"\b\d+\s*fitness\b.*?(?=\.|$)",
        r"\bprobability\s*=\s*[^.]+",
        r"\bnormalize\s*[^.]+",
        r"\bcrossover(?:\s+crossover){1,}\b",
        r"\bstring\s+\d{3,}\b",
        r"\b\d{4,}\b",
    ]
    for p in garbage_patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    # Split into sentences and filter weak fragments
    sents = re.split(r'(?<=[.!?])\s+', text)
    cleaned = []
    for s in sents:
        s = s.strip(" -;,:")
        if not s:
            continue

        words = s.split()
        if len(words) < 6:
            continue

        # Skip sentence fragments starting with conjunctions
        if re.match(r"^(and|or|but|else|then)\b", s, flags=re.IGNORECASE):
            continue

        # Skip if mostly non-letters
        alpha = sum(ch.isalpha() for ch in s)
        if alpha / max(len(s), 1) < 0.6:
            continue

        cleaned.append(s)

    # Keep at most 4 concise sentences
    cleaned = cleaned[:4]

    out = " ".join(cleaned)
    out = re.sub(r"\s+", " ", out).strip()

    if out and out[-1] not in ".!?":
        out += "."
    return out