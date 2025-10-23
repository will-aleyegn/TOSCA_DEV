"""
Camera Information Script

Opens a specific camera and displays detailed information about its capabilities.

Usage:
    python 02_camera_info.py [camera_id]

If no camera_id provided, uses first available camera.
"""

import sys

import vmbpy


def get_camera_info(camera_id: str = None) -> None:
    """
    Display detailed information about a specific camera.

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
            print(f"Using first available camera: {camera.get_id()}\n")

        with camera:
            print("Camera Information:")
            print(f"  ID:              {camera.get_id()}")
            print(f"  Model:           {camera.get_model()}")
            print(f"  Name:            {camera.get_name()}")
            print(f"  Serial Number:   {camera.get_serial()}")
            print(f"  Interface:       {camera.get_interface_id()}")

            print("\nImage Format:")
            try:
                width = camera.get_feature_by_name("Width")
                height = camera.get_feature_by_name("Height")
                pixel_format = camera.get_feature_by_name("PixelFormat")

                print(f"  Width:           {width.get()}")
                print(f"  Height:          {height.get()}")
                print(f"  Pixel Format:    {pixel_format.get()}")
            except vmbpy.VmbFeatureError as e:
                print(f"  Error reading image format: {e}")

            print("\nExposure Settings:")
            try:
                exposure_time = camera.get_feature_by_name("ExposureTime")
                exposure_auto = camera.get_feature_by_name("ExposureAuto")

                print(f"  Exposure Time:   {exposure_time.get()} µs")
                print(f"  Exposure Auto:   {exposure_auto.get()}")
            except vmbpy.VmbFeatureError as e:
                print(f"  Error reading exposure: {e}")

            print("\nGain Settings:")
            try:
                gain = camera.get_feature_by_name("Gain")
                print(f"  Gain:            {gain.get()}")
            except vmbpy.VmbFeatureError as e:
                print(f"  Error reading gain: {e}")


if __name__ == "__main__":
    camera_id = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        get_camera_info(camera_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
