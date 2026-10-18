
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.estimator import estimate_scope
from app.knowledge_client import ask_knowledge_brain
from app.schemas import ScopeRequest
from app.scope_generator import (
    generate_scope,
    render_change_report,
    render_proposal,
)
from app.transcript_parser import parse_transcript

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Meeting-to-Scope",
    description=(
        "Turns meeting transcripts into preliminary project scopes, "
        "engineering estimates, proposals, and change reports."
    ),
    version="1.0.0",
)


class ApprovalRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    approved: bool
    reviewer: str = Field(min_length=1, max_length=200)
    notes: str = Field(default="", max_length=2000)


def process_transcript(
    project_name: str,
    transcript: str,
    previous_scope: dict | None = None,
) -> dict:
    parsed = parse_transcript(transcript)
    requirements = parsed["requirements"]

    # Task 1 is called for every processed transcript.
    knowledge_question = (
        f"Project requirements and documentation question: "
        f"{' '.join(requirements) if requirements else transcript[:1500]}"
    )

    knowledge = ask_knowledge_brain(knowledge_question)

    generation = generate_scope(
        project_name=project_name,
        transcript=parsed["transcript"],
        requirements=requirements,
        knowledge_context=knowledge,
        previous_scope=previous_scope,
    )

    scope = generation["scope"]
    estimate = estimate_scope(scope["features"])

    proposal = render_proposal(
        scope=scope,
        estimate=estimate,
        knowledge_context=knowledge,
    )

    change_report = render_change_report(
        previous_scope=previous_scope,
        current_scope=scope,
        estimate=estimate,
    )

    return {
        "project_name": project_name,
        "meeting_title": parsed["meeting_title"],
        "parsed_requirement_count": parsed["requirement_count"],
        "parsed_requirements": requirements,
        "scope": scope,
        "estimate": estimate,
        "knowledge_context": knowledge,
        "generation_method": generation["generation_method"],
        "model": generation["model"],
        "generation_warning": generation["generation_warning"],
        "proposal_markdown": proposal,
        "change_report_markdown": change_report,
        "requires_human_approval": True,
        "approval_status": "pending",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "meeting-to-scope",
        "version": "1.0.0",
    }


@app.post("/scope")
def create_scope(request: ScopeRequest):
    """Generate a preliminary scope from a submitted transcript."""
    try:
        return process_transcript(
            project_name=request.project_name,
            transcript=request.transcript,
            previous_scope=request.previous_scope,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Scope generation failed: {exc}",
        ) from exc


@app.post("/process-samples")
def process_samples():
    """
    Process the three included sample meetings.
    Meeting 03 is treated as a follow-up to Meeting 01.
    """
    sample_files = [
        ("meeting_01.txt", "Business Website Development"),
        ("meeting_02.txt", "Fitness Studio Booking Platform"),
        ("meeting_03.txt", "Business Website Development - Follow-up"),
    ]

    for filename, _ in sample_files:
        if not (DATA_DIR / filename).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Missing sample transcript: data/{filename}",
            )

    try:
        # Establish the original website scope first.
        first_transcript = (
            DATA_DIR / "meeting_01.txt"
        ).read_text(encoding="utf-8")

        first_result = process_transcript(
            "Business Website Development",
            first_transcript,
        )

        second_transcript = (
            DATA_DIR / "meeting_02.txt"
        ).read_text(encoding="utf-8")

        second_result = process_transcript(
            "Fitness Studio Booking Platform",
            second_transcript,
        )

        # Compare the follow-up against Meeting 01's original scope.
        third_transcript = (
            DATA_DIR / "meeting_03.txt"
        ).read_text(encoding="utf-8")

        third_result = process_transcript(
            "Business Website Development - Follow-up",
            third_transcript,
            previous_scope=first_result["scope"],
        )

        results = [
            first_result,
            second_result,
            third_result,
        ]

        json_path = OUTPUT_DIR / "processed_meetings.json"
        proposal_path = OUTPUT_DIR / "proposals.md"
        change_path = OUTPUT_DIR / "change_report.md"

        json_path.write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        proposal_parts = [
            f"# Proposal {index}: {result['project_name']}\n\n"
            f"{result['proposal_markdown']}"
            for index, result in enumerate(results, start=1)
        ]

        proposal_path.write_text(
            "\n\n---\n\n".join(proposal_parts),
            encoding="utf-8",
        )

        change_path.write_text(
            third_result["change_report_markdown"],
            encoding="utf-8",
        )

        return {
            "status": "success",
            "processed_meetings": len(results),
            "knowledge_brain_calls": len(results),
            "generation_methods": [
                result["generation_method"] for result in results
            ],
            "all_pending_human_approval": all(
                result["approval_status"] == "pending"
                for result in results
            ),
            "outputs": [
                str(json_path),
                str(proposal_path),
                str(change_path),
            ],
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Sample processing failed: {exc}",
        ) from exc


@app.post("/approval")
def record_approval(request: ApprovalRequest):
    """
    Record an explicit reviewer decision.
    Generating a proposal never approves it automatically.
    """
    record = {
        "project_name": request.project_name,
        "approved": request.approved,
        "reviewer": request.reviewer,
        "notes": request.notes,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

    approval_path = OUTPUT_DIR / "approvals.jsonl"

    with approval_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "status": "recorded",
        "approval_status": (
            "approved" if request.approved else "rejected"
        ),
        "record": record,
    }
