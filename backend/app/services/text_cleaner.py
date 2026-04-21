import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r", "\n")

    # Fix hyphenated line breaks: "direc-\ntion" -> "direction"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Join single newlines inside paragraphs, keep paragraph breaks
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove weird bullet leftovers
    text = text.replace("●", " ").replace("•", " ")

    # Remove repeated punctuation spacing
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    return text.strip()