"""
Continuous Frame Streaming Script

Captures continuous frames from the camera and displays frame rate.
Press Ctrl+C to stop.

Usage:
    python 05_continuous_stream.py [camera_id] [duration_seconds]

Default duration: 10 seconds
"""

import sys
import time
from typing import Any

import vmbpy


class FrameCounter:
    """Simple counter for frames captured during streaming."""

    def __init__(self) -> None:
        self.count = 0
        self.start_time = time.time()

    def increment(self) -> None:
        """Increment frame count."""
        self.count += 1

    def get_fps(self) -> float:
        """Calculate current FPS."""
        elapsed = time.time() - self.start_time
        return self.count / elapsed if elapsed > 0 else 0.0


def stream_frames(camera_id: str = None, duration: int = 10) -> None:
    """
    Capture continuous frames from camera.

    Args:
        camera_id: Optional camera ID. If None, uses first available camera.
        duration: Duration to capture in seconds.
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
            print(f"Using camera: {camera.get_id()}")

        with camera:
            counter = FrameCounter()
            print(f"\nStreaming for {duration} seconds...")
            print("Press Ctrl+C to stop early.\n")

            def on_frame(cam: Any, stream: Any, frame: Any) -> None:
                """Frame callback."""
                counter.increment()
                cam.queue_frame(frame)

            try:
                camera.start_streaming(on_frame)
                start_time = time.time()

                while time.time() - start_time < duration:
                    time.sleep(0.1)
                    elapsed = time.time() - start_time
                    if int(elapsed) % 2 == 0 and elapsed > 0.1:
                        fps = counter.get_fps()
                        print(f"Elapsed: {elapsed:.1f}s, Frames: {counter.count}, FPS: {fps:.2f}")

                camera.stop_streaming()

            except KeyboardInterrupt:
                print("\nStopping...")
                camera.stop_streaming()

            elapsed = time.time() - counter.start_time
            fps = counter.get_fps()

            print("\nCapture Complete:")
            print(f"  Duration:  {elapsed:.2f} seconds")
            print(f"  Frames:    {counter.count}")
            print(f"  Avg FPS:   {fps:.2f}")


if __name__ == "__main__":
    camera_id = sys.argv[1] if len(sys.argv) > 1 else None
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    try:
        stream_frames(camera_id, duration)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
