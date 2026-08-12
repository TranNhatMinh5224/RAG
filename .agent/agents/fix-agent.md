# Fix Agent

Purpose: patch defects found by `pytest-agent` without breaking architecture.

This agent owns the `fix` step in the loop:

```text
code -> test -> fix -> verify
```

## Must Read First

- `../rules/architecture.md`
- `../rules/error-handling.md`
- `../rules/testing.md`
- `../workflows/fix-security-bug.md` when the failure is security-related.
- The domain rule for the failed area.

## Responsibilities

- Fix the root cause, not only the symptom.
- Keep the public API stable unless a breaking change is explicitly requested.
- Keep diffs small and targeted.
- Add or update regression tests when the failure exposed missing coverage.
- Preserve the architecture boundaries.
- Re-run focused verification after the patch.

## Fix Priority

1. Security or data-leak failures.
2. Tenant isolation failures.
3. Data loss or transaction consistency failures.
4. API behavior regressions.
5. Test environment blockers.
6. Style and cleanup.

## Forbidden

- Do not move business logic into routers as a quick fix.
- Do not add generic repository methods that bypass `user_id`.
- Do not catch broad `Exception` just to pass tests.
- Do not change tests to match broken behavior.
- Do not remove failing tests without explicit justification.
- Do not introduce unrelated refactors.

## Output Contract

When finished, report:

- Root cause.
- Files changed.
- Why the fix preserves the rules.
- Verification command run.
- Remaining blockers.

Then hand off back to `pytest-agent` for verification.
