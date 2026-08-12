# Fix Review Checklist

Use this checklist after fixing a failing test or bug.

- [ ] Root cause is identified.
- [ ] Fix is in the correct layer.
- [ ] No router repository access was added.
- [ ] No `HTTPException` was added to services.
- [ ] No tenant filter was removed.
- [ ] No broad `except Exception` was added to hide failure.
- [ ] Regression test was added or existing test protects the bug.
- [ ] Focused verification was run.
- [ ] Broader verification was run or blocker was documented.
- [ ] Implementation notes were updated when the bug changed project rules.
