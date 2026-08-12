# Agent Operating Guide

Use this folder as the project-specific operating system for AI-assisted development.

Before editing backend code, read these core rules:

- `rules/architecture.md`
- `rules/error-handling.md`
- `rules/testing.md`

Then read the rule file for the area you are touching:

- API route changes: `rules/api-router.md`
- Service changes: `rules/service-layer.md`
- Repository or SQL changes: `rules/repository.md`
- Auth changes: `rules/auth-security.md`
- Upload or file changes: `rules/upload-files.md`
- RAG or vector changes: `rules/rag-vector.md`
- Tenant/user-owned data changes: `rules/multi-tenant.md`

Use workflows for common tasks:

- Closed loop development: `workflows/closed-loop-development.md`
- Add endpoint: `workflows/add-api-endpoint.md`
- Backend refactor: `workflows/backend-refactor.md`
- Security bug fix: `workflows/fix-security-bug.md`
- Production review: `workflows/production-review.md`

Use agent role guides for closed-loop work:

- Code role: `agents/code-agent.md`
- Test/bug-finding role: `agents/pytest-agent.md`
- Fix role: `agents/fix-agent.md`

Before finishing a backend task, run the review checklist:

- `checklists/backend-change.md`
- `checklists/pytest-review.md` when tests are added or changed.
- `checklists/fix-review.md` when fixing a failing test or bug.

Default backend shape:

```text
API Router -> Service -> Repository -> Database / External systems
```

Main rule: routers stay thin, services own business logic, repositories own persistence.

Default quality loop:

```text
code-agent -> pytest-agent -> fix-agent -> pytest-agent
```

Stop only when compile, focused tests, architecture checks, and documented blockers are complete.
