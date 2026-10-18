import json
import os
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def _fallback_scope(
    project_name: str,
    requirements: list[str],
) -> dict:
    features = []

    for requirement in requirements[:12]:
        words = requirement.split()
        name = " ".join(words[:7]).strip(" .,:;-")

        if not name:
            continue

        features.append({
            "name": name[:100],
            "description": requirement,
            "priority": "medium",
        })

    if not features:
        features.append({
            "name": "Requirements discovery",
            "description": (
                "Review the transcript with the client and confirm "
                "the functional and non-functional requirements."
            ),
            "priority": "high",
        })

    return {
        "project_name": project_name,
        "summary": (
            f"Preliminary scope for {project_name}, based on "
            "the requirements identified in the meeting transcript."
        ),
        "features": features,
        "assumptions": [
            "The client will provide content, branding, and required access.",
            "Third-party services and paid subscriptions are not included "
            "unless explicitly listed.",
            "Effort estimates require technical review before commitment.",
        ],
        "risks": [
            "Unconfirmed requirements may change the effort estimate.",
            "External integrations may depend on third-party access and APIs.",
        ],
        "out_of_scope": [
            "Features not identified in the meeting transcript.",
            "Production deployment and ongoing maintenance unless agreed.",
        ],
        "acceptance_criteria": [
            "The client reviews each listed feature.",
            "Requirements and exclusions are approved before implementation.",
        ],
    }


def _normalize_scope(
    data: dict,
    project_name: str,
    requirements: list[str],
) -> dict:
    fallback = _fallback_scope(project_name, requirements)

    features = data.get("features")
    if not isinstance(features, list) or not features:
        features = fallback["features"]

    clean_features = []

    for feature in features[:12]:
        if not isinstance(feature, dict):
            continue

        name = str(feature.get("name", "")).strip()
        description = str(feature.get("description", "")).strip()

        if not name:
            continue

        priority = str(feature.get("priority", "medium")).lower()
        if priority not in {"low", "medium", "high", "urgent"}:
            priority = "medium"

        clean_features.append({
            "name": name[:120],
            "description": description or name,
            "priority": priority,
        })

    if not clean_features:
        clean_features = fallback["features"]

    def safe_list(key: str) -> list[str]:
        value = data.get(key, fallback[key])

        if not isinstance(value, list):
            return fallback[key]

        return [
            str(item).strip()
            for item in value[:10]
            if str(item).strip()
        ]

    return {
        "project_name": project_name,
        "summary": str(
            data.get("summary", fallback["summary"])
        ).strip(),
        "features": clean_features,
        "assumptions": safe_list("assumptions"),
        "risks": safe_list("risks"),
        "out_of_scope": safe_list("out_of_scope"),
        "acceptance_criteria": safe_list("acceptance_criteria"),
    }



def _ensure_explicit_requirement_features(
    scope: dict,
    requirements: list[str],
) -> dict:
    """Protect explicit high-signal requirements from LLM omissions."""
    result = dict(scope)
    result["features"] = [dict(item) for item in scope.get("features", [])]
    joined = " ".join(requirements).lower()

    member_access_requested = (
        ("members-only" in joined or "members only" in joined)
        and ("register" in joined or "log in" in joined or "login" in joined)
    )
    if member_access_requested:
        existing = " ".join(
            f"{item.get('name', '')} {item.get('description', '')}"
            for item in result["features"]
        ).lower()
        if not any(term in existing for term in ("member accounts", "member login", "members-only area")):
            result["features"].append({
                "name": "Member Accounts and Login",
                "description": (
                    "Customers can register and log in to access a members-only area."
                ),
                "priority": "high",
            })
        result["out_of_scope"] = [
            item for item in result.get("out_of_scope", [])
            if not (
                "account" in str(item).lower()
                and any(word in str(item).lower() for word in ("customer", "member", "user"))
            )
        ]
        criteria = list(result.get("acceptance_criteria", []))
        criteria.append("Customers can register and log in to access the members-only area.")
        result["acceptance_criteria"] = _merge_unique_strings(criteria)
    return result



