---
name: audit
description: >
  Security audit, architecture review, and compliance analysis methodology. Use when
  performing security reviews, checking for vulnerabilities, analyzing code architecture,
  auditing dependencies, checking for circular dependencies, evaluating coupling/cohesion,
  or assessing compliance. Covers OWASP Top 10, dependency analysis, and code quality metrics.
---

# Audit Skill

## Purpose
Provide structured methodology for comprehensive security audits, architecture reviews,
and compliance checks. Produces actionable findings with severity levels and remediation paths.

## Security Audit Methodology (OWASP-aligned)

### Quick Grep Patterns

Use these patterns to quickly scan for common vulnerabilities:

#### Injection
```bash
# SQL injection
grep -rn "f\"SELECT\|f\"INSERT\|f\"UPDATE\|f\"DELETE\|f\"DROP" --include="*.py"
grep -rn "execute.*+.*input\|execute.*%s.*%.*input" --include="*.py"
grep -rn "query.*\`\$\{" --include="*.ts" --include="*.js"

# Command injection
grep -rn "os\.system\|os\.popen\|subprocess.*shell=True" --include="*.py"
grep -rn "child_process\|exec(" --include="*.ts" --include="*.js"
grep -rn "system(\|popen(" --include="*.c" --include="*.cpp"

# Eval / code execution
grep -rn "eval(\|exec(" --include="*.py" --include="*.js" --include="*.ts"
```

#### Secrets & Credentials
```bash
# Hardcoded secrets
grep -rn "password\s*=\s*['\"]" --include="*.py" --include="*.ts" --include="*.js"
grep -rn "api_key\|apiKey\|API_KEY\|secret_key\|SECRET" --include="*.py" --include="*.ts"
grep -rn "BEGIN RSA PRIVATE KEY\|BEGIN PRIVATE KEY" -r .

# Check for .env files in version control
git ls-files | grep -i "\.env"
```

#### Insecure Patterns
```bash
# HTTP instead of HTTPS
grep -rn "http://" --include="*.py" --include="*.ts" --include="*.yaml" --include="*.yml"

# Insecure crypto
grep -rn "md5\|sha1\|DES\|RC4" --include="*.py" --include="*.ts" --include="*.java"

# Missing input validation
grep -rn "request\.get\|request\.post\|req\.body\|req\.params\|req\.query" \
  --include="*.py" --include="*.ts" --include="*.js"
```

### OWASP Top 10 Checklist (2021)

| # | Category | What to Check |
|---|----------|---------------|
| A01 | Broken Access Control | Missing auth checks, IDOR, path traversal, CORS |
| A02 | Cryptographic Failures | Weak hashing, plaintext secrets, missing encryption |
| A03 | Injection | SQL, NoSQL, OS command, LDAP, XSS |
| A04 | Insecure Design | Missing threat model, no rate limiting, no abuse prevention |
| A05 | Security Misconfiguration | Default creds, verbose errors, unnecessary features |
| A06 | Vulnerable Components | Outdated deps, known CVEs |
| A07 | Auth Failures | Weak passwords allowed, missing MFA, session issues |
| A08 | Data Integrity Failures | No signature verification, insecure deserialization |
| A09 | Logging Failures | Missing audit logs, logging sensitive data |
| A10 | SSRF | Unchecked URLs, internal network access |

For detailed checklists, see [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md).

## Architecture Review Methodology

### Module Dependency Analysis

#### What to look for:
1. **Circular dependencies** — Module A imports B, B imports A (or longer cycles).
2. **God modules** — Modules that everything depends on (high fan-in AND fan-out).
3. **Layering violations** — Lower layers importing upper layers.
4. **Unstable dependencies** — Stable modules depending on frequently-changing ones.

#### Quick analysis commands:
```bash
# Python: find import cycles
grep -rn "^from \|^import " --include="*.py" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20

# Python: count dependencies per file
grep -rn "^from \|^import " --include="*.py" src/ | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn

# TypeScript: find import cycles
grep -rn "^import " --include="*.ts" --include="*.tsx" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20

# C/C++: find include dependencies
grep -rn "^#include" --include="*.h" --include="*.cpp" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### Code Quality Metrics

| Metric | Threshold | Tool |
|--------|-----------|------|
| Cyclomatic complexity | ≤ 15 per function | radon (Python), eslint (TS) |
| Function length | ≤ 50 lines | manual / linter |
| File length | ≤ 500 lines | wc -l |
| Parameters | ≤ 5 per function | linter |
| Nesting depth | ≤ 4 levels | linter |
| Fan-out (imports) | ≤ 10 per module | custom analysis |

For detailed architecture review guidance, see [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md).

## Severity Definitions

| Level | Definition | SLA |
|-------|-----------|-----|
| **CRITICAL** | Exploitable vulnerability, data loss, system compromise | Fix immediately |
| **HIGH** | Significant security or quality risk | Fix this sprint |
| **MEDIUM** | Moderate risk, maintainability concern | Fix this quarter |
| **LOW** | Minor improvement, style issue | Backlog |
| **INFO** | Observation, no action required | — |

## Report Template

```markdown
## Audit Report — [Scope]
**Date**: YYYY-MM-DD
**Auditor**: Claude Code (auditor agent)
**Scope**: [files/modules reviewed]

### Summary
| Severity | Count |
|----------|-------|
| Critical | N |
| High     | N |
| Medium   | N |
| Low      | N |
| Info     | N |

### Findings

#### [ID] [SEVERITY] Title
- **Category**: [Security/Architecture/Dependency/Compliance]
- **Location**: `file:line`
- **Description**: What the issue is
- **Impact**: What could go wrong
- **Evidence**: Code snippet or command output
- **Remediation**: How to fix it
- **Reference**: Standard/guideline (e.g., OWASP A03)
```
