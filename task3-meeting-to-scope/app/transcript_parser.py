import re


REQUIREMENT_WORDS = (
    "need", "needs", "want", "wants", "require", "requires",
    "should", "must", "include", "support", "allow", "enable",
    "build", "create", "add", "integrate", "provide",
    "feature", "functionality", "page", "dashboard",
    "booking", "payment", "search", "login", "register",
    "follow-up", "follow up", "change request",
)

SPEAKER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9 _.-]{0,35}:\s*"
)

FACILITATOR_QUESTION_STARTS = (
    "do you need", "do you want", "will you provide", "would you like",
    "should visitors", "should customers", "are these additions",
    "is this required", "do you require", "would you prefer",
)


def clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[-*•]\s*", "", line)
    line = SPEAKER_PATTERN.sub("", line)
    return line.strip()


def parse_transcript(transcript: str) -> dict:
    """Extract meeting title, cleaned text, and candidate requirements."""
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    lines = [
        clean_line(line)
        for line in transcript.splitlines()
        if line.strip()
    ]

    title = "Meeting Transcript"

    for line in lines:
        candidate = line.lstrip("#").strip()
        if candidate.lower().startswith("meeting"):
            title = candidate
            break

    requirements = []

    for line in lines:
        normalized = line.lower().strip()

        if line.startswith("#"):
            continue

        if normalized.endswith("?") and normalized.startswith(
            FACILITATOR_QUESTION_STARTS
        ):
            continue

        if normalized.endswith("?") and normalized.startswith(
            ("do you ", "would you ", "will you ", "are these ", "is this ")
        ):
            continue

        if any(word in normalized for word in REQUIREMENT_WORDS):
            if len(line) >= 12:
                requirements.append(line)

    if not requirements:
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(lines))
        requirements = [
            sentence.strip()
            for sentence in sentences
            if len(sentence.strip()) >= 20
        ]

    unique_requirements = []
    seen = set()

    for requirement in requirements:
        key = re.sub(r"\W+", " ", requirement.lower()).strip()

        if key and key not in seen:
            seen.add(key)
            unique_requirements.append(requirement)

    return {
        "meeting_title": title,
        "transcript": "\n".join(lines),
        "requirements": unique_requirements[:30],
        "requirement_count": len(unique_requirements[:30]),
    }
