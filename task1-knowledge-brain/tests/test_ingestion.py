from app.ingestion import chunk_text


def test_chunk_text_returns_content():
    chunks = chunk_text("This is a short test document.")

    assert len(chunks) == 1
    assert chunks[0] == "This is a short test document."


def test_chunk_text_splits_long_content():
    text = "word " * 1000

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunk_text_handles_empty_content():
    assert chunk_text("") == []
    assert chunk_text("   ") == []