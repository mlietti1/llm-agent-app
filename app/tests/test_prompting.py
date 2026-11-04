from ragapp.prompting import build_user_message


def test_build_user_message_includes_source_and_question():
    msg = build_user_message("Who?", [{"source": "a.md", "text": "Hello"}])
    assert "[a.md]" in msg and "Hello" in msg and "Who?" in msg
