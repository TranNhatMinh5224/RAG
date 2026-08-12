# Multi-Tenant Rules

Every user-owned resource must be scoped by `current_user.id`.

Client-provided IDs are untrusted.

Required pattern:

```python
conversation = await chat_repo.get_conversation_with_documents(
    conversation_id=conversation_id,
    user_id=user_id,
)
if conversation is None:
    raise ConversationNotFoundError
```

Never fetch user-owned data only by ID when the ID came from the client.

Bad:

```python
conversation = await chat_repo.get_by_id(conversation_id)
document = await doc_repo.get_by_id(document_id)
messages = await chat_repo.get_recent_messages(conversation_id)
```

Good:

```python
conversation = await chat_repo.get_conversation_with_documents(conversation_id, user_id)
document = await doc_repo.get_by_id_and_user(document_id, user_id)
messages = await chat_repo.get_recent_messages_for_user(conversation_id, user_id)
```

If a resource belongs to another user, treat it as not found.

Do not leak:

- Whether another user's conversation exists.
- Whether another user's document exists.
- Document filenames from another user.
- Vector payloads from another user.

Required tests:

- User A cannot read User B's conversation.
- User A cannot attach User B's document.
- User A cannot update User B's conversation-document relation.
- User A cannot write messages into User B's conversation.
- Vector retrieval filters by both `user_id` and allowed document IDs.
