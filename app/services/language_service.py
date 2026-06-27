def detect_language(text: str) -> str:
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    total_chars = len(text.replace(" ", ""))

    if total_chars == 0:
        return "en"

    arabic_ratio = arabic_chars / total_chars

    if arabic_ratio > 0.3:
        return "ar"
    return "en"