---
name: document
description: >
  Documentation standards, templates, and generation methodology. Use when writing READMEs,
  API docs, Architecture Decision Records (ADRs), changelogs, release notes, docstrings,
  onboarding guides, or any technical documentation. Also use when assessing documentation
  coverage or quality.
---

# Documentation Skill

## Purpose
Provide templates, standards, and methodology for creating and maintaining
high-quality software documentation that developers actually read and use.

## Documentation Types Reference

| Type | When | Where | Template |
|------|------|-------|----------|
| Module README | New module created | `module/README.md` | See below |
| API Reference | Public API changes | Docstrings in source | See below |
| ADR | Architecture decision | `docs/adr/NNNN-*.md` | [adr.md.tmpl](templates/adr.md.tmpl) |
| Changelog | Every PR/change | `CHANGELOG.md` (root) | [changelog-entry.md.tmpl](templates/changelog-entry.md.tmpl) |
| API Doc | New/changed endpoints | `docs/api/` | [api-doc.md.tmpl](templates/api-doc.md.tmpl) |
| Runbook | Operational procedure | `docs/runbooks/` | Freeform |
| Getting Started | New project or major change | Root `README.md` | See below |

## README Structure Standard

Every README should follow this structure (omit irrelevant sections):

```markdown
# Project/Module Name

One-sentence summary of what this does and why it exists.

## Quick Start

Minimal example to get from zero to working in < 2 minutes.

## Installation

Prerequisites, dependencies, and setup steps.

## Usage

### Basic Usage
Most common use case with a working code example.

### Advanced Usage
Less common patterns, configuration options.

## API Reference

Key functions/classes with signatures (or link to generated docs).

## Architecture

Brief description of how this is structured and why.
Link to ADRs for significant decisions.

## Configuration

Environment variables, config files, and their options.

## Development

How to set up for development, run tests, and contribute.

## Troubleshooting

Common issues and their solutions.
```

## Docstring Standards

### Python (Google Style)
```python
def transfer_funds(
    source: Account,
    target: Account,
    amount: Decimal,
    currency: str = "USD",
) -> TransferResult:
    """Transfer funds between two accounts.

    Validates sufficient balance, converts currency if needed, and
    executes the transfer atomically. Emits a TransferCompleted event
    on success.

    Args:
        source: The account to debit.
        target: The account to credit.
        amount: Transfer amount. Must be positive.
        currency: ISO 4217 currency code. Defaults to "USD".

    Returns:
        TransferResult containing transaction ID and final balances.

    Raises:
        InsufficientFundsError: If source balance < amount.
        CurrencyConversionError: If conversion rate unavailable.
        AccountFrozenError: If either account is frozen.

    Example:
        >>> result = transfer_funds(checking, savings, Decimal("500"))
        >>> print(result.transaction_id)
        'txn_abc123'

    Note:
        This operation is idempotent — retrying with the same
        idempotency key will return the original result.
    """
```

### TypeScript (TSDoc)
```typescript
/**
 * Transfer funds between two accounts.
 *
 * Validates sufficient balance, converts currency if needed, and
 * executes the transfer atomically.
 *
 * @param source - The account to debit
 * @param target - The account to credit
 * @param amount - Transfer amount (must be positive)
 * @param options - Optional transfer configuration
 * @returns Promise resolving to TransferResult with transaction ID
 * @throws {InsufficientFundsError} If source balance < amount
 * @throws {AccountFrozenError} If either account is frozen
 *
 * @example
 * ```ts
 * const result = await transferFunds(checking, savings, 500);
 * console.log(result.transactionId); // 'txn_abc123'
 * ```
 */
```

### C++ (Doxygen)
```cpp
/**
 * @brief Transfer funds between two accounts.
 *
 * Validates sufficient balance, converts currency if needed,
 * and executes the transfer atomically.
 *
 * @param source The account to debit
 * @param target The account to credit
 * @param amount Transfer amount (must be positive)
 * @return TransferResult containing transaction ID
 * @throws InsufficientFundsError if source balance < amount
 *
 * @code
 * auto result = transfer_funds(checking, savings, 500.0);
 * std::cout << result.transaction_id << std::endl;
 * @endcode
 */
```

## Changelog Standard (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New features that have been added

### Changed
- Changes in existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Vulnerability fixes
```

Categories in order: Added, Changed, Deprecated, Removed, Fixed, Security.

## Documentation Coverage Check

Use the script in `scripts/doc_coverage.sh` to check:
- Public functions/methods without docstrings
- Modules without README files
- Missing changelog entries
- Stale docs (modified code but unchanged docs)

## Templates

See the `templates/` directory for ready-to-use templates:
- [adr.md.tmpl](templates/adr.md.tmpl) — Architecture Decision Record
- [api-doc.md.tmpl](templates/api-doc.md.tmpl) — API endpoint documentation
- [changelog-entry.md.tmpl](templates/changelog-entry.md.tmpl) — Changelog entry
