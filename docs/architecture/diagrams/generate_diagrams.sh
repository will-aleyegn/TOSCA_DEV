#!/bin/bash
# TOSCA Architecture Diagram Generation Script
# Generates PNG and SVG images from PlantUML sources

set -e  # Exit on error

echo "========================================="
echo "TOSCA Architecture Diagram Generator"
echo "========================================="
echo ""

# Check for PlantUML JAR
PLANTUML_JAR="plantuml.jar"
PLANTUML_URL="https://sourceforge.net/projects/plantuml/files/plantuml.jar/download"

if [ ! -f "$PLANTUML_JAR" ]; then
    echo "PlantUML JAR not found. Downloading..."
    wget "$PLANTUML_URL" -O "$PLANTUML_JAR"
    echo "Download complete."
    echo ""
fi

# Check for Java
if ! command -v java &> /dev/null; then
    echo "ERROR: Java not found. Please install Java Runtime Environment (JRE) 8+."
    echo "  Ubuntu/Debian: sudo apt install default-jre"
    echo "  macOS: brew install openjdk"
    exit 1
fi

# Create output directories
mkdir -p output/png
mkdir -p output/svg

echo "Generating diagrams..."
echo ""

# Count .puml files
PUML_COUNT=$(find . -maxdepth 1 -name "*.puml" | wc -l)
echo "Found $PUML_COUNT PlantUML source files"
echo ""

# Generate PNG diagrams
echo "[1/2] Generating PNG images..."
java -jar "$PLANTUML_JAR" -tpng *.puml -o output/png
echo "  ✓ PNG images generated in output/png/"
echo ""

# Generate SVG diagrams
echo "[2/2] Generating SVG images..."
java -jar "$PLANTUML_JAR" -tsvg *.puml -o output/svg
echo "  ✓ SVG images generated in output/svg/"
echo ""

echo "========================================="
echo "Diagram generation complete!"
echo "========================================="
echo ""
echo "PNG images: $(ls output/png/*.png 2>/dev/null | wc -l) files"
echo "SVG images: $(ls output/svg/*.svg 2>/dev/null | wc -l) files"
echo ""
echo "To view diagrams:"
echo "  PNG: open output/png/"
echo "  SVG: open output/svg/"
