from fastapi import FastAPI, HTTPException, Query

from app.config import APP_NAME, APP_VERSION
from app.ingestion import ingest_knowledge_base
from app.llm import generate_answer
from app.retrieval import load_documents, search_knowledge
from app.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    IngestResponse,
    Source,
)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "A local Ollama-powered knowledge service for "
        "Brilliant Directories help-center documentation."
    ),
)


@app.get("/", tags=["General"])
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "message": "Knowledge Brain API is running.",
        "docs": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["General"],
)
def health():
    return HealthResponse(
        status="ok",
        service="knowledge-brain",
        version=APP_VERSION,
    )


@app.get("/index-status", tags=["Knowledge"])
def index_status():
    documents = load_documents()

    return {
        "indexed": bool(documents),
        "chunks_indexed": len(documents),
    }


@app.post(
    "/ingest",
    response_model=IngestResponse,
    tags=["Knowledge"],
)
def ingest():
    try:
        result = ingest_knowledge_base()

        return IngestResponse(
            status="success",
            **result,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Knowledge ingestion failed: {exc}",
        ) from exc


@app.get("/search", tags=["Knowledge"])
def search(
    question: str = Query(min_length=3, max_length=2000),
    top_k: int = Query(default=5, ge=1, le=10),
):
    """Inspect the relevant documents without calling the LLM."""
    matches = search_knowledge(question, top_k=top_k)

    return {
        "question": question,
        "match_count": len(matches),
        "matches": [
            {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "excerpt": item.get("text", "")[:350],
                "score": item.get("score", 0.0),
                "coverage": item.get("coverage", 0.0),
            }
            for item in matches
        ],
    }


@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["Questions"],
)
def ask(request: AskRequest):
    try:
        matches = search_knowledge(
            request.question,
            top_k=request.top_k,
        )

        # Do not call Ollama when there is no relevant evidence.
        answer = generate_answer(
            request.question,
            matches,
        )

        sources = []
        seen_urls = set()

        for match in matches:
            url = match.get("url", "")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            sources.append(
                Source(
                    title=match.get("title", "Untitled"),
                    url=url,
                    excerpt=match.get("text", "")[:350],
                    score=match.get("score", 0.0),
                )
            )

        return AskResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            grounded=bool(matches),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not generate the answer. Check that the "
                "knowledge index is readable and Ollama is running "
                "with the configured model. "
                f"Details: {exc}"
            ),
        ) from exc