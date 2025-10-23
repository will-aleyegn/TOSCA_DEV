"""
Camera Detection Script

Detects and lists all Allied Vision cameras connected to the system.
Displays camera ID, model, and interface type.

Usage:
    python 01_list_cameras.py
"""

import sys

import vmbpy


def list_cameras() -> None:
    """
    Detect and list all connected Allied Vision cameras.

    Prints camera information including:
    - Camera ID (required for opening camera)
    - Model name
    - Interface type (USB, GigE, etc.)
    """
    vmb = vmbpy.VmbSystem.get_instance()

    with vmb:
        cameras = vmb.get_all_cameras()

        if not cameras:
            print("No cameras detected.")
            print("\nTroubleshooting:")
            print("- Check camera is powered on")
            print("- Check USB/network cable is connected")
            print("- Check camera drivers are installed")
            return

        print(f"Found {len(cameras)} camera(s):\n")

        for idx, camera in enumerate(cameras, 1):
            print(f"Camera {idx}:")
            print(f"  ID:        {camera.get_id()}")
            print(f"  Model:     {camera.get_model()}")
            print(f"  Interface: {camera.get_interface_id()}")
            print()


if __name__ == "__main__":
    try:
        list_cameras()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
