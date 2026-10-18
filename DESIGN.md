# Design Document — AI Tech Consultant

## 1. Overview

The AI Tech Consultant project contains three connected components designed to assist with customer support, email handling, and meeting-to-project-scope generation.

- **Task 1 — Knowledge Brain:** Retrieves relevant information from the Brilliant Directories help content and provides grounded answers through an API.
- **Task 2 — Inbox Agent:** Classifies customer emails, determines priority and sentiment, identifies cases requiring human review, and prepares reply drafts using Knowledge Brain information.
- **Task 3 — Meeting-to-Scope:** Processes client meeting transcripts, extracts project requirements, estimates effort, and produces scope proposals and change reports.

The components are designed to work together while keeping generated outputs available for human review.

## 2. System Architecture

### Task 1: Knowledge Brain

The Knowledge Brain ingests help-center content, makes it searchable, retrieves relevant information for a question, and returns an answer with supporting sources.

The API is intended to help downstream components answer questions using available documentation rather than relying only on a language model's general knowledge.

If sufficient relevant information cannot be retrieved, the system should indicate that the answer is not adequately grounded instead of presenting unsupported information as fact.

### Task 2: Inbox Agent

The Inbox Agent is implemented in TypeScript. It processes customer emails and assigns a category, priority, sentiment, concise summary, and human-review reasons.

Its workflow is:

1. Read the email subject and body.
2. Classify the email into the supported category vocabulary.
3. Determine priority and sentiment using the implemented rules.
4. Flag billing disputes, security issues, legal concerns, negative sentiment, and high-impact issues for review where applicable.
5. Use the Knowledge Brain API to support grounded reply drafting.
6. Keep generated replies as drafts for human review rather than automatically sending them.

The classification rules are deterministic keyword-based rules. Their limitations include ambiguous wording, overlapping keywords, and language that differs from the tested examples.

### Task 3: Meeting-to-Scope

The Meeting-to-Scope service is implemented in Python. It processes meeting transcripts, extracts requirements, generates structured project scope and effort estimates, and supports follow-up meetings.

Its workflow is:

1. Load and parse the meeting transcript.
2. Identify client requirements while excluding facilitator questions that are not requirements.
3. Generate a draft scope and feature estimates.
4. Use Knowledge Brain information where relevant.
5. Merge follow-up requirements with the previous scope.
6. Record explicitly added or removed features in a change report.
7. Produce proposal and report files for human approval.

Generated estimates are planning aids and should be reviewed against the actual requirements, dependencies, and implementation constraints.

## 3. Component Communication

Task 2 and Task 3 use the Knowledge Brain API to obtain relevant documentation.

The local development services use the following default endpoints:

- Knowledge Brain: `http://127.0.0.1:8000`
- Meeting-to-Scope: `http://127.0.0.1:8001`

The services should be tested independently before testing cross-service workflows. API failures, missing sources, or insufficiently relevant retrieval results should be treated as limitations rather than evidence that an answer is grounded.

## 4. Models and Configuration

The project supports local Ollama models configured in the development environment, including `qwen2.5:3b` and `llama3.2:3b`.

Model availability, output quality, latency, and resource consumption must be measured on the machine used for evaluation. No model-comparison winner is claimed in this document because benchmark results have not yet been recorded.

Configuration values should be supplied through environment variables where appropriate. Secrets and machine-specific environment files must not be committed to version control.

## 5. Reliability and Human Oversight

The system uses several safeguards:

- Source-aware answers from the Knowledge Brain.
- Explicit handling of insufficiently grounded answers.
- Human-review flags for sensitive or high-impact emails.
- Draft-only email replies.
- Human approval of generated project scopes and estimates.
- Tests for classification, retrieval, and scope-merging behavior.

These safeguards reduce risk but do not eliminate incorrect retrieval, classification errors, incomplete requirements, or estimation mistakes.

## 6. Testing and Evaluation

Each component should be tested independently and through integration workflows.

Task 1 tests should cover retrieval relevance, grounded answers, and rejection of unrelated questions. Task 2 tests should cover category assignment, priority, sentiment, review flags, and reply-drafting behavior. Task 3 tests should cover requirement extraction, estimates, follow-up merging, explicit removals, and change-report consistency.

The separate 20-case Task 2 classification holdout currently scores 20 correct predictions out of 20 in the user's latest run. This is a small evaluation set and does not establish equivalent accuracy on unseen production emails.

Live integration results and the local Ollama model comparison must be recorded after those checks have been run.

## 7. Known Limitations

- Keyword-based email classification can fail on ambiguous or unfamiliar wording.
- Retrieval quality depends on the available help content and query relevance.
- Generated replies and scopes can omit context or misinterpret requirements.
- Effort estimates are approximate and require expert review.
- Local model performance depends on hardware, configuration, and prompt design.
- A passing unit-test suite does not by itself prove that every service integration works correctly.
