#!/usr/bin/env python3
"""
Test script to verify camera settings fix.

Tests:
1. Status labels update when show_settings=False (Treatment tab)
2. Status labels update when show_settings=True (Hardware tab)
3. Control sliders work when show_settings=True
4. Hardware feedback signals update UI correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication

# Mock camera controller
class MockCameraController:
    """Mock camera controller for testing."""

    from PyQt6.QtCore import pyqtSignal, QObject

    class Signals(QObject):
        pixmap_ready = pyqtSignal(object)
        fps_update = pyqtSignal(float)
        connection_changed = pyqtSignal(bool)
        error_occurred = pyqtSignal(str)
        recording_status_changed = pyqtSignal(bool)
        exposure_changed = pyqtSignal(float)
        gain_changed = pyqtSignal(float)

    def __init__(self):
        self.signals = self.Signals()
        self.is_connected = False
        self.is_streaming = False
        self.is_recording = False
        self._exposure = 10000.0  # 10ms
        self._gain = 5.0  # 5dB

    def __getattr__(self, name):
        """Redirect signal access to signals object."""
        if hasattr(self.signals, name):
            return getattr(self.signals, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def connect(self):
        self.is_connected = True
        self.connection_changed.emit(True)
        return True

    def disconnect(self):
        self.is_connected = False
        self.connection_changed.emit(False)
        return True

    def start_streaming(self):
        self.is_streaming = True
        return True

    def stop_streaming(self):
        self.is_streaming = False
        return True

    def set_exposure(self, exposure_us):
        self._exposure = exposure_us
        # Emit signal to trigger hardware feedback
        self.exposure_changed.emit(exposure_us)
        return True

    def set_gain(self, gain_db):
        self._gain = gain_db
        # Emit signal to trigger hardware feedback
        self.gain_changed.emit(gain_db)
        return True

    def get_exposure(self):
        return self._exposure

    def get_gain(self):
        return self._gain

    def get_exposure_range(self):
        return (100.0, 1000000.0)

    def get_gain_range(self):
        return (0.0, 24.0)

    def set_auto_exposure(self, enabled):
        return True

    def set_auto_gain(self, enabled):
        return True

    def set_auto_white_balance(self, enabled):
        return True

    def set_display_scale(self, scale):
        return True


def test_treatment_tab_status_labels():
    """Test that status labels update in Treatment tab (show_settings=False)."""
    print("\n=== Test 1: Treatment Tab Status Labels ===")

    from ui.widgets.camera_widget import CameraWidget

    app = QApplication.instance() or QApplication(sys.argv)

    # Create mock controller
    mock_controller = MockCameraController()

    # Create widget with show_settings=False (Treatment tab mode)
    widget = CameraWidget(camera_controller=mock_controller, show_settings=False)

    # Verify controls don't exist
    assert widget.exposure_slider is None, "Exposure slider should not exist in Treatment tab"
    assert widget.gain_slider is None, "Gain slider should not exist in Treatment tab"
    print("✓ Controls hidden correctly in Treatment tab")

    # Simulate connection and settings update
    mock_controller.connect()

    # Emit hardware signals
    test_exposure = 15000.0  # 15ms
    test_gain = 8.5  # 8.5dB
    mock_controller.exposure_changed.emit(test_exposure)
    mock_controller.gain_changed.emit(test_gain)

    # Process events
    app.processEvents()

    # Check status labels updated
    expected_exposure_text = f"Exposure: 15000 µs (15.0 ms)"
    expected_gain_text = f"Gain: 8.5 dB"

    actual_exposure_text = widget.exposure_info.text()
    actual_gain_text = widget.gain_info.text()

    print(f"Expected exposure: {expected_exposure_text}")
    print(f"Actual exposure: {actual_exposure_text}")
    print(f"Expected gain: {expected_gain_text}")
    print(f"Actual gain: {actual_gain_text}")

    assert actual_exposure_text == expected_exposure_text, \
        f"Exposure label mismatch: expected '{expected_exposure_text}', got '{actual_exposure_text}'"
    assert actual_gain_text == expected_gain_text, \
        f"Gain label mismatch: expected '{expected_gain_text}', got '{actual_gain_text}'"

    print("✓ Status labels updated correctly in Treatment tab")

    widget.close()


def test_hardware_tab_full_controls():
    """Test that full controls work in Hardware tab (show_settings=True)."""
    print("\n=== Test 2: Hardware Tab Full Controls ===")

    from ui.widgets.camera_widget import CameraWidget

    app = QApplication.instance() or QApplication(sys.argv)

    # Create mock controller
    mock_controller = MockCameraController()

    # Create widget with show_settings=True (Hardware tab mode)
    widget = CameraWidget(camera_controller=mock_controller, show_settings=True)

    # Verify controls exist
    assert widget.exposure_slider is not None, "Exposure slider should exist in Hardware tab"
    assert widget.gain_slider is not None, "Gain slider should exist in Hardware tab"
    assert widget.auto_exposure_check is not None, "Auto exposure checkbox should exist"
    assert widget.auto_gain_check is not None, "Auto gain checkbox should exist"
    assert widget.auto_wb_check is not None, "Auto WB checkbox should exist"
    print("✓ Controls visible in Hardware tab")

    # Simulate connection
    mock_controller.connect()
    app.processEvents()

    # Emit hardware signals
    test_exposure = 20000.0  # 20ms
    test_gain = 12.5  # 12.5dB
    mock_controller.exposure_changed.emit(test_exposure)
    mock_controller.gain_changed.emit(test_gain)

    # Process events
    app.processEvents()

    # Check status labels updated
    expected_exposure_text = f"Exposure: 20000 µs (20.0 ms)"
    expected_gain_text = f"Gain: 12.5 dB"

    actual_exposure_text = widget.exposure_info.text()
    actual_gain_text = widget.gain_info.text()

    print(f"Expected exposure: {expected_exposure_text}")
    print(f"Actual exposure: {actual_exposure_text}")
    print(f"Expected gain: {expected_gain_text}")
    print(f"Actual gain: {actual_gain_text}")

    assert actual_exposure_text == expected_exposure_text, \
        f"Exposure label mismatch: expected '{expected_exposure_text}', got '{actual_exposure_text}'"
    assert actual_gain_text == expected_gain_text, \
        f"Gain label mismatch: expected '{expected_gain_text}', got '{actual_gain_text}'"

    # Check sliders updated
    assert widget.exposure_slider.value() == 20000, \
        f"Exposure slider not updated: expected 20000, got {widget.exposure_slider.value()}"
    assert widget.gain_slider.value() == 125, \
        f"Gain slider not updated: expected 125, got {widget.gain_slider.value()}"

    print("✓ Status labels and controls updated correctly in Hardware tab")

    widget.close()


def test_slider_user_interaction():
    """Test that slider changes trigger camera controller updates."""
    print("\n=== Test 3: Slider User Interaction ===")

    from ui.widgets.camera_widget import CameraWidget

    app = QApplication.instance() or QApplication(sys.argv)

    # Create mock controller with tracking
    mock_controller = MockCameraController()
    exposure_calls = []
    gain_calls = []

    original_set_exposure = mock_controller.set_exposure
    original_set_gain = mock_controller.set_gain

    def tracked_set_exposure(value):
        exposure_calls.append(value)
        return original_set_exposure(value)

    def tracked_set_gain(value):
        gain_calls.append(value)
        return original_set_gain(value)

    mock_controller.set_exposure = tracked_set_exposure
    mock_controller.set_gain = tracked_set_gain

    # Create widget
    widget = CameraWidget(camera_controller=mock_controller, show_settings=True)

    # Simulate connection
    mock_controller.connect()
    app.processEvents()

    # Clear initial calls from connection
    exposure_calls.clear()
    gain_calls.clear()

    # Simulate user changing slider
    print("Simulating user slider changes...")
    widget.exposure_slider.setValue(25000)
    widget.gain_slider.setValue(150)  # 15.0 dB

    app.processEvents()

    # Check that controller was called
    print(f"Exposure calls: {exposure_calls}")
    print(f"Gain calls: {gain_calls}")

    assert 25000.0 in exposure_calls, "set_exposure not called with correct value"
    assert 15.0 in gain_calls, "set_gain not called with correct value"

    print("✓ Slider changes trigger camera controller updates")

    widget.close()


if __name__ == "__main__":
    print("Camera Settings Fix Verification")
    print("=" * 50)

    try:
        test_treatment_tab_status_labels()
        test_hardware_tab_full_controls()
        test_slider_user_interaction()

        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
