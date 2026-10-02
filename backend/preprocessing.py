import re
from typing import List

from config import settings


# Keep preprocessing dependency-free. Semantic understanding is handled by Gemini.
nlp = True


def get_nlp():
    """Compatibility helper retained for callers; no local NLP model is loaded."""
    return nlp


def normalize_text(text: str) -> str:
    """Clean raw text without loading a local NLP model."""
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def tokenize_and_clean(text: str) -> List[str]:
    """Tokenize text with lightweight regex rules."""
    stop_words = {
        "the", "and", "a", "of", "to", "in", "is", "for", "with", "on",
        "as", "at", "by", "an", "be", "this", "that", "from", "are",
    }
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b", text.lower())
    return [word for word in words if word not in stop_words]


def segment_sentences(text: str) -> List[str]:
    """Split text into sentences using lightweight punctuation rules."""
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]
