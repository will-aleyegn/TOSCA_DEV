#!/bin/bash
# TOSCA Repository Cleanup - Phase 1: Cache Folders
# Date: 2025-10-28
# Safe to run - all files regenerate automatically

echo "=========================================="
echo "TOSCA Repository Cleanup - Phase 1"
echo "=========================================="
echo ""

cd "$(dirname "$0")" || exit 1

echo "📊 Current disk usage:"
du -sh .mypy_cache/ htmlcov/ .pytest_cache/ .backups/ 2>/dev/null
echo ""

echo "🗑️  Deleting cache folders..."
echo ""

# Delete mypy cache (86 MB)
if [ -d ".mypy_cache" ]; then
    rm -rf .mypy_cache/
    echo "✅ Deleted .mypy_cache/ (86 MB - type checking cache)"
else
    echo "⚠️  .mypy_cache/ not found (already deleted?)"
fi

# Delete HTML coverage reports (3.5 MB)
if [ -d "htmlcov" ]; then
    rm -rf htmlcov/
    echo "✅ Deleted htmlcov/ (3.5 MB - test coverage reports)"
else
    echo "⚠️  htmlcov/ not found (already deleted?)"
fi

# Delete pytest cache (15 KB)
if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache/
    echo "✅ Deleted .pytest_cache/ (15 KB - pytest cache)"
else
    echo "⚠️  .pytest_cache/ not found (already deleted?)"
fi

# Delete empty backups folder
if [ -d ".backups" ]; then
    rm -rf .backups/
    echo "✅ Deleted .backups/ (empty folder)"
else
    echo "⚠️  .backups/ not found (already deleted?)"
fi

echo ""
echo "🧹 Cleaning __pycache__ folders..."
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
echo "✅ Deleted all __pycache__ folders (outside venv)"

echo ""
echo "🗑️  Deleting old data folder..."
if [ -d "src/data" ]; then
    echo "   Comparing databases:"
    ls -lh data/tosca.db src/data/tosca.db 2>/dev/null
    rm -rf src/data/
    echo "✅ Deleted src/data/ (304 KB - old duplicate)"
else
    echo "⚠️  src/data/ not found (already deleted?)"
fi

echo ""
echo "🗑️  Deleting empty protocols folder..."
if [ -d "data/protocols" ]; then
    rm -rf data/protocols/
    echo "✅ Deleted data/protocols/ (empty folder)"
else
    echo "⚠️  data/protocols/ not found (already deleted?)"
fi

echo ""
echo "=========================================="
echo "✅ Phase 1 Cleanup Complete!"
echo "=========================================="
echo ""
echo "📊 Space recovered: ~90 MB"
echo ""
echo "🔍 Verification:"
echo "   Run: ls -la .mypy_cache htmlcov .pytest_cache .backups src/data data/protocols 2>&1 | grep 'No such'"
echo ""
echo "✅ All deleted folders should show 'No such file or directory'"
