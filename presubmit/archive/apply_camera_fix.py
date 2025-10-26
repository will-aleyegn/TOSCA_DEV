#!/usr/bin/env python3
"""
Script to apply the camera display bug fix to camera_widget.py

This script will:
1. Backup the original file
2. Apply the stride/bytes_per_line fix
3. Verify the changes were applied correctly
"""

import shutil
from datetime import datetime
from pathlib import Path


def main() -> int:
    # File paths
    widget_file = Path("C:/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py")
    backup_file = widget_file.with_suffix(f".py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    print("Camera Display Bug Fix Script")
    print("=" * 60)
    print(f"Target file: {widget_file}")
    print(f"Backup file: {backup_file}")
    print()

    # Check if file exists
    if not widget_file.exists():
        print(f"ERROR: File not found: {widget_file}")
        return 1

    # Create backup
    print("Creating backup...")
    shutil.copy2(widget_file, backup_file)
    print(f"Backup created: {backup_file}")
    print()

    # Read the file
    print("Reading file...")
    with open(widget_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the old code to replace
    old_code = """            # Convert to QImage
            if len(frame.shape) == 2:
                # Grayscale
                bytes_per_line = width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
                )
            else:
                # RGB
                channels = frame.shape[2]
                bytes_per_line = channels * width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )"""

    # Define the new code
    new_code = """            # Convert to QImage
            # Ensure frame is C-contiguous for QImage
            frame = np.ascontiguousarray(frame)

            if len(frame.shape) == 2:
                # Grayscale
                bytes_per_line = frame.strides[0]
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
                )
            else:
                # RGB - use actual stride from numpy array
                bytes_per_line = frame.strides[0]
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )"""

    # Check if old code exists
    if old_code not in content:
        print("WARNING: Could not find the exact code to replace.")
        print("The file may have already been modified or the line numbers changed.")
        print()
        print("Please manually apply the fix using CAMERA_FIX_INSTRUCTIONS.md")
        return 1

    # Apply the fix
    print("Applying fix...")
    new_content = content.replace(old_code, new_code)

    # Verify the replacement worked
    if new_content == content:
        print("ERROR: No changes were made. The replacement failed.")
        return 1

    # Write the fixed content
    print("Writing fixed file...")
    with open(widget_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print()
    print("=" * 60)
    print("SUCCESS! Camera display bug fix applied.")
    print()
    print("Changes made:")
    print("  - Added np.ascontiguousarray() to ensure C-contiguous memory")
    print("  - Changed bytes_per_line calculation to use frame.strides[0]")
    print()
    print("Next steps:")
    print("  1. Restart the TOSCA application")
    print("  2. Test the camera display")
    print("  3. Verify the full image is shown without glitching")
    print()
    print(f"If you need to revert: Copy {backup_file} back to {widget_file}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
