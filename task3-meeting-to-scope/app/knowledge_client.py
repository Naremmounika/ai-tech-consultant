
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_BRAIN_URL = os.getenv(
    "KNOWLEDGE_BRAIN_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


def ask_knowledge_brain(question: str) -> dict:
    """Retrieve relevant documentation from Task 1."""
    try:
        response = httpx.post(
            f"{KNOWLEDGE_BRAIN_URL}/ask",
            json={
                "question": question[:1900],
                "top_k": 5,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

        sources = result.get("sources", [])

        return {
            "available": True,
            "question": result.get("question", question),
            "answer": result.get("answer", ""),
            "grounded": bool(result.get("grounded", False)),
            "sources": [
                {
                    "title": source.get("title", "Untitled"),
                    "url": source.get("url", ""),
                    "excerpt": source.get("excerpt", ""),
                }
                for source in sources
            ],
            "error": None,
        }

    except (httpx.HTTPError, ValueError) as exc:
        return {
            "available": False,
            "question": question,
            "answer": (
                "Knowledge Brain was unavailable. "
                "Do not treat this as verified documentation."
            ),
            "grounded": False,
            "sources": [],
            "error": str(exc),
        }
