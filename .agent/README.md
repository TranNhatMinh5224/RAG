# Agent Rules

This folder contains project-specific engineering rules for this RAG application.

Start here:

- `AGENTS.md` - operating guide for AI-assisted development.
- `rules/` - focused coding rules by topic.
- `agents/` - role definitions for code, pytest/bug finding, and fixes.
- `workflows/` - step-by-step workflows for common backend tasks.
- `checklists/` - review checklists before finishing work.
- `CODE_RULES.md` - original long-form rule book.

Default backend standard:

```text
API Router -> Service -> Repository -> Database / External systems
```

Routers stay thin. Services own business logic. Repositories own persistence.

Closed-loop development standard:

```text
code -> find bugs with pytest -> fix root cause -> verify again
```

Use:

- `agents/code-agent.md`
- `agents/pytest-agent.md`
- `agents/fix-agent.md`
- `workflows/closed-loop-development.md`
