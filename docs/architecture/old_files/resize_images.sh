#!/bin/bash
# Resize PNG diagrams to maximum 8 inches at 150 DPI (1200 pixels)

cd diagrams/output/png || exit 1

MAX_SIZE=1200  # 8 inches * 150 DPI

echo "Resizing PNG diagrams to ${MAX_SIZE}x${MAX_SIZE} max..."
echo ""

for img in *.png; do
    if [ -f "$img" ]; then
        # Get current dimensions
        current=$(identify -format "%wx%h" "$img")

        # Resize maintaining aspect ratio, only if larger than max
        convert "$img" -resize "${MAX_SIZE}x${MAX_SIZE}>" -quality 95 "$img"

        # Get new dimensions
        new=$(identify -format "%wx%h" "$img")

        echo "$img: $current -> $new"
    fi
done

echo ""
echo "Done!"
