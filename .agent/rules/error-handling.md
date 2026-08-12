# Error Handling Rules

Expected business failures use domain exceptions.

Example:

```python
class DomainError(Exception):
    pass


class ConversationNotFoundError(DomainError):
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

Unexpected errors:

- Do not expose internal exception messages to clients.
- Do not expose SQL errors.
- Do not expose file paths.
- Do not expose prompts, document chunks, tokens, or secrets.
- Log enough context for debugging, but keep sensitive content out of logs.

Use consistent status mapping:

- `400`: invalid business state or invalid request.
- `401`: unauthenticated.
- `403`: authenticated but forbidden, only when revealing existence is safe.
- `404`: not found or not owned.
- `409`: conflict such as duplicate or invalid state transition.
- `413`: upload too large.
- `422`: schema validation errors from FastAPI/Pydantic.
- `500`: unexpected server error with generic client message.
