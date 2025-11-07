"""
Unit tests for PyQt6 signal/slot introspection utilities.

Tests signal enumeration, slot detection, connection validation,
and object hierarchy traversal.

Author: AI Assistant (Task 4.1)
Created: 2025-11-01
"""

import pytest
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QPushButton, QSlider, QWidget

from src.utils.signal_introspection import (
    SignalSlotIntrospector,
    introspect_widget,
    introspect_widget_hierarchy,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def simple_widget(qapp):
    """Create a simple test widget."""
    widget = QWidget()
    widget.setObjectName("test_widget")
    yield widget


@pytest.fixture
def button_widget(qapp):
    """Create a QPushButton test widget."""
    button = QPushButton("Test Button")
    button.setObjectName("test_button")
    yield button


@pytest.fixture
def custom_signal_widget(qapp):
    """Create a widget with custom signals."""

    class CustomWidget(QWidget):
        # Custom signals
        value_changed = pyqtSignal(int)
        status_updated = pyqtSignal(str, bool)
        simple_signal = pyqtSignal()

        def __init__(self):
            super().__init__()
            self.setObjectName("custom_widget")

        @pyqtSlot(int)
        def on_value_changed(self, value: int):
            """Qt slot for value changes."""
            pass

        def public_method(self, text: str) -> None:
            """Public method (potential slot)."""
            pass

        def _private_method(self):
            """Private method (not a slot)."""
            pass

    widget = CustomWidget()
    yield widget


@pytest.fixture
def nested_widget_hierarchy(qapp):
    """Create a nested widget hierarchy for testing."""
    parent = QWidget()
    parent.setObjectName("parent_widget")

    child1 = QPushButton("Child 1", parent)
    child1.setObjectName("child1_button")

    child2 = QSlider(parent)
    child2.setObjectName("child2_slider")

    grandchild = QPushButton("Grandchild", child1)
    grandchild.setObjectName("grandchild_button")

    yield parent


# ============================================================================
# Introspector Initialization Tests
# ============================================================================


def test_introspector_initialization():
    """Test SignalSlotIntrospector initialization."""
    introspector = SignalSlotIntrospector()
    assert introspector is not None
    assert isinstance(introspector.signal_registry, dict)
    assert len(introspector.signal_registry) == 0


# ============================================================================
# Signal Detection Tests
# ============================================================================


def test_detect_qt_builtin_signals(button_widget):
    """Test detection of Qt built-in signals (QPushButton.clicked)."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(button_widget, include_children=False)

    # Check that clicked signal is detected
    signal_names = [sig.name for sig in registry.signals]
    assert "clicked" in signal_names

    # Check signal properties
    clicked_signal = next(sig for sig in registry.signals if sig.name == "clicked")
    assert clicked_signal.declaring_class == "QPushButton"
    assert not clicked_signal.is_custom  # Built-in signal
    assert clicked_signal.parameter_count == 1  # clicked(bool)
    assert clicked_signal.parameter_types == ["bool"]


def test_detect_custom_signals(custom_signal_widget):
    """Test detection of custom signals defined with pyqtSignal()."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(custom_signal_widget, include_children=False)

    # Check custom signals are detected
    signal_names = [sig.name for sig in registry.signals]
    assert "value_changed" in signal_names
    assert "status_updated" in signal_names
    assert "simple_signal" in signal_names

    # Check custom signal properties
    value_changed_sig = next(sig for sig in registry.signals if sig.name == "value_changed")
    assert value_changed_sig.is_custom  # Custom signal
    assert value_changed_sig.parameter_count == 1
    assert value_changed_sig.parameter_types == ["int"]

    status_updated_sig = next(sig for sig in registry.signals if sig.name == "status_updated")
    assert status_updated_sig.is_custom
    assert status_updated_sig.parameter_count == 2
    assert status_updated_sig.parameter_types == ["QString", "bool"]

    simple_signal_sig = next(sig for sig in registry.signals if sig.name == "simple_signal")
    assert simple_signal_sig.is_custom
    assert simple_signal_sig.parameter_count == 0


# ============================================================================
# Slot Detection Tests
# ============================================================================


def test_detect_qt_builtin_slots(button_widget):
    """Test detection of Qt built-in slots (QPushButton.setEnabled)."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(button_widget, include_children=False)

    # Check that setEnabled slot is detected
    slot_names = [slot.name for slot in registry.slots]
    assert "setEnabled" in slot_names


def test_detect_pyqt_slots(custom_signal_widget):
    """Test detection of @pyqtSlot decorated methods."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(custom_signal_widget, include_children=False)

    # Check that @pyqtSlot decorated method is detected
    slot_names = [slot.name for slot in registry.slots]
    assert "on_value_changed" in slot_names

    # Check slot properties
    on_value_changed_slot = next(slot for slot in registry.slots if slot.name == "on_value_changed")
    assert on_value_changed_slot.is_slot  # Decorated with @pyqtSlot
    assert on_value_changed_slot.parameter_count == 1


def test_detect_callable_methods_as_slots(custom_signal_widget):
    """Test detection of public methods as potential slots."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(custom_signal_widget, include_children=False)

    # Check that public method is detected as potential slot
    slot_names = [slot.name for slot in registry.slots]
    assert "public_method" in slot_names

    # Private methods should NOT be detected
    assert "_private_method" not in slot_names


# ============================================================================
# Object Hierarchy Tests
# ============================================================================


def test_introspect_with_children(nested_widget_hierarchy):
    """Test recursive introspection of widget hierarchy."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(nested_widget_hierarchy, include_children=True)

    # Check parent widget
    assert registry.object_name == "parent_widget"
    assert registry.class_name == "QWidget"

    # Check children are detected
    assert len(registry.children) >= 2  # child1_button and child2_slider

    child_names = [child.object_name for child in registry.children]
    assert "child1_button" in child_names
    assert "child2_slider" in child_names


def test_find_all_qobjects(nested_widget_hierarchy):
    """Test finding all QObject instances in hierarchy."""
    introspector = SignalSlotIntrospector()
    all_objects = introspector.find_all_qobjects(nested_widget_hierarchy)

    # Should find parent + 2 children + 1 grandchild = 4 objects minimum
    assert len(all_objects) >= 4

    # Check specific objects are found
    object_names = [obj.objectName() for obj in all_objects]
    assert "parent_widget" in object_names
    assert "child1_button" in object_names
    assert "child2_slider" in object_names
    assert "grandchild_button" in object_names


# ============================================================================
# Connection Validation Tests
# ============================================================================


def test_validate_valid_connection(button_widget):
    """Test validation of a valid signal/slot connection."""
    introspector = SignalSlotIntrospector()

    # clicked(bool) -> setEnabled(bool) is valid
    is_valid, errors = introspector.validate_connection(
        button_widget, "clicked", button_widget, "setEnabled"
    )

    assert is_valid
    assert len(errors) == 0


def test_validate_nonexistent_signal(button_widget):
    """Test validation fails for non-existent signal."""
    introspector = SignalSlotIntrospector()

    # nonexistent_signal does not exist
    is_valid, errors = introspector.validate_connection(
        button_widget, "nonexistent_signal", button_widget, "setEnabled"
    )

    assert not is_valid
    assert len(errors) > 0
    assert "Signal 'nonexistent_signal' not found" in errors[0]


def test_validate_nonexistent_slot(button_widget):
    """Test validation fails for non-existent slot."""
    introspector = SignalSlotIntrospector()

    # nonexistent_slot does not exist
    is_valid, errors = introspector.validate_connection(
        button_widget, "clicked", button_widget, "nonexistent_slot"
    )

    assert not is_valid
    assert len(errors) > 0
    assert "Slot 'nonexistent_slot' not found" in errors[0]


def test_validate_parameter_count_mismatch(custom_signal_widget):
    """Test validation detects parameter count mismatches."""
    introspector = SignalSlotIntrospector()

    # Create a widget with incompatible slot
    class TestWidget(QWidget):
        test_signal = pyqtSignal(int)  # 1 parameter

        @pyqtSlot(int, str)  # 2 parameters (more than signal)
        def test_slot(self, value: int, text: str):
            pass

    test_widget = TestWidget()

    # This connection should be invalid (slot has more params than signal)
    is_valid, errors = introspector.validate_connection(
        test_widget, "test_signal", test_widget, "test_slot"
    )

    assert not is_valid
    assert any("more parameters" in error for error in errors)


# ============================================================================
# Report Generation Tests
# ============================================================================


def test_generate_signal_report(button_widget):
    """Test signal report generation."""
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(button_widget, include_children=False)

    report = introspector.generate_signal_report(registry)

    # Check report contains key sections
    assert "QPushButton" in report
    assert "test_button" in report
    assert "Signals" in report
    assert "Slots" in report
    assert "clicked" in report  # Signal name


# ============================================================================
# Convenience Function Tests
# ============================================================================


def test_introspect_widget_convenience(button_widget):
    """Test introspect_widget convenience function."""
    registry = introspect_widget(button_widget)

    assert registry is not None
    assert registry.class_name == "QPushButton"
    assert len(registry.signals) > 0
    assert len(registry.children) == 0  # include_children=False


def test_introspect_widget_hierarchy_convenience(nested_widget_hierarchy):
    """Test introspect_widget_hierarchy convenience function."""
    registry = introspect_widget_hierarchy(nested_widget_hierarchy)

    assert registry is not None
    assert registry.class_name == "QWidget"
    assert len(registry.children) >= 2  # include_children=True


# ============================================================================
# Edge Case Tests
# ============================================================================


def test_introspect_object_without_objectname(qapp):
    """Test introspection of object without explicit objectName."""
    widget = QWidget()  # No setObjectName() call

    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(widget, include_children=False)

    # Should use default naming: "<unnamed ClassName>"
    assert "<unnamed QWidget>" in registry.object_name


def test_invalid_object_type():
    """Test introspection fails gracefully for non-QObject."""
    introspector = SignalSlotIntrospector()

    with pytest.raises(TypeError, match="Object must be QObject instance"):
        introspector.introspect_object("not a qobject")


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_introspection_workflow(custom_signal_widget):
    """Test complete introspection workflow."""
    introspector = SignalSlotIntrospector()

    # 1. Introspect widget
    registry = introspector.introspect_object(custom_signal_widget, include_children=False)

    # 2. Verify signals detected
    assert len(registry.signals) >= 3  # Custom signals

    # 3. Verify slots detected
    assert len(registry.slots) >= 2  # @pyqtSlot + public methods

    # 4. Generate report
    report = introspector.generate_signal_report(registry)
    assert len(report) > 0

    # 5. Validate connections
    is_valid, errors = introspector.validate_connection(
        custom_signal_widget,
        "value_changed",
        custom_signal_widget,
        "on_value_changed",
    )
    assert is_valid
    assert len(errors) == 0
