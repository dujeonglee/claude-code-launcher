#!/usr/bin/env bash
# doc_coverage.sh — Check documentation coverage across the project.
#
# Usage:
#   ./doc_coverage.sh [src_dir]
#
# Checks:
#   1. Public functions/classes without docstrings (Python, TS)
#   2. Modules without README files
#   3. CHANGELOG.md presence and freshness
#   4. Files with code changes but no doc updates

set -euo pipefail

SRC_DIR="${1:-.}"
ISSUES=0

echo "========================================"
echo "Documentation Coverage Report"
echo "========================================"
echo ""

# ─── 1. Docstring coverage (Python) ──────────────────────────────
echo "## Python Docstring Coverage"
echo ""

PY_FILES=$(find "${SRC_DIR}" -name "*.py" -not -path "*/test*" \
    -not -path "*/__pycache__/*" -not -path "*/node_modules/*" \
    -not -name "__init__.py" 2>/dev/null)

if [[ -n "${PY_FILES}" ]]; then
    TOTAL_PUBLIC=0
    UNDOCUMENTED=0

    while IFS= read -r file; do
        # Count public functions/classes (not starting with _)
        PUBLIC=$(grep -cE "^(def [^_]|class [^_])" "${file}" 2>/dev/null || echo 0)
        # Count those with docstrings (function/class followed by triple-quote)
        DOCUMENTED=$(grep -cE "^(def [^_]|class [^_]).*:$" "${file}" 2>/dev/null || echo 0)

        # Rough check: count triple-quote blocks after public definitions
        DOC_STRINGS=$(grep -cE '^\s+"""' "${file}" 2>/dev/null || echo 0)

        MISSING=$((PUBLIC - DOC_STRINGS))
        if [[ ${MISSING} -gt 0 ]] && [[ ${PUBLIC} -gt 0 ]]; then
            echo "  WARNING: ${file} — ${MISSING}/${PUBLIC} public items missing docstrings"
            UNDOCUMENTED=$((UNDOCUMENTED + MISSING))
            ISSUES=$((ISSUES + 1))
        fi
        TOTAL_PUBLIC=$((TOTAL_PUBLIC + PUBLIC))
    done <<< "${PY_FILES}"

    DOCUMENTED=$((TOTAL_PUBLIC - UNDOCUMENTED))
    if [[ ${TOTAL_PUBLIC} -gt 0 ]]; then
        PCT=$((DOCUMENTED * 100 / TOTAL_PUBLIC))
        echo ""
        echo "  Python docstring coverage: ${PCT}% (${DOCUMENTED}/${TOTAL_PUBLIC})"
    else
        echo "  No public Python functions/classes found."
    fi
else
    echo "  No Python files found."
fi
echo ""

# ─── 2. Module README coverage ────────────────────────────────────
echo "## Module README Coverage"
echo ""

# Find directories that contain source code but no README
SRC_DIRS=$(find "${SRC_DIR}" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" \
    -o -name "*.js" -o -name "*.jsx" -o -name "*.rs" -o -name "*.go" \
    -o -name "*.cpp" -o -name "*.c" \) \
    -not -path "*/test*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \
    -exec dirname {} \; 2>/dev/null | sort -u)

TOTAL_DIRS=0
MISSING_README=0

while IFS= read -r dir; do
    if [[ -z "${dir}" ]]; then continue; fi
    TOTAL_DIRS=$((TOTAL_DIRS + 1))
    if [[ ! -f "${dir}/README.md" ]] && [[ ! -f "${dir}/README.rst" ]]; then
        echo "  MISSING: ${dir}/README.md"
        MISSING_README=$((MISSING_README + 1))
        ISSUES=$((ISSUES + 1))
    fi
done <<< "${SRC_DIRS}"

WITH_README=$((TOTAL_DIRS - MISSING_README))
if [[ ${TOTAL_DIRS} -gt 0 ]]; then
    PCT=$((WITH_README * 100 / TOTAL_DIRS))
    echo ""
    echo "  Module README coverage: ${PCT}% (${WITH_README}/${TOTAL_DIRS} dirs)"
fi
echo ""

# ─── 3. Root documentation files ─────────────────────────────────
echo "## Required Project Files"
echo ""

REQUIRED_FILES=("README.md" "CHANGELOG.md" "LICENSE")
OPTIONAL_FILES=("CONTRIBUTING.md" "SECURITY.md" "CODE_OF_CONDUCT.md")

for f in "${REQUIRED_FILES[@]}"; do
    if [[ -f "${f}" ]]; then
        echo "  PASS: ${f} exists"
    else
        echo "  FAIL: ${f} missing (required)"
        ISSUES=$((ISSUES + 1))
    fi
done

for f in "${OPTIONAL_FILES[@]}"; do
    if [[ -f "${f}" ]]; then
        echo "  PASS: ${f} exists"
    else
        echo "  INFO: ${f} missing (recommended)"
    fi
done
echo ""

# ─── 4. Stale docs check (git-based) ─────────────────────────────
echo "## Stale Documentation Check"
echo ""

if git rev-parse --git-dir &>/dev/null; then
    # Find files changed in last 10 commits
    CHANGED_SRC=$(git log --oneline -10 --name-only --diff-filter=M -- \
        "*.py" "*.ts" "*.tsx" "*.js" "*.rs" "*.go" "*.cpp" "*.c" 2>/dev/null | \
        grep -E "\.(py|ts|tsx|js|rs|go|cpp|c)$" | sort -u)

    CHANGED_DOCS=$(git log --oneline -10 --name-only --diff-filter=M -- \
        "*.md" "*.rst" 2>/dev/null | grep -E "\.(md|rst)$" | sort -u)

    if [[ -n "${CHANGED_SRC}" ]] && [[ -z "${CHANGED_DOCS}" ]]; then
        echo "  WARNING: Source files changed in recent commits but no docs updated."
        echo "  Changed source files:"
        echo "${CHANGED_SRC}" | head -10 | sed 's/^/    /'
        ISSUES=$((ISSUES + 1))
    else
        echo "  PASS: Documentation appears up-to-date with recent changes."
    fi
else
    echo "  SKIP: Not a git repository."
fi
echo ""

# ─── Summary ──────────────────────────────────────────────────────
echo "========================================"
echo "Documentation Coverage: ${ISSUES} issue(s) found"
echo "========================================"

exit "${ISSUES}"
