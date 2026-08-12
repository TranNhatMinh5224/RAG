# Workflow: Production Review

Use this workflow when reviewing readiness for production.

Review areas:

- Architecture consistency.
- Multi-tenant isolation.
- Auth and session security.
- Upload hardening.
- Background jobs and retries.
- Transaction boundaries.
- RAG quality and evals.
- Logging, metrics, tracing, alerting.
- Docker and deployment.
- Database migrations, indexes, backup, restore.
- Dependency pinning and security scanning.

Output findings by severity:

- Critical: data leak, auth bypass, destructive data loss.
- High: production outage, major security weakness, costly abuse path.
- Medium: reliability, maintainability, test gaps.
- Low: cleanup, naming, minor consistency.

Every finding should include:

- File and line when possible.
- Why it matters.
- Suggested fix.
