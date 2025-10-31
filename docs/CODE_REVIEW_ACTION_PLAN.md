# Code Review Action Plan - Week 4-5 Fixes

**Date:** 2025-10-31
**Review Completion:** Week 4-5 comprehensive review
**Overall Grade:** A- (87/100)
**Status:** Action Required

---

## Executive Summary

Week 4-5 implementations are excellent overall, but one CRITICAL issue prevents Week 4 completion: **H.264 CRF quality parameter is not applied to video encoding**. This must be fixed before Week 4 can be considered complete.

### Priority Matrix

```
CRITICAL (Must Fix):
└── H.264 CRF Implementation

HIGH (Should Fix):
├── Background threading for database vacuum
└── Hardcoded validator in config models

LOW (Good to Fix):
├── QTimer cleanup on widget destruction
└── Document single-process assumption
```

---

## CRITICAL PRIORITY

### 1. Fix H.264 CRF Implementation

**Issue:** Video compression quality parameter (CRF=28) is configured but not applied to OpenCV VideoWriter.

**Impact:**
- Week 4 goal (50% file size reduction) NOT achieved
- Configuration parameter has no effect
- Videos recorded with default quality settings

**Root Cause:**
OpenCV's `cv2.VideoWriter` constructor doesn't accept CRF parameter directly. Must be passed via FFmpeg backend environment variable.

**Fix Location:**
`src/hardware/camera_controller.py` - `VideoRecorder._initialize_writer()` method

**Implementation:**

```python
# File: src/hardware/camera_controller.py
# Location: VideoRecorder class, _initialize_writer() method

import os  # Add to imports at top of file

def _initialize_writer(self) -> None:
    """
    Initialize video writer with codec fallback.

    Tries primary codec first, falls back to fallback codec if unavailable.
    For H.264, uses CRF quality setting for file size optimization via FFmpeg.
    """
    # Map codec names to fourcc codes
    codec_map = {
        "H264": "H264",  # H.264 codec (best compression)
        "X264": "X264",  # Alternative H.264
        "avc1": "avc1",  # Another H.264 variant
        "MJPG": "MJPG",  # Motion JPEG (moderate compression)
        "MJPEG": "MJPG",  # Motion JPEG alternative
        "mp4v": "mp4v",  # MPEG-4 Part 2 (basic compression)
    }

    # Try primary codec
    codec_code = codec_map.get(self.codec, self.codec)
    fourcc = cv2.VideoWriter_fourcc(*codec_code)

    # === FIX STARTS HERE ===
    # For H.264 codecs, set FFmpeg-specific params via environment variable
    # This is the standard way to pass CRF to OpenCV's VideoWriter
    original_ffmpeg_opts = os.environ.get("OPENCV_FFMPEG_WRITER_OPTIONS")

    if "264" in self.codec.upper():
        # Set CRF quality parameter for H.264 encoding
        # CRF range: 0 (lossless) to 51 (worst quality)
        # Recommended: 18 (visually lossless), 23 (default), 28 (good balance)
        os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"] = f"crf={self.quality_crf}"
        logger.debug(f"Set FFmpeg CRF={self.quality_crf} for H.264 encoding")
    # === FIX ENDS HERE ===

    self.writer = cv2.VideoWriter(
        str(self.output_path), fourcc, self.fps, self.frame_size
    )

    # === CLEANUP STARTS HERE ===
    # Restore original environment variable to avoid side effects
    if "264" in self.codec.upper():
        if original_ffmpeg_opts is None:
            # Remove if it didn't exist before
            if "OPENCV_FFMPEG_WRITER_OPTIONS" in os.environ:
                del os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"]
        else:
            # Restore original value
            os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"] = original_ffmpeg_opts
        logger.debug("Restored FFmpeg environment variable")
    # === CLEANUP ENDS HERE ===

    if self.writer and self.writer.isOpened():
        self.actual_codec_used = self.codec
        logger.info(f"Using primary codec: {self.codec} with CRF={self.quality_crf}")
        return

    # Primary codec failed, try fallback
    logger.warning(
        f"Primary codec {self.codec} not available, trying fallback {self.fallback_codec}"
    )

    # Repeat environment variable setup for fallback codec
    original_ffmpeg_opts = os.environ.get("OPENCV_FFMPEG_WRITER_OPTIONS")
    if "264" in self.fallback_codec.upper():
        os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"] = f"crf={self.quality_crf}"

    fallback_code = codec_map.get(self.fallback_codec, self.fallback_codec)
    fourcc = cv2.VideoWriter_fourcc(*fallback_code)
    self.writer = cv2.VideoWriter(
        str(self.output_path), fourcc, self.fps, self.frame_size
    )

    # Cleanup for fallback
    if "264" in self.fallback_codec.upper():
        if original_ffmpeg_opts is None:
            if "OPENCV_FFMPEG_WRITER_OPTIONS" in os.environ:
                del os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"]
        else:
            os.environ["OPENCV_FFMPEG_WRITER_OPTIONS"] = original_ffmpeg_opts

    if self.writer and self.writer.isOpened():
        self.actual_codec_used = self.fallback_codec
        logger.info(f"Using fallback codec: {self.fallback_codec}")
        return

    # Both codecs failed
    logger.error(f"Both {self.codec} and {self.fallback_codec} codecs failed")
    self.actual_codec_used = "none"
```

