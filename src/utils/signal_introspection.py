"""
PyQt6 Signal/Slot Introspection Utilities

Tools for analyzing PyQt6 signal/slot architecture, validating connections,
and generating connection documentation for the TOSCA medical device system.

Author: TOSCA Development Team (Task 4.1)
Created: 2025-11-01
"""

import inspect
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import QMetaMethod, QMetaObject, QObject

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class SignalInfo:
    """Information about a PyQt6 signal."""

    name: str  # Signal name (e.g., "clicked", "valueChanged")
    declaring_class: str  # Class that declared the signal (e.g., "QPushButton")
    signature: str  # Full signature (e.g., "clicked(bool)")
    parameter_types: List[str]  # Parameter types (e.g., ["bool"])
    parameter_count: int  # Number of parameters
    is_custom: bool = False  # True if defined with pyqtSignal() decorator
    source_file: Optional[str] = None  # Source file if custom signal


@dataclass
class SlotInfo:
    """Information about a PyQt6 slot (method that can be connected)."""

    name: str  # Method name
    declaring_class: str  # Class that declared the method
    signature: str  # Method signature from inspect
    parameter_types: List[str]  # Parameter types
    parameter_count: int  # Number of parameters (excluding self)
    is_slot: bool = False  # True if decorated with @pyqtSlot


@dataclass
class ConnectionInfo:
    """Information about a signal/slot connection."""

    signal_name: str  # Signal name
    signal_object: str  # Object emitting signal (class name or instance repr)
    slot_name: str  # Slot method name
    slot_object: str  # Object receiving signal
    source_file: Optional[str] = None  # File where connection is made
    line_number: Optional[int] = None  # Line number of connection
    is_valid: bool = True  # Connection is valid (both signal and slot exist)
    validation_errors: List[str] = field(default_factory=list)  # Validation issues


@dataclass
class ObjectSignalRegistry:
    """Registry of all signals and slots for a QObject instance."""

    object_name: str  # Object name or class name
    class_name: str  # Class name
    signals: List[SignalInfo]  # All signals
    slots: List[SlotInfo]  # All slots
    connections: List[ConnectionInfo]  # Known connections
    children: List["ObjectSignalRegistry"] = field(default_factory=list)  # Child objects


# ============================================================================
# Signal/Slot Introspection
# ============================================================================


