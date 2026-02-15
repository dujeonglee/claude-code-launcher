#!/usr/bin/env bash
# coverage_check.sh — Run tests with coverage and check against thresholds.
#
# Usage:
#   ./coverage_check.sh [language] [threshold]
#
# Example:
#   ./coverage_check.sh python 80
#   ./coverage_check.sh typescript 75

set -euo pipefail

LANG="${1:-auto}"
THRESHOLD="${2:-80}"

# ─── Auto-detect language ─────────────────────────────────────────
detect_language() {
    if [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]] || [[ -f "pytest.ini" ]]; then
        echo "python"
    elif [[ -f "package.json" ]]; then
        echo "typescript"
    elif [[ -f "Cargo.toml" ]]; then
        echo "rust"
    elif [[ -f "CMakeLists.txt" ]] || [[ -f "Makefile" ]]; then
        echo "cpp"
    elif [[ -f "go.mod" ]]; then
        echo "go"
    else
        echo "unknown"
    fi
}

if [[ "${LANG}" == "auto" ]]; then
    LANG=$(detect_language)
    echo "Auto-detected language: ${LANG}"
fi

# ─── Run coverage by language ─────────────────────────────────────
case "${LANG}" in
    python)
        echo "Running pytest with coverage (threshold: ${THRESHOLD}%)..."
        python -m pytest \
            --cov=src --cov=. \
            --cov-report=term-missing \
            --cov-fail-under="${THRESHOLD}" \
            -q 2>&1 || {
                echo "FAIL: Coverage below ${THRESHOLD}%"
                exit 1
            }
        ;;

    typescript|javascript)
        echo "Running vitest/jest with coverage (threshold: ${THRESHOLD}%)..."
        if grep -q "vitest" package.json 2>/dev/null; then
            npx vitest run --coverage --coverage.thresholds.lines="${THRESHOLD}" 2>&1
        else
            npx jest --coverage --coverageThreshold="{\"global\":{\"lines\":${THRESHOLD}}}" 2>&1
        fi
        ;;

    rust)
        echo "Running cargo tarpaulin (threshold: ${THRESHOLD}%)..."
        cargo tarpaulin --fail-under "${THRESHOLD}" 2>&1 || {
            echo "FAIL: Coverage below ${THRESHOLD}%"
            exit 1
        }
        ;;

    go)
        echo "Running go test with coverage (threshold: ${THRESHOLD}%)..."
        go test ./... -coverprofile=coverage.out 2>&1
        COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | tr -d '%')
        echo "Total coverage: ${COVERAGE}%"
        if (( $(echo "${COVERAGE} < ${THRESHOLD}" | bc -l) )); then
            echo "FAIL: Coverage ${COVERAGE}% is below threshold ${THRESHOLD}%"
            exit 1
        fi
        ;;

    *)
        echo "ERROR: Could not detect language. Specify: python, typescript, rust, go, cpp"
        exit 1
        ;;
esac

echo "PASS: Coverage meets threshold of ${THRESHOLD}%"