**Testing Criteria:**

1. **Functional Test:**
   - Record 30-second video with CRF=28
   - Record same 30-second video with CRF=18
   - Verify CRF=28 file is smaller (should be ~40-50% smaller)
   - Verify both videos are playable

2. **Quality Test:**
   - Manually review CRF=28 video
   - Confirm diagnostic quality maintained
   - No visible artifacts or quality degradation

3. **Configuration Test:**
   - Change `video_quality_crf` in config.yaml (18, 23, 28, 35)
   - Verify each setting produces different file sizes
   - Confirm lower CRF = larger file (better quality)

4. **Fallback Test:**
   - Test with H.264 unavailable (rename codec DLL)
   - Verify fallback to MJPEG works
   - Verify no crashes or errors

**Validation:**
```bash
# Test script
python -c "
from pathlib import Path
from src.hardware.camera_controller import VideoRecorder
import numpy as np

# Create test video with CRF=28
rec_28 = VideoRecorder(Path('test_crf28.mp4'), fps=30, codec='H264', quality_crf=28)
for i in range(30*30):  # 30 seconds at 30 FPS
    frame = np.random.randint(0, 255, (1088, 1456, 3), dtype=np.uint8)
    rec_28.write_frame(frame)
rec_28.close()

# Create test video with CRF=18 (higher quality)
rec_18 = VideoRecorder(Path('test_crf18.mp4'), fps=30, codec='H264', quality_crf=18)
for i in range(30*30):
    frame = np.random.randint(0, 255, (1088, 1456, 3), dtype=np.uint8)
    rec_18.write_frame(frame)
rec_18.close()

# Compare file sizes
import os
size_28 = os.path.getsize('test_crf28.mp4')
size_18 = os.path.getsize('test_crf18.mp4')
print(f'CRF=28: {size_28/1024/1024:.1f}MB')
print(f'CRF=18: {size_18/1024/1024:.1f}MB')
print(f'Reduction: {(1 - size_28/size_18)*100:.1f}%')
assert size_28 < size_18, 'CRF=28 should be smaller than CRF=18'
"
```

**Estimated Effort:** 30-45 minutes

**Completion Criteria:**
- [ ] Code changes implemented
- [ ] Manual test confirms file size reduction
- [ ] Automated test added to test suite
- [ ] Configuration documentation updated
- [ ] Week 4 goal (50% reduction) validated

---

## HIGH PRIORITY

### 2. Background Thread for Database Vacuum

**Issue:** Database vacuum operation blocks GUI thread, causing application freeze.

**Impact:**
- Poor user experience (unresponsive GUI)
- No progress indication during operation
- No way to cancel long-running vacuum

**Fix Location:**
`src/ui/widgets/performance_dashboard_widget.py` - `_on_vacuum_clicked()` method

**Implementation:**

