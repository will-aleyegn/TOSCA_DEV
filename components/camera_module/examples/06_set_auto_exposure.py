"""
Auto Exposure Configuration Script

Enable or disable auto exposure on the camera.

Usage:
    python 06_set_auto_exposure.py [on|off|continuous|once]

Auto Exposure Modes:
    - Off: Manual exposure control
    - Once: Auto exposure runs once then locks
    - Continuous: Auto exposure continuously adjusts
"""

import sys

import vmbpy


def set_auto_exposure(camera_id: str = None, mode: str = "Continuous") -> None:
    """
    Configure auto exposure mode.

    Args:
        camera_id: Optional camera ID. If None, uses first available camera.
        mode: Auto exposure mode (Off, Once, Continuous)
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
            try:
                exposure_auto = camera.get_feature_by_name("ExposureAuto")
                exposure_time = camera.get_feature_by_name("ExposureTime")

                print("Current Settings:")
                print(f"  Exposure Auto:  {exposure_auto.get()}")
                print(f"  Exposure Time:  {exposure_time.get():.2f} µs\n")

                exposure_auto.set(mode)

                print(f"Auto Exposure set to: {mode}\n")

                print("New Settings:")
                print(f"  Exposure Auto:  {exposure_auto.get()}")
                print(f"  Exposure Time:  {exposure_time.get():.2f} µs")

                if mode in ["Once", "Continuous"]:
                    print(
                        "\nNote: Exposure time will adjust automatically based on scene brightness."
                    )

            except Exception as e:
                print(f"Error configuring auto exposure: {e}")


if __name__ == "__main__":
    camera_id = None
    mode = "Continuous"

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "off":
            mode = "Off"
        elif arg == "on" or arg == "continuous":
            mode = "Continuous"
        elif arg == "once":
            mode = "Once"
        else:
            print(f"Unknown mode: {arg}")
            print("Valid modes: off, on, continuous, once")
            sys.exit(1)

    try:
        set_auto_exposure(camera_id, mode)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
