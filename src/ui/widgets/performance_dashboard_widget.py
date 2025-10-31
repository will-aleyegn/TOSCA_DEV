"""
Performance Monitoring Dashboard Widget.

Displays system performance metrics, database statistics, log file info,
and resource usage for maintenance and monitoring purposes.
"""

import logging
from pathlib import Path
from typing import Optional

import psutil  # type: ignore[import-untyped]
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class PerformanceDashboardWidget(QWidget):
    """
    Performance monitoring dashboard for system health and maintenance.

    Displays:
    - Database statistics (size, vacuum info)
    - Log file statistics (size, count, rotation status)
    - System resource usage (CPU, memory, disk)
    - Performance recommendations
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        log_directory: Optional[Path] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize performance dashboard.

        Args:
            db_manager: Database manager for database statistics
            log_directory: Path to log files directory
            parent: Parent widget
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.log_directory = log_directory or Path("data/logs")

        self._setup_ui()
        self._start_auto_refresh()

    def _setup_ui(self) -> None:
        """Setup dashboard UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title
        title = QLabel("Performance Monitoring Dashboard")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Create metrics panels
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)

        # Row 1: Database and Logs
        self.db_panel = self._create_database_panel()
        self.log_panel = self._create_log_panel()
        metrics_layout.addWidget(self.db_panel, 0, 0)
        metrics_layout.addWidget(self.log_panel, 0, 1)

        # Row 2: System Resources and Actions
        self.system_panel = self._create_system_panel()
        self.action_panel = self._create_action_panel()
        metrics_layout.addWidget(self.system_panel, 1, 0)
        metrics_layout.addWidget(self.action_panel, 1, 1)

        layout.addLayout(metrics_layout)

        # Recommendations panel
        self.recommendations_panel = self._create_recommendations_panel()
        layout.addWidget(self.recommendations_panel)

        layout.addStretch()
        self.setLayout(layout)

        # Initial update
        self.update_metrics()

    def _create_database_panel(self) -> QGroupBox:
        """Create database statistics panel."""
        panel = QGroupBox("Database Statistics")
        layout = QVBoxLayout()

        self.db_size_label = QLabel("Size: --")
        self.db_records_label = QLabel("Records: --")
        self.db_last_vacuum_label = QLabel("Last Vacuum: Never")

        layout.addWidget(self.db_size_label)
        layout.addWidget(self.db_records_label)
        layout.addWidget(self.db_last_vacuum_label)

        panel.setLayout(layout)
        return panel

    def _create_log_panel(self) -> QGroupBox:
        """Create log file statistics panel."""
        panel = QGroupBox("Log File Statistics")
        layout = QVBoxLayout()

        self.log_count_label = QLabel("Files: --")
        self.log_total_size_label = QLabel("Total Size: --")
        self.log_oldest_label = QLabel("Oldest: --")

        layout.addWidget(self.log_count_label)
        layout.addWidget(self.log_total_size_label)
        layout.addWidget(self.log_oldest_label)

        panel.setLayout(layout)
        return panel

    def _create_system_panel(self) -> QGroupBox:
        """Create system resource usage panel."""
        panel = QGroupBox("System Resources")
        layout = QVBoxLayout()

        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.disk_label = QLabel("Disk: --")

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.disk_label)

        panel.setLayout(layout)
        return panel

    def _create_action_panel(self) -> QGroupBox:
        """Create maintenance actions panel."""
        panel = QGroupBox("Maintenance Actions")
        layout = QVBoxLayout()

        # Vacuum database button
        self.vacuum_button = QPushButton("Vacuum Database")
        self.vacuum_button.clicked.connect(self._on_vacuum_clicked)
        layout.addWidget(self.vacuum_button)

        # Manual refresh button
        refresh_button = QPushButton("Refresh Metrics")
        refresh_button.clicked.connect(self.update_metrics)
        layout.addWidget(refresh_button)

        panel.setLayout(layout)
        return panel

    def _create_recommendations_panel(self) -> QGroupBox:
        """Create performance recommendations panel."""
        panel = QGroupBox("Recommendations")
        layout = QVBoxLayout()

        self.recommendations_label = QLabel("No recommendations")
        self.recommendations_label.setWordWrap(True)
        self.recommendations_label.setStyleSheet(
            "padding: 10px; background-color: #F0F0F0; border-radius: 5px;"
        )

        layout.addWidget(self.recommendations_label)
        panel.setLayout(layout)
        return panel

    def _start_auto_refresh(self) -> None:
        """Start automatic metric refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_metrics)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        logger.info("Performance dashboard auto-refresh started (5s interval)")

    def update_metrics(self) -> None:
        """Update all dashboard metrics."""
        self._update_database_metrics()
        self._update_log_metrics()
        self._update_system_metrics()
        self._update_recommendations()

    def _update_database_metrics(self) -> None:
        """Update database statistics."""
        if not self.db_manager:
            self.db_size_label.setText("Size: N/A (no db manager)")
            return

        try:
            # Get database size
            success, size_mb, message = self.db_manager.get_database_size()
            if success:
                self.db_size_label.setText(f"Size: {size_mb:.2f} MB")
            else:
                self.db_size_label.setText(f"Size: Error ({message})")

            # Count records (estimate from safety logs)
            with self.db_manager.get_session() as session:
                from database.models import SafetyLog

                record_count = session.query(SafetyLog).count()
                self.db_records_label.setText(f"Safety Events: {record_count:,}")

        except Exception as e:
            logger.error(f"Error updating database metrics: {e}")
            self.db_size_label.setText("Size: Error")

    def _update_log_metrics(self) -> None:
        """Update log file statistics."""
        try:
            if not self.log_directory.exists():
                self.log_count_label.setText("Files: 0")
                self.log_total_size_label.setText("Total Size: 0 MB")
                return

            # Count log files
            log_files = list(self.log_directory.glob("*.jsonl"))
            file_count = len(log_files)

            # Calculate total size
            total_size_bytes = sum(f.stat().st_size for f in log_files if f.exists())
            total_size_mb = total_size_bytes / (1024 * 1024)

            # Find oldest log
            if log_files:
                oldest_file = min(log_files, key=lambda f: f.stat().st_mtime)
                oldest_name = oldest_file.name
            else:
                oldest_name = "None"

            self.log_count_label.setText(f"Files: {file_count}")
            self.log_total_size_label.setText(f"Total Size: {total_size_mb:.2f} MB")
            self.log_oldest_label.setText(f"Oldest: {oldest_name}")

        except Exception as e:
            logger.error(f"Error updating log metrics: {e}")
            self.log_count_label.setText("Files: Error")

    def _update_system_metrics(self) -> None:
        """Update system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            self.memory_label.setText(
                f"Memory: {memory_used_gb:.1f}/{memory_total_gb:.1f} GB ({memory_percent:.1f}%)"
            )

            # Disk usage (data directory)
            data_path = Path("data")
            if data_path.exists():
                disk = psutil.disk_usage(str(data_path))
                disk_percent = disk.percent
                disk_free_gb = disk.free / (1024**3)
                self.disk_label.setText(
                    f"Disk Free: {disk_free_gb:.1f} GB ({100-disk_percent:.1f}% free)"
                )
            else:
                self.disk_label.setText("Disk: N/A")

        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
            self.cpu_label.setText("CPU: Error")

    def _update_recommendations(self) -> None:
        """Update performance recommendations based on metrics."""
        recommendations = []

        try:
            # Check database size
            if self.db_manager:
                success, size_mb, _ = self.db_manager.get_database_size()
                if success and size_mb > 100:
                    recommendations.append(
                        f"Database large ({size_mb:.0f}MB) - Consider running VACUUM"
                    )

            # Check log file count
            if self.log_directory.exists():
                log_files = list(self.log_directory.glob("*.jsonl"))
                if len(log_files) > 50:
                    recommendations.append(
                        f"Many log files ({len(log_files)}) - Log rotation working correctly"
                    )

            # Check disk space
            data_path = Path("data")
            if data_path.exists():
                disk = psutil.disk_usage(str(data_path))
                if disk.percent > 90:
                    recommendations.append(
                        f"Disk space low ({100-disk.percent:.1f}% free) - Clean up old data"
                    )

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                recommendations.append(
                    f"Memory usage high ({memory.percent:.0f}%) - Consider restarting application"
                )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        # Update UI
        if recommendations:
            text = "\\n".join(f"• {rec}" for rec in recommendations)
            self.recommendations_label.setText(text)
            self.recommendations_label.setStyleSheet(
                "padding: 10px; background-color: #FFF3E0; "
                "border: 2px solid #F57C00; border-radius: 5px;"
            )
        else:
            self.recommendations_label.setText("No recommendations - System healthy")
            self.recommendations_label.setStyleSheet(
                "padding: 10px; background-color: #E8F5E9; "
                "border: 2px solid #4CAF50; border-radius: 5px;"
            )

    def _on_vacuum_clicked(self) -> None:
        """Handle vacuum database button click."""
        if not self.db_manager:
            logger.warning("Cannot vacuum database: no db manager")
            return

        try:
            self.vacuum_button.setEnabled(False)
            self.vacuum_button.setText("Vacuuming...")

            logger.info("Starting database vacuum (user-initiated)")
            success, message, stats = self.db_manager.vacuum_database()

            if success:
                logger.info(f"Database vacuum complete: {message}")
                self.recommendations_label.setText(
                    f"Vacuum complete: {stats.get('size_reduction_percent', 0):.1f}% reduction"
                )
                self.recommendations_label.setStyleSheet(
                    "padding: 10px; background-color: #E8F5E9; "
                    "border: 2px solid #4CAF50; border-radius: 5px;"
                )
            else:
                logger.error(f"Database vacuum failed: {message}")
                self.recommendations_label.setText(f"Vacuum failed: {message}")
                self.recommendations_label.setStyleSheet(
                    "padding: 10px; background-color: #FFEBEE; "
                    "border: 2px solid #F44336; border-radius: 5px;"
                )

            # Refresh metrics
            self.update_metrics()

        except Exception as e:
            logger.error(f"Error during vacuum: {e}")
            self.recommendations_label.setText(f"Vacuum error: {e}")

        finally:
            self.vacuum_button.setEnabled(True)
            self.vacuum_button.setText("Vacuum Database")

    def stop_auto_refresh(self) -> None:
        """Stop automatic metric refresh timer."""
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()
            logger.info("Performance dashboard auto-refresh stopped")
