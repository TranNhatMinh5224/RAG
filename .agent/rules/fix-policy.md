# Fix Policy Rules

Bug fixing must preserve the architecture.

## Root Cause First

Before editing code, identify:

- What failed.
- Why it failed.
- Which layer owns the fix.
- Which test should catch it next time.

## Layer Ownership

Fix in the correct layer:

- HTTP mapping bug: router or global exception handler.
- Business rule bug: service.
- Query/filter bug: repository.
- Token/hash bug: auth service or security helper.
- Vector filter bug: retriever/vector service.
- Upload safety bug: document service or upload helper.

## Forbidden Fixes

Never fix by:

- Adding repository calls in routers.
- Returning HTTP responses from services.
- Removing tenant filters.
- Catching and ignoring exceptions.
- Returning success when an operation failed.
- Changing tests to match unsafe behavior.
- Logging secrets, prompts, chunks, or tokens.

## Regression Rule

If the bug could return wrong data, leak data, corrupt data, or break auth, add a regression test.

## Verification Rule

After a fix, run:

```powershell
python -m compileall src/backend
```

Then run the focused failing test.

Then run the broader test suite when dependencies allow it.
