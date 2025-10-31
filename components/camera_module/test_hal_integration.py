#!/usr/bin/env python3
"""
Quick validation test for Camera HAL integration.

Tests basic camera controller functionality without requiring the full GUI.
Use this for quick validation before running full GUI tests.
"""

import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_camera_connection() -> bool:
    """Test basic camera connection."""
    logger.info("=" * 60)
    logger.info("Test 1: Camera Connection")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        logger.info("Camera controller created")

        # Test connection
        success = controller.connect()
        if not success:
            logger.error("Failed to connect to camera")
            return False

        logger.info("# [DONE] Camera connected successfully")

        # Test disconnect
        controller.disconnect()
        logger.info("# [DONE] Camera disconnected successfully")

        return True

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def test_camera_info() -> bool:
    """Test camera information retrieval."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Camera Information")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        controller.connect()

        info = controller.get_camera_info()
        if info:
            logger.info(f"Camera ID: {info.camera_id}")
            logger.info(f"Model: {info.model}")
            logger.info(f"Serial: {info.serial_number}")
            logger.info(f"Interface: {info.interface}")
            logger.info(f"Max Resolution: {info.max_resolution}")
            logger.info(f"Max FPS: {info.max_fps}")
            logger.info("# [DONE] Camera info retrieved successfully")
            result = True
        else:
            logger.error("Failed to get camera info")
            result = False

        controller.disconnect()
        return result

    except Exception as e:
        logger.error(f"Camera info test failed: {e}")
        return False


def test_exposure_gain_ranges() -> bool:
    """Test exposure and gain range retrieval."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Exposure and Gain Ranges")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        controller.connect()

        # Get exposure range
        exp_min, exp_max = controller.get_exposure_range()
        logger.info(f"Exposure range: {exp_min} - {exp_max} µs")

        # Get gain range
        gain_min, gain_max = controller.get_gain_range()
        logger.info(f"Gain range: {gain_min} - {gain_max} dB")

        if exp_max > exp_min and gain_max >= gain_min:
            logger.info("# [DONE] Ranges retrieved successfully")
            result = True
        else:
            logger.error("Invalid ranges")
            result = False

        controller.disconnect()
        return result

    except Exception as e:
        logger.error(f"Range test failed: {e}")
        return False


def test_streaming_brief() -> bool:
    """Test brief streaming (5 seconds)."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Brief Streaming Test (5 seconds)")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        controller.connect()

        frame_count = [0]  # Use list to modify in callback

        def count_frames(frame):  # type: ignore
            frame_count[0] += 1

        # Connect frame signal
        controller.frame_ready.connect(count_frames)

        # Start streaming
        success = controller.start_streaming()
        if not success:
            logger.error("Failed to start streaming")
            controller.disconnect()
            return False

        logger.info("Streaming started, collecting frames...")

        # Stream for 5 seconds
        time.sleep(5)

        # Stop streaming
        controller.stop_streaming()

        fps = frame_count[0] / 5.0
        logger.info(f"Frames received: {frame_count[0]}")
        logger.info(f"Average FPS: {fps:.1f}")

        if fps >= 30:
            logger.info("# [DONE] Streaming test passed (FPS >= 30)")
            result = True
        else:
            logger.warning(f"Low FPS detected: {fps:.1f}")
            result = False

        controller.disconnect()
        return result

    except Exception as e:
        logger.error(f"Streaming test failed: {e}")
        return False


def test_exposure_control() -> bool:
    """Test exposure control."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: Exposure Control")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        controller.connect()

        # Test manual exposure
        test_values = [5000, 10000, 20000]
        for exp_value in test_values:
            success = controller.set_exposure(exp_value)
            if success:
                logger.info(f"# [DONE] Set exposure to {exp_value} µs")
            else:
                logger.error(f"Failed to set exposure to {exp_value} µs")
                controller.disconnect()
                return False

        # Test auto exposure
        success_auto = controller.set_auto_exposure(True)
        if success_auto:
            logger.info("# [DONE] Auto exposure enabled")
        else:
            logger.warning("Auto exposure may not be supported")

        controller.set_auto_exposure(False)
        logger.info("# [DONE] Auto exposure disabled")

        controller.disconnect()
        logger.info("# [DONE] Exposure control test passed")
        return True

    except Exception as e:
        logger.error(f"Exposure control test failed: {e}")
        return False


def test_gain_control() -> bool:
    """Test gain control."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 6: Gain Control")
    logger.info("=" * 60)

    try:
        from hardware.camera_controller import CameraController

        controller = CameraController()
        controller.connect()

        # Test manual gain
        test_values = [0.0, 6.0, 12.0]
        for gain_value in test_values:
            success = controller.set_gain(gain_value)
            if success:
                logger.info(f"# [DONE] Set gain to {gain_value} dB")
            else:
                logger.error(f"Failed to set gain to {gain_value} dB")
                controller.disconnect()
                return False

        # Test auto gain
        success_auto = controller.set_auto_gain(True)
        if success_auto:
            logger.info("# [DONE] Auto gain enabled")
        else:
            logger.warning("Auto gain may not be supported")

        controller.set_auto_gain(False)
        logger.info("# [DONE] Auto gain disabled")

        controller.disconnect()
        logger.info("# [DONE] Gain control test passed")
        return True

    except Exception as e:
        logger.error(f"Gain control test failed: {e}")
        return False


def main() -> int:
    """Run all validation tests."""
    logger.info("\n" + "=" * 60)
    logger.info("Camera HAL Integration Test")
    logger.info("=" * 60)
    logger.info("This script tests basic camera controller functionality")
    logger.info("Ensure Allied Vision camera is connected before running")
    logger.info("=" * 60 + "\n")

    tests = [
        ("Camera Connection", test_camera_connection),
        ("Camera Information", test_camera_info),
        ("Exposure/Gain Ranges", test_exposure_gain_ranges),
        ("Brief Streaming", test_streaming_brief),
        ("Exposure Control", test_exposure_control),
        ("Gain Control", test_gain_control),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

        time.sleep(1)  # Brief pause between tests

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = 0
    failed = 0
    for test_name, result in results.items():
        status = "# [DONE] PASS" if result else "# [FAILED] FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info("=" * 60)
    logger.info(f"Total: {passed} passed, {failed} failed out of {len(tests)} tests")
    logger.info("=" * 60)

    if failed == 0:
        logger.info("\n# [DONE] All tests passed! Camera HAL is working correctly.")
        logger.info("You can now proceed to full GUI testing.")
        return 0
    else:
        logger.warning(f"\n# [FAILED] {failed} test(s) failed. Review logs and fix issues.")
        logger.info("Check data/logs/tosca.log for detailed error information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
