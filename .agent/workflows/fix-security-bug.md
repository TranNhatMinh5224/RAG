# Workflow: Fix Security Bug

Use this workflow for tenant, auth, upload, secret, or data exposure bugs.

1. Reproduce or describe the exploit path.
2. Find all similar paths with `rg`.
3. Fix the root pattern, not only one endpoint.
4. Add regression tests that fail before the fix.
5. Ensure errors do not leak whether another user's data exists.
6. Check logs for sensitive data exposure.
7. Run backend verification.
8. Document residual risk if any remains.

For multi-tenant bugs, verify:

- Client-provided resource IDs are scoped by `current_user.id`.
- Vector filters include `user_id`.
- Message history cannot be read or written across tenants.
- Relationship tables cannot connect resources from different users.
