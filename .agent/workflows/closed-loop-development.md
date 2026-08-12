# Workflow: Closed Loop Development

This workflow keeps the project stable through the full cycle:

```text
code -> find bugs -> fix bugs -> verify -> document
```

Use three agents or three mental roles:

- `agents/code-agent.md`
- `agents/pytest-agent.md`
- `agents/fix-agent.md`

## Step 1: Code Agent

The code agent implements the requested change.

Required output:

- What changed.
- Why it follows architecture rules.
- Tests added or updated.
- Known risky areas.

## Step 2: Pytest Agent

The pytest agent tries to break the change.

Required checks:

- Compile.
- Focused tests.
- Broader tests if possible.
- Architecture grep checks.
- Missing test analysis.

Required output:

- Pass/fail status.
- Failure report.
- Environment blockers.
- Recommended fix target layer.

## Step 3: Fix Agent

The fix agent patches the root cause.

Required behavior:

- Fix the owning layer.
- Keep diff small.
- Add regression test when needed.
- Do not weaken tests.

## Step 4: Verification Loop

After every fix, return to Step 2.

Stop only when:

- Compile passes.
- Focused tests pass.
- Architecture checks pass.
- Broader tests pass, or blockers are documented.

## Step 5: Documentation

Update implementation notes when the change affects architecture, security, or production readiness.

Use:

- `IMPLEMENTATION_STATUS.md`
- Relevant `.agent` rule if the failure revealed a missing rule.

## Closed Loop Exit Criteria

- [ ] Code follows architecture rules.
- [ ] Tests were used to find bugs.
- [ ] Fixes target root causes.
- [ ] No router business logic was introduced.
- [ ] No service `HTTPException` was introduced.
- [ ] No tenant filter was removed.
- [ ] Verification result is documented.
