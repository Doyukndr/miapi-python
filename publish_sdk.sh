#!/bin/bash
# ============================================================
# MIAPI SDK — Build & Publish to PyPI
# ============================================================
# 
# BEFORE RUNNING:
# 1. Create a PyPI account at https://pypi.org/account/register/
# 2. Go to https://pypi.org/manage/account/token/
# 3. Create an API token (scope: entire account)
# 4. Save the token (starts with "pypi-")
#
# THEN RUN:
#   bash publish_sdk.sh
# ============================================================

set -e

echo "============================================"
echo "  MIAPI SDK — Build & Publish"
echo "============================================"
echo ""

# Check if token is set
if [ -z "$1" ]; then
    echo "Usage: bash publish_sdk.sh YOUR_PYPI_TOKEN"
    echo ""
    echo "Steps:"
    echo "  1. Go to https://pypi.org/account/register/ and create account"
    echo "  2. Go to https://pypi.org/manage/account/token/"
    echo "  3. Create API token, copy it"
    echo "  4. Run: bash publish_sdk.sh pypi-YOUR_TOKEN_HERE"
    exit 1
fi

PYPI_TOKEN="$1"

echo "[1] Installing build tools..."
pip install build twine --quiet

echo "[2] Building package..."
cd /opt/miapi-sdk
python3 -m build

echo "[3] Uploading to PyPI..."
python3 -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN"

echo ""
echo "============================================"
echo "  ✅ Published! Try it:"
echo "  pip install miapi"
echo "============================================"
