"""
Camera Features Exploration Script

Lists all available features (settings) for a camera.
Displays feature name, type, value, and accessibility.

Usage:
    python 04_explore_features.py [camera_id]
"""

import sys
from typing import Any, Optional, Tuple

import vmbpy


def get_feature_info(feature: Any) -> Optional[Tuple[str, str, str, bool]]:
    """
    Extract information from a camera feature.

    Args:
        feature: VmbPy feature object

    Returns:
        Tuple of (name, category, value, is_writeable) or None if error
    """
    try:
        name = feature.get_name()
        category = feature.get_category()
        is_readable = feature.is_readable()
        is_writeable = feature.is_writeable()

        if is_readable:
            try:
                value = feature.get()
                return (name, category, value, is_writeable)
            except Exception:
                return (name, category, "N/A", is_writeable)
    except Exception:
        pass
    return None


def print_feature_list(readable_features: list) -> None:
    """
    Print formatted list of readable features.

    Args:
        readable_features: List of feature tuples
    """
    print("=== Readable Features ===\n")
    for name, category, value, writable in sorted(readable_features):
        access = "R/W" if writable else "R"
        print(f"{name:30} [{access}] = {value}")
        if category:
            print(f"  Category: {category}")
        print()


def explore_features(camera_id: str = None) -> None:
    """
    List all available features for a camera.

    Args:
        camera_id: Optional camera ID. If None, uses first available camera.
    """
    vmb = vmbpy.VmbSystem.get_instance()

    with vmb:
        cameras = vmb.get_all_cameras()

        if not cameras:
            print("No cameras detected.")
            return

        if camera_id:
            camera = vmb.get_camera_by_id(camera_id)
        else:
            camera = cameras[0]
            print(f"Using camera: {camera.get_id()}\n")

        with camera:
            features = camera.get_all_features()
            print(f"Found {len(features)} features:\n")

            readable_features = []
            writable_count = 0

            for feature in features:
                info = get_feature_info(feature)
                if info:
                    readable_features.append(info)
                    if info[3]:
                        writable_count += 1

            print_feature_list(readable_features)

            print("\n=== Summary ===")
            print(f"Total Features:     {len(features)}")
            print(f"Readable Features:  {len(readable_features)}")
            print(f"Writable Features:  {writable_count}")


if __name__ == "__main__":
    camera_id = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        explore_features(camera_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
