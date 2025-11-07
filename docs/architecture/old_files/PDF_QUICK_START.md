# TOSCA PDF Generation - Quick Start Guide

**Purpose:** Get high-quality PDFs from architecture markdown files in 5 minutes

---

## TL;DR - Fastest Path to PDF

```bash
# Navigate to architecture docs
cd /mnt/c/Users/wille/Desktop/TOSCA-dev/docs/architecture

# Single file conversion
./convert-to-pdf.sh 01_system_overview.md

# All files conversion
./convert-all-to-pdf.sh

# Output in: pdf-output/
```

---

## Prerequisites (One-Time Setup)

### Option 1: XeLaTeX (Recommended - Best Quality)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install pandoc texlive-xetex fonts-dejavu
```

**macOS:**
```bash
brew install pandoc
brew install --cask mactex
```

**Windows (WSL2):**
```bash
sudo apt update
sudo apt install pandoc texlive-xetex fonts-dejavu
```

### Option 2: wkhtmltopdf (Alternative - Easier Install)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install pandoc wkhtmltopdf
```

**macOS:**
```bash
brew install pandoc
brew install --cask wkhtmltopdf
```

**Check Installation:**
```bash
pandoc --version
xelatex --version   # or wkhtmltopdf --version
```

---

## Usage

### Convert Single File

```bash
./convert-to-pdf.sh 03_safety_system.md
```

**Output:** `03_safety_system.pdf` (same directory)

### Convert All Architecture Docs

```bash
./convert-all-to-pdf.sh
```

**Output:** `pdf-output/` directory with all PDFs

### Custom Conversion

```bash
# With table of contents
pandoc 01_system_overview.md -o output.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  --number-sections

# With custom CSS (wkhtmltopdf)
pandoc 03_safety_system.md -o output.pdf \
  --pdf-engine=wkhtmltopdf \
  --css=pdf-styles.css

# With metadata
pandoc 01_system_overview.md -o output.pdf \
  --pdf-engine=xelatex \
  --metadata title="TOSCA System Overview" \
  --metadata author="Your Name" \
  --metadata date="$(date +%Y-%m-%d)"
```

---

## Troubleshooting

### Issue: "pandoc: command not found"

**Fix:**
```bash
sudo apt install pandoc   # Ubuntu/Debian
brew install pandoc       # macOS
```

### Issue: "xelatex not found"

**Fix:**
```bash
sudo apt install texlive-xetex   # Ubuntu/Debian
brew install --cask mactex       # macOS
```

### Issue: "Image not found"

**Fix:** Check relative path from markdown file location
```bash
# Verify image exists
ls diagrams/output/png/*.png

# Use absolute path if needed
pandoc file.md -o file.pdf \
  --resource-path="/full/path/to/diagrams/output/png"
```

### Issue: "Box drawing characters render as squares"

**Fix:** Install Unicode fonts
```bash
sudo apt install fonts-dejavu fonts-liberation   # Ubuntu/Debian
brew tap homebrew/cask-fonts && brew install --cask font-dejavu-sans-mono   # macOS
```

### Issue: "PDF generation fails silently"

**Fix:** Check for verbose errors
```bash
pandoc file.md -o file.pdf --pdf-engine=xelatex --verbose
```

---

## Improving ASCII Diagram Rendering

### Current Problem

ASCII diagrams with box drawing characters (┌─┐│└┘├┤┬┴┼) render poorly in PDF.

### Quick Fix: Use XeLaTeX

XeLaTeX has better Unicode support than wkhtmltopdf:

```bash
./convert-to-pdf.sh file.md   # Auto-detects XeLaTeX if available
```

### Best Fix: Replace with PlantUML Images

See `PDF_GENERATION_GUIDE.md` and `DIAGRAM_INTEGRATION_EXAMPLE.md` for details.

**Short version:**
1. Use existing PlantUML images in `diagrams/output/png/`
2. Replace ASCII diagrams with image references:
   ```markdown
   ![Architecture Diagram](diagrams/output/png/TOSCA%20Container%20Diagram.png)
   ```
3. Regenerate PDF:
   ```bash
   ./convert-to-pdf.sh file.md
   ```

---

## Available PlantUML Diagrams

**Location:** `diagrams/output/png/`

| File | Description |
|------|-------------|
| `TOSCA System Context.png` | C4 context diagram (external systems) |
| `TOSCA Container Diagram.png` | C4 container diagram (UI, Core, HAL layers) |
| `TOSCA Component Diagram - Application Core.png` | Core components (Safety, Session, Protocol) |
| `TOSCA Component Diagram - Hardware Abstraction Layer.png` | HAL components (Camera, Laser, TEC, Actuator, GPIO) |
| `TOSCA Data Architecture.png` | Two-tier logging strategy (JSONL + SQLite) |
| `TOSCA Data Flow Diagram.png` | System data flow |
| `TOSCA Database Schema ERD.png` | Database entity-relationship diagram |
| `TOSCA Treatment Workflow Sequence.png` | Treatment execution sequence |

**Usage:**
```markdown
![Architecture](diagrams/output/png/TOSCA%20Container%20Diagram.png)
```

---

## Batch Operations

### Convert All Numbered Docs

```bash
for f in [0-9][0-9]_*.md; do
  ./convert-to-pdf.sh "$f"
done
```

### Convert All ADRs

```bash
for f in ADR-*.md; do
  ./convert-to-pdf.sh "$f"
done
```

### Convert Specific Files

```bash
files=(
  "01_system_overview.md"
  "03_safety_system.md"
  "08_security_architecture.md"
)

for f in "${files[@]}"; do
  ./convert-to-pdf.sh "$f"
done
```

---

## PDF Output Quality Comparison

| Method | Quality | Speed | Setup Difficulty |
|--------|---------|-------|------------------|
| XeLaTeX (recommended) | Excellent | Slow | Medium |
| wkhtmltopdf | Good | Fast | Easy |
| XeLaTeX + Images | Excellent | Slow | Medium |

**Recommendation:** Use XeLaTeX with PlantUML images for best quality.

---

## Next Steps

1. **Test basic conversion:**
   ```bash
   ./convert-to-pdf.sh 01_system_overview.md
   ```

2. **Review output quality:**
   ```bash
   xdg-open 01_system_overview.pdf   # Linux
   ```

3. **Replace ASCII diagrams with images** (see `DIAGRAM_INTEGRATION_EXAMPLE.md`)

4. **Generate complete documentation set:**
   ```bash
   ./convert-all-to-pdf.sh
   ```

5. **Review detailed guide** for advanced options: `PDF_GENERATION_GUIDE.md`

---

## Common Commands Reference

```bash
# Single file with TOC
pandoc file.md -o file.pdf --pdf-engine=xelatex --toc

# All files with progress
./convert-all-to-pdf.sh

# Custom output directory
mkdir -p custom-output
pandoc file.md -o custom-output/file.pdf --pdf-engine=xelatex

# Test image rendering
echo '![Test](diagrams/output/png/TOSCA%20System%20Context.png)' | \
  pandoc -o test.pdf --pdf-engine=xelatex

# Check pandoc supported formats
pandoc --list-output-formats

# Check available PDF engines
pandoc --list-extensions=pdf
```

---

## Support

- **Full Documentation:** `PDF_GENERATION_GUIDE.md`
- **Integration Examples:** `DIAGRAM_INTEGRATION_EXAMPLE.md`
- **PlantUML Diagrams:** `diagrams/README.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-05
**Author:** Documentation Team
