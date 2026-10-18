
from app.estimator import estimate_scope
from app.transcript_parser import parse_transcript


def test_parser_extracts_requirements():
    transcript = """
    # Meeting 01: Website
    Client: We need a responsive website.
    Client: Add a contact form for enquiries.
    """

    result = parse_transcript(transcript)

    assert result["requirement_count"] >= 1
    assert any(
        "responsive website" in item.lower()
        for item in result["requirements"]
    )


def test_estimator_returns_positive_effort():
    features = [
        {
            "name": "Member login",
            "description": "Members can register and log in.",
            "priority": "high",
        },
        {
            "name": "Contact form",
            "description": "Collect customer enquiries.",
            "priority": "medium",
        },
    ]

    result = estimate_scope(features)

    assert result["feature_count"] == 2
    assert result["estimated_hours"] > 0
    assert result["low_hours"] <= result["high_hours"]
    assert result["estimated_hours_with_contingency"] >= (
        result["estimated_hours"]
    )


def test_parser_deduplicates_requirements():
    transcript = """
    # Meeting 02: Test
    Client: We need a contact form.
    Client: We need a contact form.
    """

    result = parse_transcript(transcript)

    assert result["requirement_count"] == 1
