# AI_LOG.md — AI-Assisted Development Log

## AI Tools Used

ChatGPT was used as a coding assistant during the development and debugging of the AI Tech Consultant project.

## Tasks Supported

- **Task 1 — Knowledge Brain:** Assistance with understanding retrieval behavior, checking API responses, and investigating cases where relevant sources were not returned.
- **Task 2 — Inbox Agent:** Assistance with reviewing the TypeScript email classifier, improving category rules, and interpreting evaluation results.
- **Task 3 — Meeting-to-Scope:** Assistance with reviewing transcript processing, project scope generation, effort estimation, and follow-up scope behavior.
- **Documentation and testing:** Assistance with preparing project documentation, running automated tests, interpreting failures, and checking submission readiness.

## Example Development Iteration

The Task 2 classifier initially achieved 14/20 correct predictions (70%) on a separate 20-case classification holdout. After reviewing classification rules and updating the classifier, the result improved to 19/20 (95%). A subsequent adjustment for general “getting started” messages produced 20/20 correct predictions (100%) on that same holdout.

The latest reported Task 2 verification showed that the TypeScript build succeeded and all 16 existing automated tests passed.

## Verification Results Shared During Development

- **Task 1:** 12 automated tests passed in the working folder.
- **Task 2:** 16 automated tests passed; the separate 20-case classification holdout achieved 20/20 correct predictions.
- **Task 3:** 3 automated tests passed in the working folder.

These are the results observed during development, not proof that all assignment requirements or cross-service integrations have been completed. Task 1 and Task 3 grounding, additional test coverage, and end-to-end integration still require verification.

## Human Review and Limitations

AI-generated code and documentation were reviewed and tested by running commands locally and inspecting their outputs. AI suggestions were not treated as verified until supported by actual test or API results. The project still requires review for correctness, security, retrieval quality, and completeness before production use.
