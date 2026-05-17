# ════════════════════════════════════════════════════════════════
# InnAgent AI — Language Detector
# Detect Sinhala / Tamil / English using Unicode ranges + langdetect
# ════════════════════════════════════════════════════════════════

import re
from langdetect import detect, DetectorFactory

# Make langdetect deterministic
DetectorFactory.seed = 0

# Unicode ranges for Sinhala and Tamil scripts
SINHALA_RANGE = re.compile(r"[\u0D80-\u0DFF]")
TAMIL_RANGE = re.compile(r"[\u0B80-\u0BFF]")


def detect_language(text: str) -> str:
    """
    Detect whether text is Sinhala, Tamil, or English.
    Priority: Unicode script detection first, then langdetect fallback.

    Returns: 'sinhala', 'tamil', or 'english'
    """
    if not text or not text.strip():
        return "english"

    # Count script-specific characters
    sinhala_chars = len(SINHALA_RANGE.findall(text))
    tamil_chars = len(TAMIL_RANGE.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return "english"

    sinhala_ratio = sinhala_chars / total_alpha
    tamil_ratio = tamil_chars / total_alpha

    # If significant portion is Sinhala/Tamil script, classify directly
    if sinhala_ratio > 0.3:
        return "sinhala"
    if tamil_ratio > 0.3:
        return "tamil"

    # Fallback to langdetect for romanized text
    try:
        detected = detect(text)
        lang_map = {
            "si": "sinhala",
            "ta": "tamil",
            "en": "english",
        }
        return lang_map.get(detected, "english")
    except Exception:
        return "english"


def get_language_greeting(language: str) -> str:
    """Get a polite greeting in the detected language."""
    greetings = {
        "english": "Hello! Thank you for reaching out.",
        "sinhala": "ආයුබෝවන්! ඔබගේ පණිවිඩයට ස්තූතියි.",
        "tamil": "வணக்கம்! உங்கள் செய்திக்கு நன்றி.",
    }
    return greetings.get(language, greetings["english"])
