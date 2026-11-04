def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    """Split on blank lines, then pack paragraphs into chunks of ~max_chars."""
    chunks, current = [], ""
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if current and len(current) + len(para) + 2 > max_chars:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks
