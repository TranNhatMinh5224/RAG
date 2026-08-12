# Architecture Rules

The backend must use one consistent architecture:

```text
API Router -> Service -> Repository -> Database / External systems
```

## API Router

Routers own HTTP concerns only:

- Route path and method.
- Request and response schemas.
- Dependency resolution.
- Calling the use-case service method.
- Mapping domain exceptions to HTTP errors.

Routers must not contain business workflows.

## Service

Services own use cases:

- Business rules.
- Ownership checks.
- Multi-step workflows.
- Coordination between repositories and external systems.
- Domain exceptions.

Services must not raise FastAPI `HTTPException`.

## Repository

Repositories own persistence:

- SQLAlchemy queries.
- Database reads and writes.
- Query-level tenant filters.

Repositories must not implement business workflows or HTTP behavior.

## External Systems

Vector store, LLM, OCR, file storage, and email providers are external collaborators.

They should be called from services or dedicated application services, not routers or repositories.

## Dependency Direction

Allowed:

```text
router -> service -> repository
service -> external collaborator
```

Not allowed:

```text
router -> repository
router -> vector store / LLM / OCR
repository -> service
repository -> HTTP exception
```