```python
# File: src/ui/widgets/performance_dashboard_widget.py
# Add to imports:
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, QThreadPool

# Add after imports, before PerformanceDashboardWidget class:

class WorkerSignals(QObject):
    """Signals for background worker threads."""
    finished = pyqtSignal(bool, str, dict)  # (success, message, stats)
    error = pyqtSignal(str)  # error_message


class VacuumWorker(QRunnable):
    """
    Background worker for database vacuum operation.

    Executes vacuum in thread pool to prevent GUI freezing.
    Emits signals when complete for UI updates.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize vacuum worker.

        Args:
            db_manager: Database manager instance
        """
        super().__init__()
        self.db_manager = db_manager
        self.signals = WorkerSignals()

    def run(self) -> None:
        """Execute vacuum operation in background thread."""
        try:
            logger.info("Starting database vacuum in background thread")
            success, message, stats = self.db_manager.vacuum_database()
            self.signals.finished.emit(success, message, stats)
        except Exception as e:
            logger.error(f"Vacuum worker error: {e}", exc_info=True)
            self.signals.error.emit(str(e))


# In PerformanceDashboardWidget class, replace _on_vacuum_clicked():

def _on_vacuum_clicked(self) -> None:
    """Handle vacuum database button click (background thread)."""
    if not self.db_manager:
        logger.warning("Cannot vacuum database: no db manager")
        return

    try:
        self.vacuum_button.setEnabled(False)
        self.vacuum_button.setText("Vacuuming...")
        self.recommendations_label.setText("Database vacuum in progress...")
        self.recommendations_label.setStyleSheet(
            "padding: 10px; background-color: #E3F2FD; "
            "border: 2px solid #2196F3; border-radius: 5px;"
        )

        logger.info("Starting database vacuum (user-initiated, background thread)")

        # Create and start worker in background
        worker = VacuumWorker(self.db_manager)
        worker.signals.finished.connect(self._on_vacuum_finished)
        worker.signals.error.connect(self._on_vacuum_error)
        QThreadPool.globalInstance().start(worker)

    except Exception as e:
        logger.error(f"Error starting vacuum worker: {e}")
        self._on_vacuum_error(str(e))


def _on_vacuum_finished(self, success: bool, message: str, stats: dict) -> None:
    """
    Handle completion of vacuum operation (called from background thread signal).

    Args:
        success: Whether vacuum succeeded
        message: Result message
        stats: Vacuum statistics dictionary
    """
    try:
        if success:
            logger.info(f"Database vacuum complete: {message}")
            reduction = stats.get('size_reduction_percent', 0)
            self.recommendations_label.setText(
                f"Vacuum complete: {reduction:.1f}% reduction "
                f"({stats.get('size_before_mb', 0):.1f}MB → {stats.get('size_after_mb', 0):.1f}MB)"
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

        # Refresh metrics to show updated database size
        self.update_metrics()

    except Exception as e:
        logger.error(f"Error handling vacuum completion: {e}")
        self._on_vacuum_error(str(e))

    finally:
        self.vacuum_button.setEnabled(True)
        self.vacuum_button.setText("Vacuum Database")


def _on_vacuum_error(self, error_message: str) -> None:
    """
    Handle vacuum operation error (called from background thread signal).

    Args:
        error_message: Error description
    """
    logger.error(f"Vacuum operation error: {error_message}")
    self.recommendations_label.setText(f"Vacuum error: {error_message}")
    self.recommendations_label.setStyleSheet(
        "padding: 10px; background-color: #FFEBEE; "
        "border: 2px solid #F44336; border-radius: 5px;"
    )
    self.vacuum_button.setEnabled(True)
    self.vacuum_button.setText("Vacuum Database")
```

**Testing Criteria:**

1. **GUI Responsiveness:**
   - Click vacuum button
   - Verify GUI remains responsive during operation
   - Verify can interact with other widgets
   - Verify status updates appear

2. **Completion Handling:**
   - Verify success message shows statistics
   - Verify failure message shows error
   - Verify button re-enables after completion

3. **Large Database Test:**
   - Create large database (100MB+)
   - Trigger vacuum
   - Confirm no GUI freeze during long operation

**Estimated Effort:** 1 hour

**Completion Criteria:**
- [ ] Code changes implemented
- [ ] GUI remains responsive during vacuum
- [ ] Success/failure signals work correctly
- [ ] Button state managed properly
- [ ] Follows Week 5 AsyncIO documentation patterns

---

### 3. Fix Hardcoded Validator

**Issue:** Safety config validator hardcodes GPIO timeout instead of reading from configuration.

