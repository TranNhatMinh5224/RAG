# Pytest Rules

Pytest exists to reveal defects, not to decorate the project.

## Test Philosophy

Tests should protect behavior that matters:

- Tenant isolation.
- Auth boundaries.
- Upload safety.
- RAG/vector filters.
- API response contract.
- Service business rules.
- Repository query scoping.

## Test Shape

Prefer this pyramid:

```text
many service unit tests
some repository integration tests
some API integration tests
few end-to-end tests
```

## Naming

Use behavior names:

```python
def test_user_cannot_attach_other_users_document():
    ...
```

Avoid implementation-only names:

```python
def test_attach_documents_case_1():
    ...
```

## Regression Tests

Every production bug fix should add a regression test when practical.

The test should fail before the fix and pass after the fix.

## Tenant Tests

For every endpoint that receives a client-provided resource ID, include tests for:

- owner succeeds.
- other user receives not found.
- other user cannot mutate data.

## Do Not

- Do not mock away the behavior being tested.
- Do not only assert status code when response body matters.
- Do not write tests that depend on external LLM/network services.
- Do not make tests order-dependent.
- Do not weaken assertions to make a failing test pass.

## Environment Blockers

If tests cannot run because dependencies are missing, report it as an environment blocker with the exact missing module or command.

Do not mark verification as successful.