class SignalSlotIntrospector:
    """
    PyQt6 signal/slot introspection utility.

    Uses QMetaObject to enumerate signals and slots on QObject instances,
    validates connections, and builds signal registry for documentation.
    """

    def __init__(self):
        """Initialize introspector."""
        self.signal_registry: Dict[str, ObjectSignalRegistry] = {}
        logger.info("SignalSlotIntrospector initialized")

    def introspect_object(
        self, obj: QObject, include_children: bool = True
    ) -> ObjectSignalRegistry:
        """
        Introspect a QObject instance to extract all signals and slots.

        Args:
            obj: QObject instance to introspect
            include_children: If True, recursively introspect child objects

        Returns:
            ObjectSignalRegistry containing all signals, slots, and connections
        """
        if not isinstance(obj, QObject):
            raise TypeError(f"Object must be QObject instance, got {type(obj)}")

        # Get object metadata
        meta_obj = obj.metaObject()
        class_name = meta_obj.className()
        object_name = obj.objectName() or f"<unnamed {class_name}>"

        logger.debug(f"Introspecting {class_name} ({object_name})")

        # Extract signals and slots
        signals = self._extract_signals(obj, meta_obj)
        slots = self._extract_slots(obj, meta_obj)

        # Create registry entry
        registry = ObjectSignalRegistry(
            object_name=object_name,
            class_name=class_name,
            signals=signals,
            slots=slots,
            connections=[],  # Will be populated by connection analysis
        )

        # Recursively introspect children
        if include_children:
            for child in obj.children():
                if isinstance(child, QObject):
                    child_registry = self.introspect_object(child, include_children=True)
                    registry.children.append(child_registry)

        # Store in global registry
        registry_key = f"{class_name}::{object_name}"
        self.signal_registry[registry_key] = registry

        return registry

    def _extract_signals(self, obj: QObject, meta_obj: QMetaObject) -> List[SignalInfo]:
        """
        Extract all signals from QObject using QMetaObject.

        Args:
            obj: QObject instance
            meta_obj: QMetaObject for the instance

        Returns:
            List of SignalInfo for all signals on the object
        """
        signals: List[SignalInfo] = []

        # Iterate through all methods in QMetaObject
        method_count = meta_obj.methodCount()
        for i in range(method_count):
            method = meta_obj.method(i)

            # Only process signals (methodType == Signal)
            if method.methodType() != QMetaMethod.MethodType.Signal:
                continue

            # Extract signal information
            signal_name = method.name().data().decode("utf-8")
            signature = method.methodSignature().data().decode("utf-8")
            parameter_types = [
                param_type.data().decode("utf-8") for param_type in method.parameterTypes()
            ]

            # Check if custom signal (defined with pyqtSignal)
            is_custom = self._is_custom_signal(obj, signal_name)

            signal_info = SignalInfo(
                name=signal_name,
                declaring_class=meta_obj.className(),
                signature=signature,
                parameter_types=parameter_types,
                parameter_count=len(parameter_types),
                is_custom=is_custom,
                source_file=self._get_source_file(obj) if is_custom else None,
            )

            signals.append(signal_info)
            logger.debug(f"  Found signal: {signature} (custom={is_custom})")

        return signals

    def _extract_slots(self, obj: QObject, meta_obj: QMetaObject) -> List[SlotInfo]:
        """
        Extract all slots from QObject using QMetaObject and Python inspect.

        Args:
            obj: QObject instance
            meta_obj: QMetaObject for the instance

        Returns:
            List of SlotInfo for all slots on the object
        """
        slots: List[SlotInfo] = []

        # Get slots from QMetaObject (decorated with @pyqtSlot)
        method_count = meta_obj.methodCount()
        qt_slots = set()

        for i in range(method_count):
            method = meta_obj.method(i)

            # Only process slots (methodType == Slot)
            if method.methodType() != QMetaMethod.MethodType.Slot:
                continue

            slot_name = method.name().data().decode("utf-8")
            qt_slots.add(slot_name)

            signature = method.methodSignature().data().decode("utf-8")
            parameter_types = [
                param_type.data().decode("utf-8") for param_type in method.parameterTypes()
            ]

            slot_info = SlotInfo(
                name=slot_name,
                declaring_class=meta_obj.className(),
                signature=signature,
                parameter_types=parameter_types,
                parameter_count=len(parameter_types),
                is_slot=True,
            )

            slots.append(slot_info)
            logger.debug(f"  Found Qt slot: {signature}")

        # Get all callable methods from Python introspection (potential slots)
        # Any public method can be a slot in PyQt6
        for name, method in inspect.getmembers(obj, predicate=inspect.ismethod):
            # Skip private methods and methods already found as Qt slots
            if name.startswith("_") or name in qt_slots:
                continue

            # Get method signature
            try:
                sig = inspect.signature(method)
                parameter_types = [
                    (
                        param.annotation.__name__
                        if param.annotation != inspect.Parameter.empty
                        else "Any"
                    )
                    for param_name, param in sig.parameters.items()
                    if param_name != "self"
                ]

                slot_info = SlotInfo(
                    name=name,
                    declaring_class=obj.__class__.__name__,
                    signature=f"{name}{sig}",
                    parameter_types=parameter_types,
                    parameter_count=len(parameter_types),
                    is_slot=False,  # Not decorated with @pyqtSlot
                )

                slots.append(slot_info)
                logger.debug(f"  Found potential slot: {name}{sig}")

            except (ValueError, TypeError) as e:
                logger.warning(f"  Could not inspect method {name}: {e}")

        return slots

    def _is_custom_signal(self, obj: QObject, signal_name: str) -> bool:
        """
        Check if signal is a custom signal (defined with pyqtSignal).

        Args:
            obj: QObject instance
            signal_name: Signal name to check

        Returns:
            True if custom signal, False if inherited from Qt classes
        """
        # Check if signal is defined in object's class (not inherited from Qt)
        obj_class = obj.__class__

        # Walk through class hierarchy to find where signal is defined
        for cls in obj_class.__mro__:
            # Stop at Qt base classes
            if cls.__name__.startswith("Q") and cls.__module__.startswith("PyQt6"):
                return False

            # Check if signal is defined in this class
            if signal_name in cls.__dict__:
                # Signal is defined in user class, not Qt class
                return True

        return False

    def _get_source_file(self, obj: QObject) -> Optional[str]:
        """
        Get source file path for object's class.

        Args:
            obj: QObject instance

        Returns:
            Source file path or None if not available
        """
        try:
            return inspect.getfile(obj.__class__)
        except (TypeError, OSError):
            return None

    def find_all_qobjects(self, root: QObject) -> List[QObject]:
        """
        Recursively find all QObject instances in object hierarchy.

        Args:
            root: Root QObject to start traversal

        Returns:
            List of all QObject instances (including root)
        """
        objects = [root]

        def traverse(obj: QObject):
            for child in obj.children():
                if isinstance(child, QObject):
                    objects.append(child)
                    traverse(child)

        traverse(root)
        logger.info(f"Found {len(objects)} QObject instances in hierarchy")
        return objects

    def validate_connection(
        self, signal_obj: QObject, signal_name: str, slot_obj: QObject, slot_name: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a signal/slot connection is valid.

        Args:
            signal_obj: Object emitting the signal
            signal_name: Signal name
            slot_obj: Object receiving the signal
            slot_name: Slot method name

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check signal exists
        signal_registry = self.introspect_object(signal_obj, include_children=False)
        signal_exists = any(sig.name == signal_name for sig in signal_registry.signals)

        if not signal_exists:
            errors.append(f"Signal '{signal_name}' not found on {signal_obj.__class__.__name__}")

        # Check slot exists
        slot_registry = self.introspect_object(slot_obj, include_children=False)
        slot_exists = any(slot.name == slot_name for slot in slot_registry.slots)

        if not slot_exists:
            errors.append(f"Slot '{slot_name}' not found on {slot_obj.__class__.__name__}")

        # If both exist, check signature compatibility
        if signal_exists and slot_exists:
            signal_info = next(sig for sig in signal_registry.signals if sig.name == signal_name)
            slot_info = next(slot for slot in slot_registry.slots if slot.name == slot_name)

            # Slot must have <= parameters than signal
            if slot_info.parameter_count > signal_info.parameter_count:
                errors.append(
                    f"Slot has more parameters ({slot_info.parameter_count}) "
                    f"than signal ({signal_info.parameter_count})"
                )

        is_valid = len(errors) == 0
        return is_valid, errors

    def generate_signal_report(self, registry: ObjectSignalRegistry) -> str:
        """
        Generate human-readable report for signal registry.

        Args:
            registry: ObjectSignalRegistry to generate report for

        Returns:
            Formatted string report
        """
        lines = []
        lines.append(f"=== {registry.class_name} ({registry.object_name}) ===")
        lines.append(f"\nSignals ({len(registry.signals)}):")

        for signal in registry.signals:
            custom_marker = " [CUSTOM]" if signal.is_custom else ""
            lines.append(f"  • {signal.signature}{custom_marker}")

        lines.append(f"\nSlots ({len(registry.slots)}):")
        for slot in registry.slots:
            slot_marker = " [@pyqtSlot]" if slot.is_slot else " [callable]"
            lines.append(f"  • {slot.signature}{slot_marker}")

        lines.append(f"\nChildren ({len(registry.children)}):")
        for child in registry.children:
            lines.append(f"  • {child.class_name} ({child.object_name})")

        return "\n".join(lines)


# ============================================================================
# Convenience Functions
# ============================================================================


def introspect_widget(widget: QObject) -> ObjectSignalRegistry:
    """
    Convenience function to introspect a single widget.

    Args:
        widget: QObject widget to introspect

    Returns:
        ObjectSignalRegistry with signal/slot information
    """
    introspector = SignalSlotIntrospector()
    return introspector.introspect_object(widget, include_children=False)


def introspect_widget_hierarchy(root_widget: QObject) -> ObjectSignalRegistry:
    """
    Convenience function to introspect widget and all children.

    Args:
        root_widget: Root widget to start introspection

    Returns:
        ObjectSignalRegistry with complete hierarchy
    """
    introspector = SignalSlotIntrospector()
    return introspector.introspect_object(root_widget, include_children=True)


def print_signal_report(widget: QObject):
    """
    Print signal/slot report for a widget to console.

    Args:
        widget: QObject widget to report on
    """
    introspector = SignalSlotIntrospector()
    registry = introspector.introspect_object(widget, include_children=False)
    report = introspector.generate_signal_report(registry)
    print(report)


# ============================================================================
# Example Usage (for testing)
# ============================================================================

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QPushButton

    # Example: Introspect a QPushButton
    app = QApplication([])
    button = QPushButton("Test Button")
    button.setObjectName("test_button")

    print("=== QPushButton Introspection ===")
    print_signal_report(button)

    # Example: Validate connection
    introspector = SignalSlotIntrospector()

    # Valid connection
    is_valid, errors = introspector.validate_connection(
        button, "clicked", button, "setEnabled"  # Signal  # Slot
    )
    print(f"\nValidation: clicked -> setEnabled")
    print(f"Valid: {is_valid}, Errors: {errors}")

    # Invalid connection (non-existent signal)
    is_valid, errors = introspector.validate_connection(
        button, "nonexistent_signal", button, "setEnabled"
    )
    print(f"\nValidation: nonexistent_signal -> setEnabled")
    print(f"Valid: {is_valid}, Errors: {errors}")
