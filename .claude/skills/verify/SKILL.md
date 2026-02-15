---
name: verify
description: >
  Software verification, testing, and quality assurance methodology. Use when running
  tests, writing tests, checking coverage, performing static analysis, debugging test
  failures, or validating code quality. Covers pytest, Jest/Vitest, cargo test,
  GoogleTest, and general testing best practices.
---

# Verification Skill

## Purpose
Provide structured methodology for comprehensive software verification including
testing, static analysis, coverage measurement, and quality metrics.

## Testing Pyramid

```
        ╱╲
       ╱  ╲       E2E Tests (few, slow, high confidence)
      ╱────╲
     ╱      ╲     Integration Tests (moderate count)
    ╱────────╲
   ╱          ╲   Unit Tests (many, fast, focused)
  ╱────────────╲
```

- **Unit tests**: Test individual functions/methods in isolation. Mock dependencies.
- **Integration tests**: Test module interactions. Use real (or test) databases.
- **E2E tests**: Test full user flows. Slowest but highest confidence.

Target ratio: ~70% unit, ~20% integration, ~10% E2E.

## Test Structure: Arrange-Act-Assert

Every test should follow this pattern:

```python
def test_user_creation_with_valid_email_returns_user():
    # Arrange — set up preconditions
    email = "alice@example.com"
    repo = FakeUserRepository()
    service = UserService(repo)

    # Act — perform the action under test
    user = service.create_user(email)

    # Assert — verify the result
    assert user.email == email
    assert user.id is not None
    assert repo.find_by_id(user.id) is not None
```

## Test Naming Convention

Format: `test_<unit>_<scenario>_<expected_result>`

Good examples:
- `test_parse_config_with_missing_key_raises_validation_error`
- `test_calculate_tax_with_zero_amount_returns_zero`
- `test_authenticate_with_expired_token_returns_unauthorized`

## What to Test

### Always test:
- Happy path (normal operation)
- Edge cases: empty input, null/None, zero, negative, max values
- Error paths: invalid input, network failures, timeout, permission denied
- Boundary values: off-by-one, min/max of ranges, empty collections
- State transitions: initial → active → suspended → terminated

### Test smells to avoid:
- **No assertions**: Test runs code but doesn't verify anything
- **Tautological tests**: `assert True`, `assert x == x`
- **Implementation coupling**: Tests break when internals change but behavior doesn't
- **Test interdependence**: Test B only passes if Test A runs first
- **Excessive mocking**: Mocking the thing you're trying to test

## Framework Quick Reference

### Python (pytest)
```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run specific test
pytest tests/test_auth.py::test_login_success -v

# Run tests matching pattern
pytest -k "test_payment" -v

# Type checking
mypy src/ --strict
```

### TypeScript (Vitest / Jest)
```bash
# Run all tests
npx vitest run

# Run with coverage
npx vitest run --coverage

# Run specific file
npx vitest run src/auth.test.ts

# Type check
npx tsc --noEmit
```

### Rust
```bash
# Run all tests
cargo test

# Run with output
cargo test -- --nocapture

# Run specific test
cargo test test_payment_processing

# Coverage
cargo tarpaulin --out Html
```

### C/C++ (GoogleTest / CTest)
```bash
# Build and run
cmake --build build --target test
ctest --test-dir build -V

# Run specific test
./build/tests/test_binary --gtest_filter="SuiteName.TestName"
```

## Coverage Targets

| Category | Target | Rationale |
|----------|--------|-----------|
| New code | ≥ 80% | Ensures new features are tested |
| Critical paths | ≥ 95% | Auth, payment, data integrity |
| Overall project | ≥ 70% | Pragmatic baseline |
| Bug fixes | 100% of fix | Regression test for every bug |

## Static Analysis Tools

| Language | Type Check | Linter | Formatter |
|----------|-----------|--------|-----------|
| Python | mypy | pylint, flake8, ruff | black, ruff |
| TypeScript | tsc | eslint | prettier |
| Rust | (built-in) | clippy | rustfmt |
| C/C++ | (compiler) | clang-tidy, cppcheck | clang-format |
| Go | (built-in) | golangci-lint | gofmt |

## Test Templates

See the `templates/` directory for ready-to-use test file templates:
- `test_template.py.tmpl` — Python pytest template
- `jest.test.ts.tmpl` — TypeScript Jest/Vitest template
