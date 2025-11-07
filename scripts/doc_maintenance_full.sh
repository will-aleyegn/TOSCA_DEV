#!/bin/bash
# TOSCA Documentation Full Maintenance Script
# Runs all automated fixes and generates comprehensive report

set -e

echo "🔧 TOSCA Documentation Maintenance System"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")/.."

echo "📍 Working directory: $(pwd)"
echo ""

# Step 1: Run audit (before fixes)
echo "📊 Step 1: Running initial audit..."
python3 scripts/doc_maintenance.py --score-only > /tmp/score_before.txt
SCORE_BEFORE=$(grep "Quality Score:" /tmp/score_before.txt | awk '{print $3}' | cut -d'/' -f1)
echo "   Initial Quality Score: $SCORE_BEFORE/100"
echo ""

# Step 2: Fix dates
echo "🗓️  Step 2: Adding missing dates..."
python3 scripts/doc_fix_dates.py
echo ""

# Step 3: Fix code blocks
echo "💻 Step 3: Adding language specifications to code blocks..."
python3 scripts/doc_fix_code_blocks.py
echo ""

# Step 4: Run audit (after fixes)
echo "📊 Step 4: Running final audit..."
python3 scripts/doc_maintenance.py
python3 scripts/doc_maintenance.py --score-only > /tmp/score_after.txt
SCORE_AFTER=$(grep "Quality Score:" /tmp/score_after.txt | awk '{print $3}' | cut -d'/' -f1)
echo "   Final Quality Score: $SCORE_AFTER/100"
echo ""

# Calculate improvement
IMPROVEMENT=$((SCORE_AFTER - SCORE_BEFORE))
echo "=========================================="
echo "✅ Maintenance Complete!"
echo ""
echo "   Before:      $SCORE_BEFORE/100"
echo "   After:       $SCORE_AFTER/100"
if [ $IMPROVEMENT -gt 0 ]; then
    echo "   Improvement: +$IMPROVEMENT points 📈"
elif [ $IMPROVEMENT -lt 0 ]; then
    echo "   Change:      $IMPROVEMENT points 📉"
else
    echo "   No change    ➡️"
fi
echo ""
echo "📄 Reports available at:"
echo "   - docs/DOCUMENTATION_MAINTENANCE_REPORT.md"
echo "   - docs/reports/doc_audit_*.json"
echo ""

# Cleanup
rm /tmp/score_before.txt /tmp/score_after.txt

exit 0
