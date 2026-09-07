import re
import spacy
from typing import List

nlp = None

def get_nlp():
    """
    Lazy loads the SpaCy model, downloading it if not present.
    """
    global nlp
    if nlp is not None:
        return nlp
        
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        import sys
        try:
            print("Downloading spaCy model 'en_core_web_sm'...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Error downloading spaCy model: {e}")
            # Fallback to a dummy object or blank model
            nlp = spacy.blank("en")
    return nlp

def normalize_text(text: str) -> str:
    """
    Cleans raw text by removing duplicate spaces, control characters, and standardizing line breaks.
    """
    if not text:
        return ""
    # Standardize newline characters
    text = text.replace("\r", "\n")
    # Remove control/non-printable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    # Remove excessive empty lines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove duplicate spaces within lines
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def tokenize_and_clean(text: str) -> List[str]:
    """
    Tokenizes text, converts to lowercase, removes stop words and punctuation.
    """
    model = get_nlp()
    doc = model(text.lower())
    tokens = [
        token.lemma_ for token in doc 
        if not token.is_stop and not token.is_punct and token.text.strip()
    ]
    return tokens

def segment_sentences(text: str) -> List[str]:
    """
    Splits text into sentences.
    """
    model = get_nlp()
    doc = model(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