def _feature_identity(name: str) -> str:
    """Normalize common feature-name variants for follow-up comparisons."""
    key = re.sub(r"\W+", " ", name.lower()).strip()
    tokens = set(key.split())
    if "contact" in tokens and ({"form", "enquiry", "inquiry"} & tokens):
        return "contact form"
    if "directory" in tokens and ({"service", "services"} & tokens):
        return "service directory"
    if "responsive" in tokens or ("mobile" in tokens and ({"design", "friendly"} & tokens)):
        return "responsive design"
    if "admin" in tokens and ({"area", "panel", "management"} & tokens):
        return "admin area"
    if "seo" in tokens or ("search" in tokens and "optimization" in tokens):
        return "seo"
    if "multilingual" in tokens or ({"multi", "language"} <= tokens) or (
        "languages" in tokens and ({"english", "spanish"} & tokens)
    ):
        return "multi-language support"
    if {"favorite", "favorites", "favourite", "favourites"} & tokens:
        return "favorites list"
    return key


def _explicitly_removed_feature(feature: dict, transcript: str) -> bool:
    """Remove an old feature only when a removal clause names that feature."""
    removal_markers = re.compile(
        r"\b(remove|removed|drop|dropped|delete|deleted|exclude|excluded|"
        r"no longer need|don't need|do not need|do not include|don't include|"
        r"postpone|defer|deferred|move to a future phase)\b",
        re.IGNORECASE,
    )
    clauses = re.split(r"(?<=[.!?])\s+|\n+", transcript)
    name = str(feature.get("name", "")).lower()
    name_tokens = {
        token for token in re.findall(r"[a-z0-9]+", name)
        if token not in {"the", "for", "and", "of", "to", "main"}
    }
    identity = _feature_identity(name)

    for clause in clauses:
        if not removal_markers.search(clause):
            continue
        clause_lower = clause.lower()
        clause_tokens = set(re.findall(r"[a-z0-9]+", clause_lower))
        if name and name in clause_lower:
            return True
        if identity == "seo" and "seo" in clause_tokens:
            return True
        if identity == "contact form" and {"contact", "form"} <= clause_tokens:
            return True
        if identity == "responsive design" and ({"responsive", "mobile"} & clause_tokens):
            return True
        if identity == "admin area" and "admin" in clause_tokens:
            return True
        if len(name_tokens) >= 2:
            overlap = name_tokens.intersection(clause_tokens)
            if len(overlap) >= max(2, (len(name_tokens) + 1) // 2):
                return True
    return False


def _merge_unique_strings(*groups: list[str]) -> list[str]:
    merged = []
    seen = set()
    for group in groups:
        for value in group:
            item = str(value).strip()
            key = re.sub(r"\W+", " ", item.lower()).strip()
            if item and key not in seen:
                seen.add(key)
                merged.append(item)
    return merged


def _merge_follow_up_scope(
    previous_scope: dict,
    current_scope: dict,
    transcript: str,
) -> dict:
    """Preserve baseline features unless explicitly removed in the transcript."""
    previous_features = [
        item for item in previous_scope.get("features", [])
        if isinstance(item, dict) and item.get("name")
    ]
    current_features = [
        item for item in current_scope.get("features", [])
        if isinstance(item, dict) and item.get("name")
    ]

    merged_features = []
    identity_to_index = {}
    previous_identities = set()
    removed_identities = set()

    for old_feature in previous_features:
        identity = _feature_identity(str(old_feature["name"]))
        if _explicitly_removed_feature(old_feature, transcript):
            removed_identities.add(identity)
            continue
        previous_identities.add(identity)
        identity_to_index[identity] = len(merged_features)
        merged_features.append(dict(old_feature))

    for new_feature in current_features:
        identity = _feature_identity(str(new_feature["name"]))
        # Do not let a model-generated current feature undo an explicit removal.
        if identity in removed_identities:
            continue
        if identity in identity_to_index:
            index = identity_to_index[identity]
            old_name = merged_features[index].get("name", "")
            merged_features[index] = {
                **merged_features[index],
                **new_feature,
                "name": old_name,
            }
        else:
            identity_to_index[identity] = len(merged_features)
            merged_features.append(dict(new_feature))

    all_feature_text = " ".join(
        f"{item.get('name', '')} {item.get('description', '')}"
        for item in merged_features
    ).lower()
    out_of_scope = _merge_unique_strings(
        previous_scope.get("out_of_scope", []),
        current_scope.get("out_of_scope", []),
    )
    cleaned_out_of_scope = []
    for item in out_of_scope:
        low = item.lower()
        if "account" in low and any(
            word in all_feature_text for word in ("member", "account", "login")
        ):
            continue
        if "payment" in low and "payment" in all_feature_text:
            continue
        cleaned_out_of_scope.append(item)

    for clause in re.split(r"(?<=[.!?])\s+|\n+", transcript):
        low = clause.lower()
        if any(word in low for word in ("postpone", "defer", "future phase")):
            if any(word in low for word in ("blog", "migration", "migrate")):
                cleaned_out_of_scope = _merge_unique_strings(
                    cleaned_out_of_scope,
                    ["Blog migration is deferred to a future phase and excluded from the current estimate."],
                )

    result = dict(current_scope)
    result["features"] = merged_features[:20]
    result["out_of_scope"] = cleaned_out_of_scope[:20]
    result["assumptions"] = _merge_unique_strings(
        previous_scope.get("assumptions", []), current_scope.get("assumptions", [])
    )[:20]
    result["risks"] = _merge_unique_strings(
        previous_scope.get("risks", []), current_scope.get("risks", [])
    )[:20]
    result["acceptance_criteria"] = _merge_unique_strings(
        previous_scope.get("acceptance_criteria", []), current_scope.get("acceptance_criteria", [])
    )[:30]

    additions = [
        item["name"] for item in merged_features
        if _feature_identity(str(item.get("name", ""))) not in previous_identities
    ]
    summary = str(current_scope.get("summary", "")).strip()
    result["summary"] = (
        f"{summary} Existing scoped features are retained unless explicitly removed."
        + (f" Follow-up additions: {', '.join(additions)}." if additions else "")
    )
    return result

def generate_scope(
    project_name: str,
    transcript: str,
    requirements: list[str],
    knowledge_context: dict,
    previous_scope: dict | None = None,
) -> dict:
    """Generate structured scope with Ollama and safe fallback."""
    knowledge_text = json.dumps(
        {
            "grounded": knowledge_context.get("grounded", False),
            "answer": knowledge_context.get("answer", ""),
            "sources": knowledge_context.get("sources", []),
        },
        ensure_ascii=False,
    )

    previous_text = json.dumps(
        previous_scope or {},
        ensure_ascii=False,
    )[:6000]

    prompt = f"""
You are an AI solutions consultant preparing a preliminary
software project scope from meeting notes.

Return ONLY valid JSON with this exact structure:
{{
  "summary": "short project summary",
  "features": [
    {{
      "name": "short feature name",
      "description": "specific requirement grounded in the transcript",
      "priority": "low, medium, or high"
    }}
  ],
  "assumptions": ["assumption"],
  "risks": ["risk"],
  "out_of_scope": ["explicit exclusion or item not yet agreed"],
  "acceptance_criteria": ["testable criterion"]
}}

Rules:
- Use only requirements supported by the transcript.
- Do not invent prices, deadlines, integrations, or commitments.
- Mark uncertainty as an assumption or risk.
- Keep the feature list focused and avoid duplicates.
- Knowledge-base content is reference context, not proof that
  the client requested a feature.
- Do not claim a requirement was documented by Knowledge Brain
  unless the supplied source information supports that claim.
- Interviewer questions are questions, not requirements; use the client's explicit answers.
- If this is a follow-up, return the FULL revised scope, including every previous feature unless the transcript explicitly names it for removal. Do not return only the newly added features.
- Record items explicitly postponed or deferred as out of scope for the current release.
- Leave approval pending.

Project name:
{project_name}

Transcript:
{transcript[:12000]}

Candidate requirements extracted from the transcript:
{json.dumps(requirements, ensure_ascii=False)}

Knowledge Brain context:
{knowledge_text}

Previous scope, if any:
{previous_text}
"""

    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2},
            },
            timeout=120.0,
        )
        response.raise_for_status()

        raw_text = response.json().get("response", "")
        data = json.loads(raw_text)

        if not isinstance(data, dict):
            raise ValueError("Ollama did not return a JSON object.")

        scope = _normalize_scope(
            data,
            project_name,
            requirements,
        )
        scope = _ensure_explicit_requirement_features(scope, requirements)
        if previous_scope:
            scope = _merge_follow_up_scope(
                previous_scope,
                scope,
                transcript,
            )

        return {
            "scope": scope,
            "generation_method": "ollama",
            "model": OLLAMA_MODEL,
            "generation_warning": None,
        }

    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        scope = _fallback_scope(project_name, requirements)
        scope = _ensure_explicit_requirement_features(scope, requirements)
        if previous_scope:
            scope = _merge_follow_up_scope(
                previous_scope,
                scope,
                transcript,
            )

        return {
            "scope": scope,
            "generation_method": "rule_based_fallback",
            "model": None,
            "generation_warning": str(exc),
        }