**Impact:**
- Configuration becomes brittle
- Changes to `watchdog_timeout_ms` won't update validator
- Potential validation mismatch

**Fix Location:**
`src/config/models.py` - `SafetyConfig.validate_heartbeat()` method

**Implementation:**

```python
# File: src/config/models.py
# Replace the existing field_validator with this:

class SafetyConfig(BaseModel):
    """Safety system configuration."""

    watchdog_enabled: bool = Field(default=True, description="Enable hardware watchdog timer")
    watchdog_heartbeat_ms: int = Field(
        default=500,
        ge=100,
        le=4000,
        description="Heartbeat interval (must be < watchdog timeout)",
    )
    emergency_stop_enabled: bool = Field(
        default=True, description="Enable emergency stop functionality"
    )
    interlock_check_enabled: bool = Field(
        default=True, description="Enable safety interlock checking"
    )
    laser_enable_requires_interlocks: bool = Field(
        default=True, description="Laser cannot enable without valid interlocks"
    )

    # REMOVE OLD VALIDATOR (lines 121-128)
    # Add this at the TOSCAConfig level instead


class TOSCAConfig(BaseModel):
    """Root configuration for TOSCA system."""

    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    gui: GUIConfig = Field(default_factory=GUIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @model_validator(mode="after")
    def validate_heartbeat_against_timeout(self) -> "TOSCAConfig":
        """
        Ensure heartbeat is less than watchdog timeout.

        Validates that safety heartbeat interval is shorter than
        the GPIO watchdog timeout to prevent false timeout triggers.

        Returns:
            Validated config instance

        Raises:
            ValueError: If heartbeat >= timeout
        """
        heartbeat = self.safety.watchdog_heartbeat_ms
        timeout = self.hardware.gpio.watchdog_timeout_ms

        if heartbeat >= timeout:
            raise ValueError(
                f"Safety heartbeat interval ({heartbeat}ms) must be less than "
                f"GPIO watchdog timeout ({timeout}ms). "
                f"Recommended: heartbeat = timeout / 2 = {timeout // 2}ms"
            )

        # Additional safety margin check (heartbeat should be < 90% of timeout)
        safety_margin = 0.9
        if heartbeat >= timeout * safety_margin:
            logger.warning(
                f"Safety heartbeat ({heartbeat}ms) is close to timeout ({timeout}ms). "
                f"Recommended margin: heartbeat < {timeout * safety_margin:.0f}ms"
            )

        return self
```

**Testing Criteria:**

1. **Valid Configuration:**
   ```yaml
   hardware:
     gpio:
       watchdog_timeout_ms: 1000
   safety:
     watchdog_heartbeat_ms: 500  # Valid (< 1000)
   ```
   - Should load without errors

2. **Invalid Configuration:**
   ```yaml
   hardware:
     gpio:
       watchdog_timeout_ms: 1000
   safety:
     watchdog_heartbeat_ms: 1000  # Invalid (>= timeout)
   ```
   - Should raise ValueError with clear message

3. **Warning Case:**
   ```yaml
   hardware:
     gpio:
       watchdog_timeout_ms: 1000
   safety:
     watchdog_heartbeat_ms: 950  # Close to limit
   ```
   - Should load but log warning

**Estimated Effort:** 15-30 minutes

**Completion Criteria:**
- [ ] Validator reads from actual config values
- [ ] Error messages are clear and actionable
- [ ] Warning for near-threshold values
- [ ] Tests added for valid/invalid cases

---

## LOW PRIORITY

### 4. QTimer Cleanup on Widget Destruction

**Issue:** Performance dashboard timer not stopped when widget destroyed.

**Impact:**
- Potential memory leak
- Timer continues firing on deleted widget
- Resource waste

**Fix Location:**
`src/ui/widgets/performance_dashboard_widget.py` - Add `closeEvent()` method

**Implementation:**

```python
# File: src/ui/widgets/performance_dashboard_widget.py
# Add to imports:
from PyQt6.QtGui import QCloseEvent

# Add to PerformanceDashboardWidget class:

def closeEvent(self, event: QCloseEvent) -> None:
    """
    Handle widget close event.

    Ensures timer is stopped when widget is closed or destroyed
    to prevent resource leaks and callbacks on deleted widgets.

    Args:
        event: Close event
    """
    logger.debug("Performance dashboard closing, stopping auto-refresh")
    self.stop_auto_refresh()
    super().closeEvent(event)

def stop_auto_refresh(self) -> None:
    """Stop automatic metric refresh timer."""
    if hasattr(self, "refresh_timer") and self.refresh_timer.isActive():
        self.refresh_timer.stop()
        logger.info("Performance dashboard auto-refresh stopped")
```

