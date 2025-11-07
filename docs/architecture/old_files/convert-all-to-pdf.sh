#!/bin/bash
# convert-all-to-pdf.sh
# Converts all architecture markdown files to PDF
# Usage: ./convert-all-to-pdf.sh

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

OUTPUT_DIR="pdf-output"
CURRENT_DATE=$(date +%Y-%m-%d)

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo -e "${BLUE}Output directory: $OUTPUT_DIR${NC}"

# Check for pandoc
if ! command -v pandoc &> /dev/null; then
  echo -e "${RED}Error: pandoc is not installed${NC}"
  echo "Install with: sudo apt install pandoc (Ubuntu/Debian)"
  exit 1
fi

# Check for XeLaTeX (preferred) or fallback to wkhtmltopdf
PDF_ENGINE=""
if command -v xelatex &> /dev/null; then
  PDF_ENGINE="xelatex"
  echo -e "${GREEN}Using XeLaTeX engine (high quality)${NC}"
elif command -v wkhtmltopdf &> /dev/null; then
  PDF_ENGINE="wkhtmltopdf"
  echo -e "${YELLOW}Using wkhtmltopdf engine (fallback)${NC}"
  echo -e "${YELLOW}Install texlive-xetex for better quality: sudo apt install texlive-xetex${NC}"
else
  echo -e "${RED}Error: No PDF engine found${NC}"
  echo "Install one of:"
  echo "  - sudo apt install texlive-xetex (recommended)"
  echo "  - sudo apt install wkhtmltopdf"
  exit 1
fi

# Convert all numbered architecture docs
SUCCESS_COUNT=0
FAIL_COUNT=0

echo -e "\n${BLUE}Converting architecture documents...${NC}\n"

for MD_FILE in [0-9][0-9]_*.md; do
  if [ -f "$MD_FILE" ]; then
    OUTPUT_PDF="$OUTPUT_DIR/${MD_FILE%.md}.pdf"

    echo -e "${GREEN}Processing: $MD_FILE${NC}"

    if [ "$PDF_ENGINE" = "xelatex" ]; then
      if pandoc "$MD_FILE" -o "$OUTPUT_PDF" \
        --pdf-engine=xelatex \
        --variable mainfont="DejaVu Sans Mono" \
        --variable geometry:margin=1in \
        --toc \
        --toc-depth=3 \
        --number-sections \
        --metadata title="TOSCA Architecture Documentation" \
        --metadata date="$CURRENT_DATE" \
        --resource-path=".:diagrams/output/png:diagrams/output/svg" 2>&1; then
        echo -e "  ${GREEN}✓ Generated: $OUTPUT_PDF${NC}"
        ((SUCCESS_COUNT++))
      else
        echo -e "  ${RED}✗ Failed: $MD_FILE${NC}"
        ((FAIL_COUNT++))
      fi
    else
      # Fallback to wkhtmltopdf
      if pandoc "$MD_FILE" -o "$OUTPUT_PDF" \
        --pdf-engine=wkhtmltopdf \
        --toc \
        --toc-depth=3 \
        --number-sections \
        --metadata title="TOSCA Architecture Documentation" \
        --metadata date="$CURRENT_DATE" \
        --resource-path=".:diagrams/output/png:diagrams/output/svg" 2>&1; then
        echo -e "  ${GREEN}✓ Generated: $OUTPUT_PDF${NC}"
        ((SUCCESS_COUNT++))
      else
        echo -e "  ${RED}✗ Failed: $MD_FILE${NC}"
        ((FAIL_COUNT++))
      fi
    fi

    echo ""
  fi
done

# Convert additional important documents
echo -e "${BLUE}Converting additional documents...${NC}\n"

ADDITIONAL_DOCS=(
  "ADR-001-protocol-consolidation.md"
  "ADR-002-dependency-injection-pattern.md"
  "ADR-003-pyqt6-gui-framework.md"
  "ADR-004-sqlite-database.md"
  "ADR-005-arduino-gpio-migration.md"
  "ADR-006-selective-shutdown-policy.md"
  "SAFETY_SHUTDOWN_POLICY.md"
  "SECURITY_THREAT_MODEL.md"
  "QUALITY_ATTRIBUTES.md"
  "ARCHITECTURE_DOCUMENTATION_INDEX.md"
)

for MD_FILE in "${ADDITIONAL_DOCS[@]}"; do
  if [ -f "$MD_FILE" ]; then
    OUTPUT_PDF="$OUTPUT_DIR/${MD_FILE%.md}.pdf"

    echo -e "${GREEN}Processing: $MD_FILE${NC}"

    if [ "$PDF_ENGINE" = "xelatex" ]; then
      if pandoc "$MD_FILE" -o "$OUTPUT_PDF" \
        --pdf-engine=xelatex \
        --variable mainfont="DejaVu Sans Mono" \
        --variable geometry:margin=1in \
        --toc \
        --toc-depth=3 \
        --number-sections \
        --metadata title="TOSCA Architecture Documentation" \
        --metadata date="$CURRENT_DATE" \
        --resource-path=".:diagrams/output/png:diagrams/output/svg" 2>&1; then
        echo -e "  ${GREEN}✓ Generated: $OUTPUT_PDF${NC}"
        ((SUCCESS_COUNT++))
      else
        echo -e "  ${RED}✗ Failed: $MD_FILE${NC}"
        ((FAIL_COUNT++))
      fi
    else
      # Fallback to wkhtmltopdf
      if pandoc "$MD_FILE" -o "$OUTPUT_PDF" \
        --pdf-engine=wkhtmltopdf \
        --toc \
        --toc-depth=3 \
        --number-sections \
        --metadata title="TOSCA Architecture Documentation" \
        --metadata date="$CURRENT_DATE" \
        --resource-path=".:diagrams/output/png:diagrams/output/svg" 2>&1; then
        echo -e "  ${GREEN}✓ Generated: $OUTPUT_PDF${NC}"
        ((SUCCESS_COUNT++))
      else
        echo -e "  ${RED}✗ Failed: $MD_FILE${NC}"
        ((FAIL_COUNT++))
      fi
    fi

    echo ""
  fi
done

# Summary
echo -e "\n${BLUE}=== Conversion Summary ===${NC}"
echo -e "${GREEN}Successful: $SUCCESS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo -e "${BLUE}Output directory: $OUTPUT_DIR${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
  echo -e "\n${GREEN}All conversions completed successfully!${NC}"
  exit 0
else
  echo -e "\n${YELLOW}Some conversions failed. Check error messages above.${NC}"
  exit 1
fi
