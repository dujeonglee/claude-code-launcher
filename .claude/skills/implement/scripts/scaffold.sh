#!/usr/bin/env bash
# scaffold.sh — Create a new module skeleton following project conventions.
#
# Usage:
#   ./scaffold.sh <language> <module_name> [output_dir]
#
# Example:
#   ./scaffold.sh python user_service src/services/
#   ./scaffold.sh typescript PaymentForm src/components/
#   ./scaffold.sh cpp WifiDriver src/drivers/

set -euo pipefail

LANG="${1:?Usage: scaffold.sh <language> <module_name> [output_dir]}"
MODULE="${2:?Usage: scaffold.sh <language> <module_name> [output_dir]}"
OUTDIR="${3:-.}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/templates"

mkdir -p "${OUTDIR}"

case "${LANG}" in
    python|py)
        # Create Python module with __init__.py and test stub
        MODULE_DIR="${OUTDIR}/${MODULE}"
        mkdir -p "${MODULE_DIR}"
        touch "${MODULE_DIR}/__init__.py"

        cat > "${MODULE_DIR}/${MODULE}.py" << 'PYEOF'
"""${MODULE} module."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__: list[str] = []
PYEOF

        # Test stub
        TEST_DIR="${OUTDIR}/tests"
        mkdir -p "${TEST_DIR}"
        cat > "${TEST_DIR}/test_${MODULE}.py" << PYTEST
"""Tests for ${MODULE}."""

import pytest

class TestPlaceholder:
    def test_placeholder(self):
        """Remove this — placeholder to verify test discovery."""
        assert True
PYTEST

        echo "Created Python module: ${MODULE_DIR}/"
        echo "Created test file: ${TEST_DIR}/test_${MODULE}.py"
        ;;

    typescript|ts|tsx)
        cat > "${OUTDIR}/${MODULE}.tsx" << 'TSEOF'
// TODO: Implement component
export {};
TSEOF

        cat > "${OUTDIR}/${MODULE}.test.tsx" << TSTEST
import { describe, it, expect } from "vitest";

describe("${MODULE}", () => {
  it("placeholder", () => {
    expect(true).toBe(true);
  });
});
TSTEST

        echo "Created TypeScript files in ${OUTDIR}/"
        ;;

    cpp|c++)
        cat > "${OUTDIR}/${MODULE}.h" << 'HEOF'
#pragma once
// TODO: Implement header
HEOF

        cat > "${OUTDIR}/${MODULE}.cpp" << 'CEOF'
// TODO: Implement module
CEOF

        echo "Created C++ files in ${OUTDIR}/"
        ;;

    *)
        echo "Unsupported language: ${LANG}"
        echo "Supported: python, typescript, cpp"
        exit 1
        ;;
esac

echo "Done. Remember to:"
echo "  1. Fill in the implementation"
echo "  2. Write real tests"
echo "  3. Run linter/formatter"
