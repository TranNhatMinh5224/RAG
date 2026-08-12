# Implementation Status - 2026-08-12

Started Phase 1 from `PRODUCTION_ROADMAP.md`: Security foundation.

## Completed

- Moved conversation document attach logic into `ChatService`.
- `POST /conversation/{conversation_id}/documents` now verifies conversation ownership before replacing document links.
- `GET /conversation/{conversation_id}` now uses `ChatService` instead of calling repository directly.
- Conversation detail message history is fetched with both `conversation_id` and `current_user.id`.
- `POST /chat` now verifies conversation ownership before reading history, calling RAG, or saving messages.
- Added unit coverage for `ChatService` multi-tenant boundaries in `src/backend/tests/test_chat_service_tenant.py`.

## Verification

- `python -m compileall src/backend` passes.
- `python -m unittest discover -s src/backend/tests -p "test_*.py"` is blocked in the current Python environment because `sqlalchemy` is not installed.

## Next

- Install backend dependencies in the active Python environment and run the unit tests.
- Add API-level integration tests with a real test database.
- Continue Phase 1 with rate limiting and upload MIME/magic-byte validation.

## Architecture Refactor - 2026-08-12

Standardized backend APIs toward the `.agent` rules:

- Added shared domain exceptions in `src/backend/services/exceptions.py`.
- Moved auth business flows into `AuthService`:
  - register
  - login
  - refresh token
  - change password
  - update profile
- Removed direct password verification, token creation, and refresh-token decoding from `auth.py`.
- Removed `HTTPException` from `DocumentService`; upload/delete now raise domain exceptions.
- Injected `RAGChain` into `ChatService` through dependency wiring.
- Removed direct `RAGChain` dependency from `chat.py`.
- Added `StatusResponse` for command-style endpoints.
- Standardized command endpoints to return `{ "status": "success", "message": "..." }`.

Verification:

- `python -m compileall src/backend` passes.
- No `HTTPException` remains in `src/backend/services`.
- No router-level `service.repo`, password verification, token creation, refresh-token decoding, or RAG orchestration patterns remain in `src/backend/api/routers`.
- Unit tests are still blocked in the current Python environment because `sqlalchemy` is not installed.

## Agent Closed Loop Setup - 2026-08-12

Added a three-agent operating model under `.agent/`:

- `code-agent`: implements code while preserving architecture.
- `pytest-agent`: runs compile/tests/architecture checks to find bugs.
- `fix-agent`: fixes root causes without breaking layer rules.

Added supporting rules and workflows:

- `.agent/rules/pytest.md`
- `.agent/rules/fix-policy.md`
- `.agent/workflows/closed-loop-development.md`
- `.agent/checklists/pytest-review.md`
- `.agent/checklists/fix-review.md`

Default loop:

```text
code-agent -> pytest-agent -> fix-agent -> pytest-agent
```
