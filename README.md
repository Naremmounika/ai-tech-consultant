# Fixes Applied in This Review

This is a reviewed copy of the uploaded source. The original ZIP and the user's working folder were not modified.

## Bugs fixed

1. **False-positive retrieval:** Task 1 no longer discards unknown query concepts before computing relevance coverage. Design synonyms still help natural customer wording, while unrelated questions such as a spaceship question are rejected.
2. **Follow-up scope loss:** Task 3 now merges a follow-up draft with the previous scope, retaining existing features unless the transcript explicitly names them for removal. Explicit removals win even if the model repeats the feature.
3. **Missing explicit membership requirement:** When the transcript explicitly requests registration/login for a members-only area, the scope includes a member-account feature and removes a contradictory “customer accounts out of scope” statement.
4. **Facilitator questions:** Common facilitator questions are excluded from candidate requirements, while the client's answer remains available.
5. **Estimate-rule collision:** SEO is checked before generic search terms; multilingual and favorites features have explicit rules.
6. **Unstable change-report ordering:** Added/removed/retained features now preserve scope order, making reports easier to compare.
7. **Missing tests and project hygiene:** Added automated tests (Task 1: 20; Task 2: 25; Task 3: 31), a useful `.gitignore`, safe environment examples, and the required documentation drafts.

## Verification from this review workspace

- Task 1: 20 passed.
- Task 2: TypeScript build succeeded; 25 passed; the separate 20-case category holdout scored 14/20 (70%).
- Task 3: 31 passed.

These results cover unit tests. Live integration must still be re-run on the user's computer with Ollama running and Task 1/Task 3 on ports 8000/8001. The model comparison remains unmeasured until `python scripts/benchmark_ollama.py` is run locally.