from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question about Brilliant Directories",
    )
    top_k: int = Field(default=5, ge=1, le=10)


class Source(BaseModel):
    title: str
    url: str
    excerpt: str = ""
    score: float = Field(default=0.0, ge=0.0, le=1.0)


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source] = Field(default_factory=list)

    # True means relevant source material was retrieved.
    # It is not a guarantee that every generated claim is correct.
    grounded: bool = False


class IngestResponse(BaseModel):
    status: str
    pages_discovered: int
    pages_failed_or_skipped: int
    chunks_indexed: int
    index_path: str
    created_at: str