def render_proposal(
    scope: dict,
    estimate: dict,
    knowledge_context: dict,
) -> str:
    """Render a client-reviewable proposal in Markdown."""
    features = estimate["features"]

    feature_lines = [
        (
            f"- **{item['name']}** — {item['description']} "
            f"(priority: {item['priority']}; "
            f"estimate: {item['estimated_hours']} hours, "
            f"range {item['low_hours']}–{item['high_hours']} hours)"
        )
        for item in features
    ]

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) or "- None listed"

    source_lines = [
        f"- [{source['title']}]({source['url']})"
        if source.get("url")
        else f"- {source['title']}"
        for source in knowledge_context.get("sources", [])
    ]

    if not source_lines:
        source_lines = ["- No relevant Knowledge Brain sources returned."]

    return f"""# Preliminary Project Proposal: {scope['project_name']}

## Project summary
{scope['summary']}

## Proposed scope
{chr(10).join(feature_lines)}

## Effort estimate
- Estimated effort: **{estimate['estimated_hours']} hours**
- Preliminary low–high range: **{estimate['low_hours']}–{estimate['high_hours']} hours**
- Estimate including {estimate['contingency_percent']}% contingency: **{estimate['estimated_hours_with_contingency']} hours**

These are preliminary engineering-effort estimates, not a fixed-price quote or delivery-date commitment.

## Assumptions
{bullets(scope['assumptions'])}

## Risks
{bullets(scope['risks'])}

## Out of scope / not yet agreed
{bullets(scope['out_of_scope'])}

## Acceptance criteria to confirm
{bullets(scope['acceptance_criteria'])}

## Knowledge Brain references
Grounded answer available: **{knowledge_context.get('grounded', False)}**

{chr(10).join(source_lines)}

Knowledge references are supporting documentation only. They do not replace client confirmation.

## Approval
**Status: PENDING HUMAN APPROVAL**

The client and delivery team must validate requirements, estimates, assumptions, exclusions, and acceptance criteria before implementation begins.
"""


