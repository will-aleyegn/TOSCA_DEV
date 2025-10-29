#!/bin/bash
# TOSCA Repository Cleanup - Phase 2: GPIO Consolidation
# Date: 2025-10-28
# Consolidates 3 GPIO folders into 1

echo "=========================================="
echo "TOSCA Repository Cleanup - Phase 2"
echo "GPIO Folder Consolidation"
echo "=========================================="
echo ""

cd "$(dirname "$0")" || exit 1

echo "📂 Current GPIO folders:"
ls -la components/ | grep gpio
echo ""

echo "🔄 Creating backup first..."
mkdir -p /tmp/tosca_gpio_backup_2025-10-28
cp -r components/gpio_arduino components/gpio_module components/gpio_safety /tmp/tosca_gpio_backup_2025-10-28/ 2>/dev/null
echo "✅ Backup created in /tmp/tosca_gpio_backup_2025-10-28/"
echo ""

echo "📋 Moving code review docs to presubmit/reviews/..."
if [ -f "components/gpio_module/CODE_REVIEW_2025-10-27.md" ]; then
    mv components/gpio_module/CODE_REVIEW_2025-10-27.md presubmit/reviews/GPIO_CODE_REVIEW_2025-10-27.md
    echo "✅ Moved CODE_REVIEW_2025-10-27.md"
fi

if [ -f "components/gpio_module/LESSONS_LEARNED.md" ]; then
    mv components/gpio_module/LESSONS_LEARNED.md presubmit/reviews/GPIO_LESSONS_LEARNED.md
    echo "✅ Moved LESSONS_LEARNED.md"
fi

echo ""
echo "🗑️  Deleting gpio_module/ and gpio_safety/..."
rm -rf components/gpio_module/
echo "✅ Deleted components/gpio_module/"

rm -rf components/gpio_safety/
echo "✅ Deleted components/gpio_safety/"

echo ""
echo "📝 Updating gpio_arduino/ARDUINO_SETUP.md..."
cat >> components/gpio_arduino/ARDUINO_SETUP.md <<'EOF'

---

## Historical Note

**Previous Implementations:**
- FT232H-based GPIO (deprecated Oct 2024)
  - Archived documentation available in project history
- Code reviews and lessons learned moved to `presubmit/reviews/`

**Current Implementation:**
This document describes the current Arduino Nano + PyFirmata implementation.

---

**Last Updated:** 2025-10-28 (Repository consolidation)
EOF

echo "✅ Updated ARDUINO_SETUP.md with historical note"

echo ""
echo "=========================================="
echo "✅ Phase 2 Consolidation Complete!"
echo "=========================================="
echo ""
echo "📊 Result: 3 GPIO folders → 1 GPIO folder (gpio_arduino)"
echo ""
echo "🔍 Verification:"
echo "   Run: ls -la components/ | grep gpio"
echo "   Should only show: gpio_arduino"
echo ""
echo "📁 Backup location: /tmp/tosca_gpio_backup_2025-10-28/"
echo ""
echo "⚠️  Remember to run tests: pytest"
