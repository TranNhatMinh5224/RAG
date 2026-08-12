# Service Layer Rules

Services are the home of business behavior.

Services should:

- Validate ownership.
- Enforce business rules.
- Coordinate repositories.
- Coordinate RAG, vector store, OCR, file storage, and other collaborators.
- Raise domain exceptions for expected business failures.
- Return domain models, DTO-like dicts, or plain values.

Services must not:

- Raise FastAPI `HTTPException`.
- Return HTTP responses.
- Know route paths, HTTP status codes, or headers.
- Access request objects except framework-specific cases such as `UploadFile`.

Good service behavior:

```python
conversation = await chat_repo.get_conversation_with_documents(conversation_id, user_id)
if conversation is None:
    raise ConversationNotFoundError
```

Bad service behavior:

```python
raise HTTPException(status_code=404, detail="Not found")
```

When a service writes to multiple systems, document and test failure behavior.
