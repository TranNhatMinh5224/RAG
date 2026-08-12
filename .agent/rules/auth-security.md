# Auth and Security Rules

Auth logic belongs in `AuthService`, security helpers, or API dependencies.

Rules:

- Access tokens and refresh tokens must include `token_type`.
- Protected APIs accept only access tokens.
- Refresh endpoint accepts only refresh tokens.
- Inactive users must be rejected.
- Password verification belongs in `AuthService` or security helpers called by `AuthService`.
- Password updates belong in `AuthService`.
- Do not implement password reset without verified ownership of email/account.
- Do not reveal whether an email exists in password reset flows.
- Do not log passwords, tokens, or decoded token payloads.

Routers should not directly:

- Call `verify_password` for normal business flows.
- Hash passwords.
- Create tokens except inside auth-specific use cases.
- Decode tokens except inside auth dependencies or auth-specific service methods.

Production hardening backlog:

- Refresh token session storage and revoke.
- Rate limit login, refresh, upload, and chat.
- Audit logs for account-sensitive events.
- Strong password policy.
- Secret rotation plan.
