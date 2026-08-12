# Code Rules for Production Development

This is the long-form rule book. For day-to-day agent work, start with:

- `AGENTS.md`
- `rules/architecture.md`
- `rules/error-handling.md`
- `rules/testing.md`
- `checklists/backend-change.md`

This project must follow one consistent backend architecture:

```text
API Router -> Service -> Repository -> Database / External systems
```

The API layer must be thin. Business logic belongs in services. Database access belongs in repositories.

## 1. Layer Responsibilities

### API / Router Layer

Routers are responsible only for HTTP concerns:

- Define route path, method, request schema, and response schema.
- Receive path/query/body parameters.
- Resolve dependencies such as `current_user` and services.
- Call exactly one service method for the main use case when practical.
- Convert service results into HTTP responses.
- Convert domain exceptions into HTTP status codes.

Routers must not:

- Query repositories directly.
- Access `service.repo` or `service.some_repo`.
- Perform ownership checks.
- Filter data by `user_id`.
- Hash or verify passwords.
- Decode or create JWT tokens, except in auth-specific dependency/helper layers.
- Call vector store, LLM, OCR, file processors, or database sessions directly.
- Contain multi-step business workflows.

Good router shape:

```python
@router.post("", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        answer = await chat_service.chat_with_document(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            question=request.question,
        )
        return ChatResponse(answer=answer)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")
```

Bad router shape:

```python
conv = await chat_service.chat_repo.get_conversation_with_documents(...)
messages = await chat_service.chat_repo.get_recent_messages(...)
answer = await rag_chain.answer_question_async(...)
```

### Service Layer

Services own business use cases:

- Validate ownership and multi-tenant access.
- Enforce business rules.
- Coordinate repositories.
- Coordinate external services such as RAG, vector store, OCR, and file storage.
- Decide when to create, update, or delete records.
- Raise domain exceptions for expected business failures.

Services must not:

- Raise FastAPI `HTTPException`.
- Return raw HTTP responses.
- Know about route paths, status codes, or headers.
- Depend on request/response objects unless unavoidable for framework-provided objects such as `UploadFile`.

### Repository Layer

Repositories own persistence:

- Build SQLAlchemy queries.
- Read and write database models.
- Keep query filters explicit.
- Expose intention-revealing methods, for example:
  - `get_by_id_and_user(document_id, user_id)`
  - `get_conversation_with_documents(conversation_id, user_id)`
  - `get_recent_messages_for_user(conversation_id, user_id, limit)`

Repositories must not:

- Raise HTTP exceptions.
- Implement business workflows.
- Call LLM, vector store, OCR, or file system logic.
- Silently skip tenant filters on user-owned data.

## 2. Multi-Tenant Rules

Every user-owned resource must be scoped by `current_user.id`.

Required pattern:

```python
conversation = await chat_repo.get_conversation_with_documents(
    conversation_id=conversation_id,
    user_id=current_user.id,
)
if conversation is None:
    raise ConversationNotFoundError
```

Never fetch a user-owned record only by ID when the ID comes from the client.

Bad:

```python
document = await doc_repo.get_by_id(document_id)
conversation = await chat_repo.get_by_id(conversation_id)
messages = await chat_repo.get_recent_messages(conversation_id)
```

Good:

```python
document = await doc_repo.get_by_id_and_user(document_id, user_id)
conversation = await chat_repo.get_conversation_with_documents(conversation_id, user_id)
messages = await chat_repo.get_recent_messages_for_user(conversation_id, user_id)
```

If a resource does not belong to the current user, return the same result as not found. Do not leak whether another user's resource exists.

## 3. Error Handling Standard

Expected business failures should use domain exceptions.

Examples:

```python
class DomainError(Exception):
    pass


class ConversationNotFoundError(DomainError):
    pass


class ConversationHasNoDocumentsError(DomainError):
    pass
```

Services raise domain exceptions:

```python
if conversation is None:
    raise ConversationNotFoundError
```

Routers map domain exceptions to HTTP:

```python
except ConversationNotFoundError:
    raise HTTPException(status_code=404, detail="Conversation not found")
```

