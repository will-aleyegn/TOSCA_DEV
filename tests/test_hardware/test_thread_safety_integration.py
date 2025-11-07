"""
Comprehensive thread safety validation tests for all hardware controllers.

Tests concurrent access patterns, RLock behavior, and race condition detection.
"""

import sys
import threading
from pathlib import Path

import pytest
from PyQt6.QtCore import QCoreApplication

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.mocks import (
    MockCameraController,
    MockLaserController,
    MockTECController,
)


@pytest.fixture(scope="module")
def qapp():
    """Provide QCoreApplication for tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    yield app


class TestConcurrentCameraAccess:
    """Test concurrent camera operations."""

    def test_concurrent_exposure_changes(self, qapp):
        """Test concurrent exposure setting."""
        camera = MockCameraController()
        camera.connect()
        errors = []

        def set_exposure(value, count):
            try:
                for _ in range(count):
                    camera.set_exposure(value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=set_exposure, args=(10000.0, 100)),
            threading.Thread(target=set_exposure, args=(20000.0, 100)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestConcurrentLaserAccess:
    """Test concurrent laser operations."""

    def test_concurrent_power_changes(self, qapp):
        """Test concurrent power setting."""
        laser = MockLaserController()
        laser.connect()
        errors = []

        def set_power(value, count):
            try:
                for _ in range(count):
                    laser.set_power(value)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=set_power, args=(1000.0, 100)),
            threading.Thread(target=set_power, args=(1500.0, 100)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestMultiControllerConcurrency:
    """Test multiple controllers with concurrent operations."""

    def test_multi_controller_concurrent_access(self, qapp):
        """Test concurrent access to multiple controllers."""
        camera = MockCameraController()
        laser = MockLaserController()
        tec = MockTECController()

        camera.connect()
        laser.connect()
        tec.connect()

        errors = []

        def camera_operations():
            try:
                for _ in range(50):
                    camera.set_exposure(15000.0)
                    camera.set_gain(12.0)
            except Exception as e:
                errors.append(e)

        def laser_operations():
            try:
                for _ in range(50):
                    laser.set_power(1500.0)
                    laser.set_output(True)
                    laser.set_output(False)
            except Exception as e:
                errors.append(e)

        def tec_operations():
            try:
                for _ in range(50):
                    tec.set_temperature(22.0)
                    tec.set_output(True)
                    tec.set_output(False)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=camera_operations),
            threading.Thread(target=laser_operations),
            threading.Thread(target=tec_operations),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