def render_change_report(
    previous_scope: dict | None,
    current_scope: dict,
    estimate: dict,
) -> str:
    """Compare feature names and report potential scope changes."""
    if not previous_scope:
        return (
            "# Scope Change Report\n\n"
            "No previous scope was provided. This is a baseline scope, "
            "not a verified change comparison.\n\n"
            "**Approval status: PENDING HUMAN APPROVAL**\n"
        )

    old_features = previous_scope.get("features", [])
    new_features = current_scope.get("features", [])

    def feature_map(items: list) -> dict:
        result = {}

        for item in items:
            if isinstance(item, dict):
                name = str(item.get("name", "")).strip()
            else:
                name = str(item).strip()

            key = re.sub(r"\W+", " ", name.lower()).strip()
            if key:
                result[key] = name

        return result

    old_map = feature_map(old_features)
    new_map = feature_map(new_features)

    added = [name for key, name in new_map.items() if key not in old_map]
    removed = [name for key, name in old_map.items() if key not in new_map]
    retained = [name for key, name in new_map.items() if key in old_map]

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in sorted(items)) or "- None identified"

    return f"""# Scope Change Report

## Summary
This report compares feature names in the previous scope with the current draft.
Name matching is approximate; a human must verify semantic changes.

## Added features
{bullets(added)}

## Potentially removed features
{bullets(removed)}

## Retained features
{bullets(retained)}

## Current estimate
- Estimated effort: **{estimate['estimated_hours']} hours**
- Range: **{estimate['low_hours']}–{estimate['high_hours']} hours**

The previous estimate may not be directly comparable unless it was calculated using the same estimation rules.

## Decision required
Confirm which changes are accepted, deferred, or rejected before updating the approved scope.

**Approval status: PENDING HUMAN APPROVAL**
"""
