#!/usr/bin/env python3
"""
Resize PNG diagrams to maximum 8 inches (600 DPI for high quality).
Max dimension: 8 inches * 96 DPI = 768 pixels (standard screen DPI)
For print quality: 8 inches * 150 DPI = 1200 pixels
"""

from PIL import Image
from pathlib import Path

def resize_image_to_max_dimension(image_path, max_inches=8, dpi=150):
    """
    Resize image so largest dimension is max_inches at given DPI.

    Args:
        image_path: Path to image file
        max_inches: Maximum dimension in inches
        dpi: Dots per inch (150 for good print quality)
    """
    max_pixels = int(max_inches * dpi)

    img = Image.open(image_path)
    width, height = img.size

    # Check if resizing needed
    if width <= max_pixels and height <= max_pixels:
        print(f"  {image_path.name}: {width}x{height} - No resize needed")
        return False

    # Calculate new size maintaining aspect ratio
    if width > height:
        new_width = max_pixels
        new_height = int(height * (max_pixels / width))
    else:
        new_height = max_pixels
        new_width = int(width * (max_pixels / height))

    print(f"  {image_path.name}: {width}x{height} -> {new_width}x{new_height}")

    # Resize with high-quality resampling
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Save with high quality
    resized.save(image_path, quality=95, optimize=True)

    return True

def main():
    diagrams_dir = Path('/mnt/c/Users/wille/Desktop/TOSCA-dev/docs/architecture/diagrams/output/png')

    if not diagrams_dir.exists():
        print(f"Error: Diagrams directory not found: {diagrams_dir}")
        return

    png_files = list(diagrams_dir.glob('*.png'))
    print(f"Found {len(png_files)} PNG files\n")

    resized_count = 0
    for png_file in png_files:
        if resize_image_to_max_dimension(png_file):
            resized_count += 1

    print(f"\n{resized_count} images resized")
    print(f"{len(png_files) - resized_count} images already correct size")

if __name__ == '__main__':
    main()
