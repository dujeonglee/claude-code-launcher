#!/usr/bin/env bash
# dependency_audit.sh — Audit project dependencies for vulnerabilities and issues.
#
# Usage:
#   ./dependency_audit.sh [language]
#
# Auto-detects language if not specified.

set -euo pipefail

LANG="${1:-auto}"

# ─── Auto-detect ──────────────────────────────────────────────────
detect_language() {
    if [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]]; then
        echo "python"
    elif [[ -f "package.json" ]]; then
        echo "javascript"
    elif [[ -f "Cargo.toml" ]]; then
        echo "rust"
    elif [[ -f "go.mod" ]]; then
        echo "go"
    else
        echo "unknown"
    fi
}

if [[ "${LANG}" == "auto" ]]; then
    LANG=$(detect_language)
    echo "Auto-detected: ${LANG}"
fi

ISSUES=0

# ─── Run audits ───────────────────────────────────────────────────
echo "========================================"
echo "Dependency Audit Report"
echo "========================================"
echo ""

case "${LANG}" in
    python)
        echo "--- Python Dependency Audit ---"
        echo ""

        # Check for known vulnerabilities
        echo "## Vulnerability Check"
        if command -v pip-audit &>/dev/null; then
            pip-audit 2>&1 || ISSUES=$((ISSUES + 1))
        elif command -v safety &>/dev/null; then
            safety check 2>&1 || ISSUES=$((ISSUES + 1))
        else
            echo "WARNING: Neither pip-audit nor safety installed."
            echo "  Install with: pip install pip-audit"
            ISSUES=$((ISSUES + 1))
        fi
        echo ""

        # Check for outdated packages
        echo "## Outdated Packages"
        pip list --outdated 2>/dev/null || echo "Could not check outdated packages"
        echo ""

        # Check for missing dependencies
        echo "## Unused/Missing Dependencies"
        if [[ -f "requirements.txt" ]]; then
            echo "Requirements file found. Cross-checking with imports..."
            IMPORTED=$(grep -rn "^from \|^import " --include="*.py" src/ 2>/dev/null | \
                awk -F'import ' '{print $2}' | awk -F'[. ]' '{print $1}' | sort -u)
            DECLARED=$(cat requirements.txt | grep -v "^#" | awk -F'[=><!]' '{print $1}' | tr -d ' ' | sort -u)
            echo "Imported packages: $(echo "${IMPORTED}" | wc -w)"
            echo "Declared packages: $(echo "${DECLARED}" | wc -w)"
        fi
        ;;

    javascript|typescript)
        echo "--- JavaScript/TypeScript Dependency Audit ---"
        echo ""

        echo "## Vulnerability Check"
        npm audit 2>&1 || ISSUES=$((ISSUES + 1))
        echo ""

        echo "## Outdated Packages"
        npm outdated 2>&1 || true
        echo ""

        echo "## Unused Dependencies"
        if command -v npx &>/dev/null; then
            npx depcheck 2>&1 || true
        else
            echo "Install depcheck for unused dependency detection"
        fi
        ;;

    rust)
        echo "--- Rust Dependency Audit ---"
        echo ""

        echo "## Vulnerability Check"
        if command -v cargo-audit &>/dev/null; then
            cargo audit 2>&1 || ISSUES=$((ISSUES + 1))
        else
            echo "Install with: cargo install cargo-audit"
        fi
        echo ""

        echo "## Outdated Dependencies"
        cargo outdated 2>&1 || echo "Install with: cargo install cargo-outdated"
        ;;

    go)
        echo "--- Go Dependency Audit ---"
        echo ""

        echo "## Vulnerability Check"
        if command -v govulncheck &>/dev/null; then
            govulncheck ./... 2>&1 || ISSUES=$((ISSUES + 1))
        else
            echo "Install with: go install golang.org/x/vuln/cmd/govulncheck@latest"
        fi
        echo ""

        echo "## Module Verification"
        go mod verify 2>&1 || ISSUES=$((ISSUES + 1))
        ;;

    *)
        echo "ERROR: Unknown language. Specify: python, javascript, rust, go"
        exit 1
        ;;
esac

# ─── License check ────────────────────────────────────────────────
echo ""
echo "## License Check"
echo "Checking for license files..."
if [[ -f "LICENSE" ]] || [[ -f "LICENSE.md" ]] || [[ -f "LICENCE" ]]; then
    echo "PASS: Project license file found"
else
    echo "WARNING: No LICENSE file found in project root"
    ISSUES=$((ISSUES + 1))
fi

# ─── Secrets check ────────────────────────────────────────────────
echo ""
echo "## Secrets Check"
echo "Scanning for potential secrets in source code..."

SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]*['\"]"
    "api_key\s*=\s*['\"][^'\"]*['\"]"
    "secret\s*=\s*['\"][^'\"]*['\"]"
    "BEGIN RSA PRIVATE KEY"
    "AKIA[0-9A-Z]{16}"  # AWS Access Key
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    MATCHES=$(grep -rnI "${pattern}" --include="*.py" --include="*.ts" --include="*.js" \
        --include="*.yaml" --include="*.yml" --include="*.json" \
        --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ \
        . 2>/dev/null | grep -v "test\|spec\|mock\|example\|sample" || true)
    if [[ -n "${MATCHES}" ]]; then
        echo "WARNING: Potential secret found matching pattern: ${pattern}"
        echo "${MATCHES}" | head -5
        ISSUES=$((ISSUES + 1))
    fi
done

if [[ ${ISSUES} -eq 0 ]]; then
    echo ""
    echo "No secrets detected in source code."
fi

# ─── Summary ──────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Audit Summary: ${ISSUES} issue(s) found"
echo "========================================"

exit "${ISSUES}"
