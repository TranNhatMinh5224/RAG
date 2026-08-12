# API Router Rules

Routers should be thin and boring.

Allowed in routers:

- Read request body, path, query.
- Resolve `current_user`.
- Resolve service dependencies.
- Call a service method.
- Return a Pydantic response model.
- Map domain exceptions to `HTTPException`.

Not allowed in routers:

- Calling repositories directly.
- Accessing `service.repo` or `service.some_repo`.
- Filtering by `user_id`.
- Checking ownership.
- Hashing or verifying passwords.
- Creating or decoding JWTs, except auth dependencies/helpers.
- Calling RAG, vector store, OCR, file processors, or database sessions directly.
- Running multi-step workflows.

Preferred shape:

```python
@router.post("", response_model=SomeResponse)
async def endpoint(
    request: SomeRequest,
    current_user: User = Depends(get_current_user),
    service: SomeService = Depends(get_some_service),
):
    try:
        result = await service.run_use_case(
            user_id=current_user.id,
            value=request.value,
        )
        return SomeResponse.model_validate(result)
    except SomeDomainError:
        raise HTTPException(status_code=400, detail="Invalid request")
```

If router logic grows past dependency wiring, one service call, and exception mapping, move it into a service.
