# Evaluation Report — AI Tech Consultant

## 1. Evaluation Overview

This document records the tests and evaluation results currently available for the three project components. Unit-test results and classification holdout results are reported separately because they measure different things.

## 2. Task 1 — Knowledge Brain

### Evaluation goals

- Retrieve relevant help-center content for user questions.
- Produce answers supported by retrieved sources.
- Avoid presenting unsupported answers as grounded.
- Reject unrelated questions when relevant documentation is unavailable.

### Current verification

The Knowledge Brain health endpoint returned a successful response during local testing. A question about customizing website design returned HTTP 200 with four sources and `grounded: true`.

A broader query about project requirements returned `grounded: false` with no sources during integration testing.

### Remaining work

- Run the complete Task 1 automated test suite in the current working folder.
- Verify relevant and unrelated questions, including source attribution.
- Repeat the integration test with Task 2 and Task 3.
- Record the actual test count and outcomes below after running the tests.

| Measure | Result |
|---|---|
| Health endpoint | Passed in a previous local check |
| Website-design question | HTTP 200; four sources; grounded |
| Broad project-requirements query | Not grounded; no sources |
| Current full test-suite result | Pending re-verification |

## 3. Task 2 — Inbox Agent

### Evaluation goals

- Classify customer emails into the expected categories.
- Assign priority and sentiment.
- Flag sensitive cases for human review.
- Generate useful reply drafts supported by Knowledge Brain information.

### Automated tests

The latest local run completed successfully:

- TypeScript build: passed.
- Automated tests: 16 passed, 0 failed.

### Separate classification holdout

The latest local run of `npm run eval:classification` produced the following result:

| Measure | Result |
|---|---:|
| Holdout size | 20 emails |
| Correct classifications | 20 |
| Incorrect classifications | 0 |
| Accuracy | 100% |

All evaluated examples were classified correctly across the six categories: technical support, account management, billing, sales, feature request, and other.

**Interpretation:** This result applies only to the supplied 20-case holdout. The sample is small and does not establish 100% accuracy on real-world or unseen customer emails.

### Remaining work

- Verify reply drafting with the Knowledge Brain service running.
- Inspect draft quality and source grounding.
- Test API failure and insufficient-retrieval behavior.
- Record the results of end-to-end tests.

## 4. Task 3 — Meeting-to-Scope

### Evaluation goals

- Extract client requirements from meeting transcripts.
- Generate structured scopes and effort estimates.
- Preserve previous scope during follow-up meetings.
- Respect explicit additions and removals.
- Produce consistent change reports and proposals.

### Previous local verification

The latest results available from earlier testing were:

- Python test suite: 3 passed.
- Health endpoint: successful.
- Sample processing: completed for three meetings.
- Knowledge Brain calls: three calls made, but all returned `grounded: false` with no sources.

These results show that sample processing completed, but relevant Knowledge Brain grounding still requires investigation. The earlier three-test result must not be treated as a full test-suite pass.

### Remaining work

- Run the complete Task 3 test suite.
- Verify requirement extraction, estimates, follow-up merging, and explicit removals.
- Inspect generated proposals and change reports.
- Repeat the integration workflow after addressing retrieval issues.

## 5. Model Comparison

The project supports local Ollama models including `qwen2.5:3b` and `llama3.2:3b`.

A comparative benchmark has not yet been run and recorded for this evaluation. No claim is made about which model is better.

Run the project's benchmark script locally if available:

`python scripts/benchmark_ollama.py`

Record actual results for both models, including output quality, latency, and any measured resource or cost figures. Do not enter estimated values as measured results.

## 6. Overall Status

| Area | Current status |
|---|---|
| Task 1 health and sample query | Previously verified; full suite pending |
| Task 2 build and automated tests | Passed: 16/16 |
| Task 2 classification holdout | 20/20 correct |
| Task 2 grounded reply drafting | Pending end-to-end verification |
| Task 3 sample processing | Previously completed; grounding issues remain |
| Task 3 full test suite | Pending re-verification |
| Cross-service integration | Needs re-testing |
| Ollama model comparison | Not yet measured |

## 7. Conclusion

Task 2 has passed its current automated tests and achieved 20/20 correct predictions on its separate classification holdout. Task 1 and Task 3 have demonstrated basic local operation, but retrieval grounding and full-suite verification remain outstanding. End-to-end testing and model benchmarking must be completed before claiming that the entire system is fully verified.