from app.retrieval import search_knowledge, tokenize


def test_tokenize_removes_common_words():
    tokens = tokenize("How do I customize my website colors?")
    assert "customize" in tokens
    assert "colors" in tokens
    assert "how" not in tokens
    assert "website" not in tokens


def test_empty_question_returns_no_results():
    assert search_knowledge("") == []
    assert search_knowledge("   ") == []


def test_unknown_topic_returns_no_results():
    results = search_knowledge(
        "quantum submarine cryptocurrency"
    )
    assert results == []


def test_search_returns_ranked_results():
    results = search_knowledge(
        "how do I customize website colors"
    )

    assert isinstance(results, list)

    if results:
        scores = [item["score"] for item in results]
        assert scores == sorted(scores, reverse=True)


def test_result_limit_is_respected():
    results = search_knowledge(
        "website settings design",
        top_k=2,
    )
    assert len(results) <= 2


def test_result_has_relevance_information():
    results = search_knowledge("website design settings")

    for result in results:
        assert "score" in result
        assert "coverage" in result
        assert isinstance(result["score"], (int, float))
        assert isinstance(result["coverage"], (int, float))


def test_unknown_question_does_not_match_unrelated_content():
    results = search_knowledge(
        "quantum submarine cryptocurrency"
    )
    assert results == []


def test_non_string_question_returns_no_results():
    assert search_knowledge(None) == []
