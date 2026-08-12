# Workflow: Add API Endpoint

Use this workflow when adding a backend endpoint.

1. Define request and response schemas in `models/schemas.py`.
2. Add or reuse a service method for the use case.
3. Add repository methods only for persistence operations.
4. Add route function that calls the service method.
5. Map domain exceptions to HTTP errors in the router.
6. Add tests for service behavior.
7. Add API integration test if response/status behavior matters.
8. Run backend verification commands.

Endpoint target shape:

```text
request -> service method -> response model
```

Do not place business logic in the router just because it is short.
