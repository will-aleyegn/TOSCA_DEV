#!/usr/bin/env python3
"""
Test camera streaming performance.

Measures actual frame rate and frame processing time to verify
performance optimizations in the main application.
"""

import sys
import time

import numpy as np

try:
    import vmbpy
except ImportError:
    print("ERROR: VmbPy not installed")
    print("Install with: pip install vmbpy")
    sys.exit(1)


def test_streaming_performance(duration_seconds: int = 5) -> None:
    """
    Test camera streaming performance.

    Args:
        duration_seconds: How long to stream for testing
    """
    print("=" * 60)
    print("Camera Streaming Performance Test")
    print("=" * 60)

    with vmbpy.VmbSystem.get_instance() as vmb:
        # Get camera
        cameras = vmb.get_all_cameras()
        if not cameras:
            print("ERROR: No cameras detected")
            return

        camera = cameras[0]
        print(f"\nCamera: {camera.get_id()}")
        print(f"Model: {camera.get_name()}")

        with camera:
            # Test streaming performance
            frame_count = 0
            start_time = time.time()
            processing_times = []

            def frame_callback(cam, stream, frame) -> None:  # type: ignore
                nonlocal frame_count, processing_times

                callback_start = time.time()

                try:
                    # Simulate main app processing (convert to numpy array)
                    _ = frame.as_numpy_ndarray()

                    # Measure processing time
                    processing_time = (time.time() - callback_start) * 1000  # ms
                    processing_times.append(processing_time)

                    frame_count += 1

                    # Show progress
                    if frame_count % 50 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        avg_processing = np.mean(processing_times[-50:])
                        print(
                            f"Frames: {frame_count:4d} | "
                            f"FPS: {fps:5.1f} | "
                            f"Avg Processing: {avg_processing:5.2f}ms"
                        )

                finally:
                    cam.queue_frame(frame)

            print(f"\nStreaming for {duration_seconds} seconds...")
            print("(Processing includes frame conversion only, no GUI scaling)\n")

            camera.start_streaming(frame_callback)
            time.sleep(duration_seconds)
            camera.stop_streaming()

            # Calculate statistics
            elapsed = time.time() - start_time
            avg_fps = frame_count / elapsed
            avg_processing = np.mean(processing_times)
            min_processing = np.min(processing_times)
            max_processing = np.max(processing_times)
            p95_processing = np.percentile(processing_times, 95)

            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Total Frames:        {frame_count}")
            print(f"Duration:            {elapsed:.2f}s")
            print(f"Average FPS:         {avg_fps:.1f}")
            print("\nFrame Processing Time:")
            print(f"  Average:           {avg_processing:.2f}ms")
            print(f"  Min:               {min_processing:.2f}ms")
            print(f"  Max:               {max_processing:.2f}ms")
            print(f"  95th percentile:   {p95_processing:.2f}ms")

            # Performance assessment
            print("\nPerformance Assessment:")
            if avg_fps >= 35:
                print("  EXCELLENT - Full frame rate achieved")
            elif avg_fps >= 25:
                print("  GOOD - Acceptable frame rate")
            elif avg_fps >= 15:
                print("  FAIR - Below optimal but usable")
            else:
                print("  POOR - Performance issues detected")

            if avg_processing < 5:
                print("  Frame processing is fast")
            elif avg_processing < 15:
                print("  Frame processing acceptable")
            else:
                print("  Frame processing is slow")

            print("\nNOTE: Main application adds GUI scaling overhead")
            print("      FastTransformation recommended for real-time display")


if __name__ == "__main__":
    print("\nTesting camera streaming performance...")
    print("This measures frame rate and processing time.\n")

    try:
        test_streaming_performance(duration_seconds=5)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
