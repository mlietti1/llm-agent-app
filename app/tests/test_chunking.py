from ragapp.chunking import chunk_text


def test_chunk_text_respects_max_chars():
    text = "\n\n".join(["a" * 300] * 5)
    chunks = chunk_text(text, max_chars=700)
    assert all(len(c) <= 700 for c in chunks)
    assert len(chunks) == 3