**Testing Criteria:**

1. **Manual Test:**
   - Open performance dashboard
   - Verify timer running (5-second updates)
   - Close widget
   - Verify no errors in logs
   - Verify timer stopped

2. **Resource Test:**
   - Open and close dashboard 100 times
   - Check memory usage doesn't grow
   - Verify no timer callbacks on closed widget

**Estimated Effort:** 10 minutes

**Completion Criteria:**
- [ ] closeEvent() implemented
- [ ] Timer verified stopped on close
- [ ] No errors when widget destroyed
- [ ] Follows Qt best practices

---

### 5. Document Single-Process Assumption

**Issue:** Log rotation code has theoretical race condition in multi-process scenario.

**Impact:**
- Minimal (TOSCA is single-process medical device)
- Could matter if architecture changes

**Fix Location:**
`src/core/event_logger.py` - Add documentation

**Implementation:**

```python
# File: src/core/event_logger.py
# Add to module docstring at top of file:

"""
Event logger for TOSCA treatment system.

Provides immutable audit trail for all safety-critical and operational events.
Integrates with database SafetyLog table for persistence and emits PyQt6 signals.

ARCHITECTURE ASSUMPTION:
This implementation assumes single-process operation. The log rotation and
cleanup methods are not designed for concurrent access from multiple processes.

If TOSCA architecture changes to support multi-process operation (e.g., separate
processes for UI and hardware control), the following changes would be required:

1. Add file-based locking around rotation check-and-rename operation:
   ```python
   from filelock import FileLock

   lock = FileLock(str(self.log_file) + ".lock")
   with lock:
       # Perform rotation atomically
   ```

2. Use inter-process signaling for log cleanup coordination

3. Consider using a dedicated logging service/daemon

Current implementation is appropriate for single-process medical device software.
"""

# Add to _check_and_rotate_log() docstring:

def _check_and_rotate_log(self) -> None:
    """
    Check if log file needs rotation and rotate if necessary.

    Rotation occurs when the current log file exceeds rotation_size_mb.
    Rotated files are named with timestamp: events_YYYY-MM-DD_HH-MM-SS.jsonl

    THREAD SAFETY: This method is safe for single-process, multi-threaded use.
    The try-except block handles race conditions from concurrent rotation attempts.

    NOT SAFE FOR: Multi-process concurrent access. Would require file locking.
    """

# Add to _cleanup_old_logs() docstring:

def _cleanup_old_logs(self) -> None:
    """
    Clean up log files older than retention_days.

    Scans the log directory for rotated log files (events_YYYY-MM-DD_*.jsonl)
    and deletes files older than the retention period.

    THREAD SAFETY: This method is safe for single-process, multi-threaded use.
    File deletion is atomic at the OS level.

    NOT SAFE FOR: Multi-process concurrent cleanup. Would require coordination.
    """
```

**Testing Criteria:**
- Documentation review
- Architectural decision recorded
- Future maintainers aware of assumption

**Estimated Effort:** 10 minutes

**Completion Criteria:**
- [ ] Module docstring updated
- [ ] Method docstrings clarified
- [ ] Multi-process requirements documented
- [ ] Assumption clearly stated

---

## TESTING REQUIREMENTS

### Unit Tests Required

**File:** `tests/test_database/test_db_vacuum.py` (NEW)

```python
"""
Unit tests for database vacuum operation.

Tests vacuum functionality, error handling, and statistics calculation.
"""

import pytest
from pathlib import Path
from src.database.db_manager import DatabaseManager


def test_vacuum_reduces_size():
    """Test that vacuum reduces database file size."""
    # Create database with some data
    db = DatabaseManager("test_vacuum.db")
    db.initialize()

    # Add and delete data to create fragmentation
    # ... (implementation details)

    # Vacuum and verify size reduction
    success, message, stats = db.vacuum_database()
    assert success
    assert stats['size_reduction_percent'] >= 0

def test_vacuum_handles_missing_file():
    """Test vacuum handles missing database file gracefully."""
    db = DatabaseManager("nonexistent.db")
    success, message, stats = db.vacuum_database()
    assert not success
    assert "not found" in message.lower()

def test_vacuum_statistics_accurate():
    """Test vacuum statistics calculation is accurate."""
    # ... (implementation)
```

