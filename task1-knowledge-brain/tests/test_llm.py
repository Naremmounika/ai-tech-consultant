from app.llm import FALLBACK_ANSWER, generate_answer


def test_generate_answer_uses_fallback_without_sources():
    answer = generate_answer(
        "Does the product support a spaceship builder?",
        [],
    )

    assert answer == FALLBACK_ANSWER
    assert "couldn't find sufficiently relevant information" in answer