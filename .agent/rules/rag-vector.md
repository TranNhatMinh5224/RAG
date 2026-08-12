# RAG and Vector Rules

Vector retrieval must always be tenant-scoped.

Required filters:

- `metadata.user_id == current_user.id`
- `metadata.document_id in allowed_document_ids`

Never let the client provide arbitrary vector filters.

RAG flow belongs in a service/application service:

```text
verify conversation ownership
get allowed document IDs
get chat history
save user message
call RAG
save AI message
return answer
```

Production RAG requirements:

- Add relevance threshold before answering.
- Return structured citations from trusted metadata.
- Add prompt-injection tests.
- Add retrieval eval dataset.
- Measure baseline before adding hybrid search.
- Do not log full prompts or retrieved chunks in production.

If the README claims hybrid search, the code must actually implement hybrid search or the README must be corrected.