**File:** `tests/test_core/test_log_rotation.py` (NEW)

```python
"""
Unit tests for log rotation and cleanup.

Tests rotation trigger, file naming, and retention policy.
"""

def test_rotation_at_size_threshold():
    """Test log rotates when size exceeds threshold."""
    # ... (implementation)

def test_cleanup_deletes_old_logs():
    """Test old logs are deleted based on retention policy."""
    # ... (implementation)

def test_rotation_filename_format():
    """Test rotated files have correct timestamp format."""
    # ... (implementation)
```

**File:** `tests/test_hardware/test_video_compression.py` (NEW)

```python
"""
Unit tests for video compression and codec handling.

Tests H.264 CRF parameter application and codec fallback.
"""

def test_h264_crf_reduces_file_size():
    """Test CRF parameter actually affects file size."""
    # Record with CRF=28 and CRF=18
    # Verify CRF=28 produces smaller file

def test_codec_fallback_works():
    """Test fallback to MJPEG when H.264 unavailable."""
    # ... (implementation)

def test_crf_config_setting_honored():
    """Test video_quality_crf config setting is applied."""
    # ... (implementation)
```

---

## COMPLETION CHECKLIST

### Critical Priority (Must Complete)

- [ ] H.264 CRF implementation
  - [ ] Code changes in camera_controller.py
  - [ ] Environment variable handling
  - [ ] Cleanup on both primary and fallback codecs
  - [ ] Manual testing (file size reduction verification)
  - [ ] Automated test added
  - [ ] Week 4 goal (50% reduction) validated
  - [ ] Documentation updated

### High Priority (Should Complete)

- [ ] Background vacuum operation
  - [ ] QRunnable worker class created
  - [ ] Signal/slot integration
  - [ ] Error handling
  - [ ] GUI responsiveness verified
  - [ ] Large database test passed

- [ ] Hardcoded validator fix
  - [ ] model_validator on TOSCAConfig
  - [ ] Read from actual config values
  - [ ] Clear error messages
  - [ ] Warning for near-threshold values
  - [ ] Unit tests for validation

### Low Priority (Good to Complete)

- [ ] QTimer cleanup
  - [ ] closeEvent() implemented
  - [ ] Timer verified stopped
  - [ ] Resource leak test passed

- [ ] Documentation
  - [ ] Single-process assumption documented
  - [ ] Multi-process requirements noted
  - [ ] Architecture decision recorded

### Testing

- [ ] Database vacuum tests (3+ tests)
- [ ] Log rotation tests (3+ tests)
- [ ] Video compression tests (3+ tests)
- [ ] Integration test for 50% compression goal

### Documentation

- [ ] WORK_LOG.md updated with fixes
- [ ] PROJECT_STATUS.md updated
- [ ] LESSONS_LEARNED.md entry for CRF limitation
- [ ] config.yaml documentation clarified

---

## Timeline Estimate

### Immediate (Today):
- Fix H.264 CRF implementation (30-45 min)
- Validate compression ratio achieved (15 min)

### Short-term (This Week):
- Background vacuum threading (1 hour)
- Hardcoded validator fix (30 min)
- QTimer cleanup (10 min)
- Documentation updates (30 min)

### Medium-term (Next Week):
- Write unit tests (3-4 hours)
- Integration testing (1-2 hours)
- Documentation review (1 hour)

**Total Estimated Effort:** 8-10 hours

---

## Success Criteria

Week 4-5 will be considered COMPLETE when:

1. ✅ H.264 CRF properly implemented and validated
2. ✅ 50% compression ratio achieved and documented
3. ✅ Background vacuum prevents GUI freezing
4. ✅ All high-priority fixes implemented
5. ✅ Test coverage added for new features
6. ✅ Documentation updated

---

**Document Version:** 1.0
**Last Updated:** 2025-10-31
**Next Review:** After critical fixes implemented
