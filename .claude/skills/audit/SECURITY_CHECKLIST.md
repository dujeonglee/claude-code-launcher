# Security Audit Checklist

Detailed checklist for each OWASP Top 10 category. Use during the security audit phase.

## A01: Broken Access Control

- [ ] Every endpoint/route has an explicit authorization check
- [ ] Authorization is enforced server-side (not just client-side)
- [ ] Users cannot access other users' resources (test with different user IDs)
- [ ] Admin functions are restricted to admin roles
- [ ] CORS is configured with specific allowed origins (not `*`)
- [ ] Directory listing is disabled on web servers
- [ ] File uploads validate type, size, and don't allow path traversal
- [ ] Rate limiting is applied to sensitive endpoints
- [ ] JWT tokens include audience (`aud`) and issuer (`iss`) claims
- [ ] API keys are scoped to minimum required permissions

## A02: Cryptographic Failures

- [ ] Passwords are hashed with bcrypt, scrypt, or argon2 (not MD5/SHA)
- [ ] Sensitive data is encrypted at rest (database, files)
- [ ] All network communication uses TLS 1.2+ (no plain HTTP)
- [ ] Cryptographic keys are stored securely (not in source code)
- [ ] Random number generation uses cryptographically secure source
- [ ] No deprecated algorithms (MD5, SHA1, DES, RC4, RSA < 2048 bits)
- [ ] Certificate validation is not disabled in any HTTP client

## A03: Injection

- [ ] All SQL uses parameterized queries or ORM (no string concatenation)
- [ ] All shell commands avoid user input (or strictly validate/escape)
- [ ] HTML output is escaped/sanitized to prevent XSS
- [ ] JSON/XML parsers are configured to prevent entity expansion (XXE)
- [ ] LDAP/XPath queries use parameterized APIs
- [ ] NoSQL queries don't embed user input directly
- [ ] Template rendering uses auto-escaping

## A04: Insecure Design

- [ ] Threat model exists for the application
- [ ] Rate limiting on login, registration, password reset
- [ ] Account lockout after repeated failed attempts
- [ ] Multi-factor authentication available for sensitive operations
- [ ] Business logic abuse scenarios are considered
- [ ] Resource consumption limits are enforced (file size, query complexity)

## A05: Security Misconfiguration

- [ ] Default credentials are changed
- [ ] Error messages don't expose stack traces or internal details
- [ ] Unnecessary features/endpoints are disabled
- [ ] Security headers are set (CSP, X-Frame-Options, HSTS, etc.)
- [ ] Directory indexing is disabled
- [ ] Server version headers are removed or minimized
- [ ] Debug mode is disabled in production configuration

## A06: Vulnerable & Outdated Components

- [ ] All dependencies are at latest stable versions (or patched)
- [ ] No known CVEs in dependency tree (`npm audit`, `pip audit`, `cargo audit`)
- [ ] Unused dependencies are removed
- [ ] Dependency versions are pinned (lock files committed)
- [ ] License compatibility is verified
- [ ] Components are downloaded from trusted sources only

## A07: Identification & Authentication Failures

- [ ] Password requirements enforce minimum complexity
- [ ] Brute force protection exists (rate limiting, CAPTCHA, lockout)
- [ ] Session tokens are regenerated after login
- [ ] Session timeout is configured appropriately
- [ ] "Remember me" tokens are securely stored and scoped
- [ ] Password reset tokens expire quickly and are single-use
- [ ] Multi-factor authentication is supported

## A08: Software & Data Integrity Failures

- [ ] CI/CD pipeline verifies signatures of dependencies
- [ ] Deserialization of untrusted data uses safe libraries
- [ ] Software updates are verified with digital signatures
- [ ] Git commits are signed (if required by policy)
- [ ] Webhook payloads are verified with signatures

## A09: Security Logging & Monitoring Failures

- [ ] Authentication events (login, logout, failure) are logged
- [ ] Authorization failures are logged
- [ ] Input validation failures are logged
- [ ] Logs don't contain sensitive data (passwords, tokens, PII)
- [ ] Log files are protected from tampering
- [ ] Alerting exists for suspicious patterns
- [ ] Log format supports automated analysis

## A10: Server-Side Request Forgery (SSRF)

- [ ] User-supplied URLs are validated against allowlists
- [ ] Internal network addresses (10.x, 172.16.x, 192.168.x) are blocked
- [ ] URL redirects don't allow arbitrary destinations
- [ ] DNS rebinding protections are in place
- [ ] HTTP clients follow redirects cautiously
