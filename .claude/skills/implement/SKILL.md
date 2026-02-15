---
name: implement
description: >
  Code implementation best practices, patterns, and templates. Use when writing new code,
  creating modules, classes, components, functions, or refactoring existing code. Covers
  Python, TypeScript, C/C++, Rust, Go, and general software design principles.
---

# Implementation Skill

## Purpose
Provide structured guidance for writing clean, production-quality code that follows
project conventions and industry best practices.

## Design Principles (SOLID + Pragmatism)

1. **Single Responsibility** — Each module/class/function does one thing well.
2. **Open/Closed** — Open for extension, closed for modification (use interfaces/protocols).
3. **Liskov Substitution** — Subtypes must be substitutable for their base types.
4. **Interface Segregation** — Many specific interfaces > one general-purpose interface.
5. **Dependency Inversion** — Depend on abstractions, not concrete implementations.
6. **YAGNI** — Don't build what you don't need yet.
7. **DRY** — Extract when you see the *same logic* three times (not just similar code).

## Implementation Checklist

Before writing code:
- [ ] Understand the requirement / spec / acceptance criteria
- [ ] Identify existing patterns in the codebase to follow
- [ ] Define the public API / interface first
- [ ] List edge cases and error conditions
- [ ] Identify what tests need to exist

While writing code:
- [ ] Meaningful names (variables, functions, classes)
- [ ] Small functions (< 30 lines preferred)
- [ ] Explicit error handling (no silent failures)
- [ ] Type annotations / type hints
- [ ] No hardcoded values (use constants or config)
- [ ] No unnecessary comments (code should be self-documenting)

After writing code:
- [ ] Code compiles / parses cleanly
- [ ] Existing tests still pass
- [ ] No unused imports or dead code
- [ ] Linter / formatter has been run

## Error Handling Patterns

### Python
```python
# Good: Specific exceptions with context
class PaymentError(Exception):
    def __init__(self, message: str, transaction_id: str | None = None):
        super().__init__(message)
        self.transaction_id = transaction_id

def charge(amount: Decimal) -> Receipt:
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    try:
        result = gateway.charge(amount)
    except GatewayTimeout as e:
        raise PaymentError("Gateway timeout", transaction_id=e.txn_id) from e
    return Receipt(result.id, amount)
```

### TypeScript
```typescript
// Good: Result type pattern (no thrown exceptions in business logic)
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function parseConfig(raw: string): Result<Config, ConfigError> {
  try {
    const parsed = JSON.parse(raw);
    return { ok: true, value: validateConfig(parsed) };
  } catch (e) {
    return { ok: false, error: new ConfigError(`Invalid config: ${e}`) };
  }
}
```

### C/C++
```cpp
// Good: RAII + expected/optional for error handling
std::expected<Connection, ConnectionError> connect(const Config& config) {
    auto socket = std::make_unique<Socket>(config.host, config.port);
    if (!socket->is_valid()) {
        return std::unexpected(ConnectionError::InvalidSocket);
    }
    return Connection(std::move(socket));
}
```

## Scaffolding Templates

For new module/component templates, see the `templates/` directory:
- `module.py.tmpl` — Python module with standard structure
- `component.tsx.tmpl` — React component with TypeScript
- `class.cpp.tmpl` — C++ class with header/implementation split

## Common Patterns

### Dependency Injection
```python
# Instead of:
class OrderService:
    def __init__(self):
        self.db = PostgresDB()  # Hardcoded dependency

# Do:
class OrderService:
    def __init__(self, db: Database):  # Accept interface
        self.db = db
```

### Builder Pattern (for complex construction)
```typescript
const query = new QueryBuilder()
  .select("name", "email")
  .from("users")
  .where("active", true)
  .limit(10)
  .build();
```

### Strategy Pattern (for swappable algorithms)
```python
from typing import Protocol

class CompressionStrategy(Protocol):
    def compress(self, data: bytes) -> bytes: ...

class GzipCompression:
    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data)

class FileProcessor:
    def __init__(self, compression: CompressionStrategy):
        self.compression = compression
```
