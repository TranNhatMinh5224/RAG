# Testing Rules

For pytest-specific behavior, also read `pytest.md`.

Every production-sensitive change needs tests proportional to risk.

Minimum test expectations:

- Service unit tests for business rules.
- Repository tests for tenant-scoped queries.
- API integration tests for HTTP status and response shape.

Required multi-tenant tests:

- User A cannot read User B's conversation.
- User A cannot attach User B's document.
- User A cannot update User B's conversation-document relation.
- User A cannot write chat messages into User B's conversation.
- Vector retrieval includes both `user_id` and allowed document IDs.

For upload:

- Invalid extension rejected.
- Oversized file rejected.
- Path traversal filename sanitized.
- Failed ingestion cleans up file and DB record.

For auth:

- Access token works on protected endpoint.
- Refresh token is rejected on protected endpoint.
- Access token is rejected on refresh endpoint.
- Inactive user is rejected.

Before finishing backend changes, run:

```powershell
python -m compileall src/backend
python -m pytest src/backend/tests -q
```

If pytest is not available, use:

```powershell
python -m unittest discover -s src/backend/tests -p "test_*.py"
```

If tests cannot run because dependencies are missing, report the exact blocker.
