# Repository Rules

Repositories own database persistence only.

Repositories should:

- Build SQLAlchemy queries.
- Use explicit filters.
- Return ORM models or lists of ORM models.
- Expose intention-revealing methods.

Good method names:

- `get_by_id_and_user(document_id, user_id)`
- `get_by_ids_and_user(document_ids, user_id)`
- `get_conversation_with_documents(conversation_id, user_id)`
- `get_recent_messages_for_user(conversation_id, user_id, limit)`

Repositories must not:

- Raise `HTTPException`.
- Call services.
- Call LLM, vector store, OCR, file storage, or email.
- Implement business workflows.
- Silently skip tenant filters for user-owned resources.

For user-owned records, never add a generic `get_by_id(id)` unless there is a strong reason and its caller cannot be reached from user input.
