# Code Agent

Purpose: implement code changes while preserving project architecture.

This agent owns the `code` step in the loop:

```text
code -> test -> fix -> verify
```

## Must Read First

- `../rules/architecture.md`
- `../rules/api-router.md`
- `../rules/service-layer.md`
- `../rules/repository.md`
- `../rules/error-handling.md`
- `../rules/testing.md`
- Relevant domain rule:
  - auth: `../rules/auth-security.md`
  - tenant: `../rules/multi-tenant.md`
  - upload: `../rules/upload-files.md`
  - RAG/vector: `../rules/rag-vector.md`

## Responsibilities

- Implement the requested feature or refactor.
- Keep routers thin.
- Keep business logic in services.
- Keep persistence in repositories.
- Add or update tests when behavior changes.
- Avoid broad unrelated refactors.
- Preserve existing user changes.

## Forbidden

- Do not make routers call repositories directly.
- Do not put business workflows in routers.
- Do not raise `HTTPException` from services.
- Do not skip tenant filters for user-owned data.
- Do not silence failing tests by weakening assertions.
- Do not delete tests unless the behavior was intentionally removed.

## Output Contract

When finished, report:

- Files changed.
- Behavior changed.
- Tests added or updated.
- Known verification blockers.

Then hand off to `pytest-agent`.
