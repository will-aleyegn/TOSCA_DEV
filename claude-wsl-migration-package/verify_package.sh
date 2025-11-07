#!/bin/bash
# Package Integrity Verification Script
# Run this to verify all files are present before copying to WSL

echo "=================================="
echo "Migration Package Verification"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# File list
REQUIRED_FILES=(
    "PACKAGE_INDEX.md"
    "MIGRATION_README.md"
    "MIGRATION_PACKAGE.md"
    "MEMORY_RESTORE_INSTRUCTIONS.md"
    "migrate_to_wsl.sh"
    "settings.json"
    "mcp.json.windows"
    "mcp.json.wsl"
    "verify_package.sh"
)

MISSING_FILES=()
FOUND_COUNT=0

echo "Checking package contents..."
echo ""

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
        FOUND_COUNT=$((FOUND_COUNT + 1))
    else
        echo -e "${RED}✗${NC} $file (MISSING)"
        MISSING_FILES+=("$file")
    fi
done

echo ""
echo "=================================="
echo "Summary"
echo "=================================="
echo "Files found: $FOUND_COUNT / ${#REQUIRED_FILES[@]}"

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ Package is complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Copy this entire folder to WSL"
    echo "2. Run: bash migrate_to_wsl.sh"
    exit 0
else
    echo -e "${RED}✗ Package is incomplete!${NC}"
    echo ""
    echo "Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi
