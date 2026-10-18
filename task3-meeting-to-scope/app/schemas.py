
from typing import Any

from pydantic import BaseModel, Field


class ScopeRequest(BaseModel):
    project_name: str = Field(
        default="Untitled Project",
        min_length=1,
        max_length=200,
    )
    transcript: str = Field(
        min_length=20,
        max_length=50000,
    )
    previous_scope: dict[str, Any] | None = None
    is_follow_up: bool = False


class Feature(BaseModel):
    name: str
    description: str
    priority: str = "medium"


class Estimate(BaseModel):
    estimated_hours: float
    low_hours: float
    high_hours: float


class ScopeResponse(BaseModel):
    project_name: str
    scope: dict[str, Any]
    estimate: dict[str, Any]
    knowledge_context: dict[str, Any]
    proposal_markdown: str
    change_report_markdown: str
    requires_human_approval: bool = True
    approval_status: str = "pending"