Unexpected exceptions should not expose internal stack traces, SQL errors, file paths, prompts, secrets, or provider errors to the client.

## 4. Response Standard

Use Pydantic response models for successful responses whenever possible.

For simple command endpoints, return a consistent shape:

```json
{
  "status": "success",
  "message": "..."
}
```

Do not return database models with fields that are not part of the declared response schema.

## 5. Dependency Injection Standard

Dependency wiring belongs in `api/dependencies.py`.

Routers should depend on services, not repositories.

Preferred:

```python
chat_service: ChatService = Depends(get_chat_service)
```

Avoid:

```python
chat_repo: ChatRepository = Depends(get_chat_repo)
```

If a service needs an external collaborator such as `RAGChain`, inject it into the service factory instead of passing it through the router when practical.

## 6. Auth Rules

Access tokens and refresh tokens must be distinguished by `token_type`.

- Protected APIs accept only access tokens.
- Refresh endpoint accepts only refresh tokens.
- Inactive users must be rejected.
- Password verification and password updates belong in `AuthService`.
- Routers should not call `verify_password` directly for normal business flows.

## 7. Upload and File Rules

Upload handling must be defensive:

- Sanitize filenames with `Path(file.filename).name`.
- Store files using generated names, not user-provided names.
- Enforce max upload size.
- Validate extension.
- Validate MIME type and magic bytes before production release.
- Clean up file and DB record if ingestion fails.
- Do not log file contents or extracted document chunks in production.

## 8. Vector Store and RAG Rules

Vector retrieval must always include tenant filters:

- `metadata.user_id == current_user.id`
- `metadata.document_id in allowed_document_ids`

Never let the client provide arbitrary vector filters.

RAG flow belongs in service/application service, not router:

```text
verify conversation ownership
get allowed document IDs
get chat history
save user message
call RAG
save AI message
return answer
```

## 9. Transaction and Consistency Rules

Avoid partial writes.

When a use case writes to multiple systems, document the failure behavior:

- DB write succeeds but vector ingestion fails.
- File saved but DB write fails.
- Vector delete fails but DB delete succeeds.

For production, prefer explicit transaction boundaries in services or a Unit of Work pattern.

## 10. Testing Rules

Every production-sensitive change needs tests proportional to risk.

Required tests for multi-tenant features:

- User A cannot read User B's conversation.
- User A cannot attach User B's document.
- User A cannot update User B's conversation-document relationship.
- User A cannot write chat messages into User B's conversation.
- Vector retrieval includes both `user_id` and allowed `document_id` filters.

Test levels:

- Unit tests for service business logic.
- Repository tests for tenant-scoped queries.
- API integration tests for HTTP status and response shape.

## 11. Logging Rules

Logs must help debug production without leaking data.

Do log:

- Request ID.
- User ID.
- Operation name.
- Resource IDs owned by that user.
- Error class.
- Timing.

Do not log:

- Passwords or tokens.
- Full prompts.
- Full document chunks.
- Raw extracted file text.
- Secret environment variables.

## 12. Code Style Rules

- Keep functions small and intention-revealing.
- Prefer explicit names over clever abbreviations.
- Use type hints for service and repository methods.
- Keep comments rare and useful.
- Do not introduce broad refactors while fixing a narrow bug.
- Preserve existing user changes in the working tree.
- Use `rg` for searching.
- Use `apply_patch` for manual file edits.

## 13. Review Checklist

Before considering a backend change complete, check:

- Does the router call repositories directly?
- Does any user-owned query miss `user_id`?
- Does service raise `HTTPException`?
- Does router contain business workflow logic?
- Are expected errors mapped consistently?
- Are response models declared?
- Are sensitive details hidden from client errors and logs?
- Is there at least one test for the risky behavior?
- Does `python -m compileall src/backend` pass?

## 14. Current Refactor Target

The next architecture cleanup should standardize all routers to this shape:

```text
request -> service method -> response model
```

Priority order:

1. `chat.py`
2. `conversation.py`
3. `document.py`
4. `auth.py`

The final target is that every API endpoint has the same mental model and the same production error-handling style.
