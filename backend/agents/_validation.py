def has_required_sections(text: str, required: list[str]) -> bool:
    """Check that required markdown headings are present in output."""
    text_lower = text.lower()
    return all(section.lower() in text_lower for section in required)


RESEARCH_REQUIRED = ["papers", "reading", "gap"]
NOTES_REQUIRED = ["definition", "concept", "summary"]
DOUBT_REQUIRED = ["answer", "explanation", "example"]
