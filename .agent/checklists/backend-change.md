# Backend Change Checklist

Before finishing a backend change, verify:

- [ ] Router does not call repositories directly.
- [ ] Router does not access `service.repo`.
- [ ] Router only handles HTTP concerns.
- [ ] Business logic is in service.
- [ ] Service does not raise `HTTPException`.
- [ ] Expected failures use domain exceptions.
- [ ] User-owned queries include `user_id`.
- [ ] Other user's data is returned as not found.
- [ ] Response model is declared where practical.
- [ ] Client errors do not expose internals.
- [ ] Logs do not expose tokens, prompts, chunks, or secrets.
- [ ] Risky behavior has a test.
- [ ] Pytest/focused verification was attempted.
- [ ] `python -m compileall src/backend` passes.
- [ ] Unit/integration tests pass, or blocker is documented.
