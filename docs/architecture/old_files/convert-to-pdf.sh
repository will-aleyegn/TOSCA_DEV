#!/bin/bash
# convert-to-pdf.sh
# Converts a single markdown file to high-quality PDF
# Usage: ./convert-to-pdf.sh <markdown_file.md>

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -eq 0 ]; then
  echo -e "${RED}Error: No input file specified${NC}"
  echo "Usage: $0 <markdown_file.md>"
  exit 1
fi

MARKDOWN_FILE="$1"
OUTPUT_PDF="${MARKDOWN_FILE%.md}.pdf"

# Check if file exists
if [ ! -f "$MARKDOWN_FILE" ]; then
  echo -e "${RED}Error: File not found: $MARKDOWN_FILE${NC}"
  exit 1
fi

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

# Convert to PDF
echo -e "${GREEN}Converting: $MARKDOWN_FILE → $OUTPUT_PDF${NC}"

if [ "$PDF_ENGINE" = "xelatex" ]; then
  pandoc "$MARKDOWN_FILE" -o "$OUTPUT_PDF" \
    --pdf-engine=xelatex \
    --variable mainfont="DejaVu Sans Mono" \
    --variable geometry:margin=1in \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --metadata title="TOSCA Architecture Documentation" \
    --metadata date="$(date +%Y-%m-%d)" \
    --resource-path=".:diagrams/output/png:diagrams/output/svg"
else
  # Fallback to wkhtmltopdf
  pandoc "$MARKDOWN_FILE" -o "$OUTPUT_PDF" \
    --pdf-engine=wkhtmltopdf \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --metadata title="TOSCA Architecture Documentation" \
    --metadata date="$(date +%Y-%m-%d)" \
    --resource-path=".:diagrams/output/png:diagrams/output/svg"
fi

if [ $? -eq 0 ]; then
  echo -e "${GREEN}Successfully generated: $OUTPUT_PDF${NC}"
  ls -lh "$OUTPUT_PDF"
else
  echo -e "${RED}Error during PDF generation${NC}"
  exit 1
fi
