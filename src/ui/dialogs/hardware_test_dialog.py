"""
Hardware Diagnostic Test Results Dialog.

Displays comprehensive test results for all hardware components
with pass/fail status and detailed information.
"""

import logging
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class HardwareTestDialog(QDialog):
    """
    Dialog for displaying hardware diagnostic test results.

    Shows test results for each hardware component with:
    - Pass/Fail status with visual indicators
    - Component details (resolution, position, voltage, etc.)
    - Overall summary statistics
    """

    def __init__(self, test_results: dict[str, Any], parent=None):
        """
        Initialize hardware test dialog.

        Args:
            test_results: Dictionary mapping component names to test result dicts
                Each result dict contains:
                - name (str): Display name
                - passed (bool): Test pass/fail status
                - details (list[str]): Additional information
            parent: Parent widget
        """
        super().__init__(parent)
        self.test_results = test_results
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize user interface."""
        self.setWindowTitle("Hardware Diagnostic Results")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Header
        header = QLabel("🧪 Hardware Diagnostic Test Results")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 12px; "
            "background-color: #6A1B9A; color: white; border-radius: 3px;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Scrollable results area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        results_container = QWidget()
        results_layout = QVBoxLayout()
        results_container.setLayout(results_layout)

        # Add result widget for each component
        for component_key, result in self.test_results.items():
            result_widget = self._create_result_widget(result)
            results_layout.addWidget(result_widget)

        results_layout.addStretch()
        scroll.setWidget(results_container)
        main_layout.addWidget(scroll, 1)

        # Overall summary
        summary_widget = self._create_summary()
        main_layout.addWidget(summary_widget)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def _create_result_widget(self, result: dict[str, Any]) -> QGroupBox:
        """
        Create widget displaying test result for one component.

        Args:
            result: Test result dictionary with name, passed, and details

        Returns:
            QGroupBox containing formatted test result
        """
        group = QGroupBox()

        layout = QVBoxLayout()
        group.setLayout(layout)

        # Component name and status
        header_layout = QHBoxLayout()

        name_label = QLabel(result["name"])
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Status indicator
        status_text = "✓ PASS" if result["passed"] else "✗ FAIL"
        status_color = "#4CAF50" if result["passed"] else "#f44336"

        status_label = QLabel(status_text)
        status_label.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {status_color}; "
            f"padding: 4px 12px; background-color: #2b2b2b; border-radius: 3px;"
        )
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Details
        if result["details"]:
            for detail in result["details"]:
                detail_label = QLabel(f"  • {detail}")
                detail_label.setStyleSheet("color: #aaa; font-size: 12px; padding-left: 8px;")
                layout.addWidget(detail_label)
        else:
            no_details = QLabel("  • No additional details available")
            no_details.setStyleSheet("color: #666; font-size: 12px; padding-left: 8px;")
            layout.addWidget(no_details)

        # Styling
        if result["passed"]:
            group.setStyleSheet(
                "QGroupBox { background-color: #1B5E20; border: 2px solid #4CAF50; "
                "border-radius: 4px; padding: 8px; margin-top: 4px; }"
            )
        else:
            group.setStyleSheet(
                "QGroupBox { background-color: #B71C1C; border: 2px solid #f44336; "
                "border-radius: 4px; padding: 8px; margin-top: 4px; }"
            )

        return group

    def _create_summary(self) -> QWidget:
        """
        Create overall summary widget.

        Returns:
            Widget displaying pass/fail statistics
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Calculate statistics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results.values() if r["passed"])
        failed = total - passed

        # Summary text
        summary_label = QLabel(f"Overall Results: {passed}/{total} PASSED")
        summary_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 12px; "
            "background-color: #37474F; border-radius: 3px;"
        )
        summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(summary_label)

        # Detailed breakdown
        if failed > 0:
            breakdown = QLabel(f"  ✓ Passed: {passed}  |  ✗ Failed: {failed}")
            breakdown.setStyleSheet("color: #aaa; font-size: 12px; padding: 4px;")
            breakdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(breakdown)

        return widget
