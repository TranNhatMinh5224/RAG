# Workflow: Backend Refactor

Use this workflow when standardizing existing code.

1. Identify the current responsibility leak.
2. Move business logic from router to service.
3. Move persistence logic from service to repository if needed.
4. Replace booleans or `None` ambiguity with domain exceptions where useful.
5. Keep external API response shape stable unless intentionally changing it.
6. Add regression tests for the behavior being protected.
7. Run compile and tests.

Common leaks to remove:

- Router calls repository directly.
- Router accesses `service.repo`.
- Router performs ownership checks.
- Router orchestrates multi-step workflows.
- Service raises `HTTPException`.
- Repository contains business rules.

Refactor in small steps and keep diffs reviewable.
