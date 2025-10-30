# Camera System Test Suite

Comprehensive test suite for camera performance, thread safety, and UI responsiveness.

## Test Files

### `test_camera_performance.py`
Tests for camera controller performance and optimization effectiveness.

**Test Classes:**
- `TestCameraPerformance`: Frame rate, signal emission, downsampling effectiveness
- `TestCameraThreadSafety`: Concurrent access, thread safety validation
- `TestCameraIntegration`: Full workflow integration tests

**Key Tests:**
- `test_pixmap_signal_emission`: Verifies QPixmap signals are emitted correctly
- `test_frame_downsampling_reduces_size`: Confirms 16× size reduction with 0.25× scale
- `test_exposure_limit_clamping`: Auto exposure limits stay within camera bounds
- `test_multiple_feature_name_fallback`: Compatibility across camera models
- `test_concurrent_exposure_changes`: Thread-safe concurrent access

### `test_camera_widget_performance.py`
Tests for camera widget UI performance and responsiveness.

**Test Classes:**
- `TestCameraWidgetPerformance`: Widget rendering performance
- `TestCameraWidgetUIResponsiveness`: UI interaction during streaming

**Key Tests:**
- `test_pixmap_received_is_fast`: Verifies >30 FPS processing capability
- `test_safety_limiter_blocks_long_exposure`: Prevents frame-drop-causing exposures
- `test_auto_exposure_disables_manual_controls`: UI state management
- `test_button_clicks_during_frame_updates`: UI remains responsive at 30 FPS

## Running Tests

### Run All Camera Tests
```bash
pytest tests/test_camera_*.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_camera_performance.py::TestCameraPerformance -v
```

### Run with Coverage
```bash
pytest tests/test_camera_*.py --cov=src/hardware/camera_controller --cov=src/ui/widgets/camera_widget --cov-report=html
```

### Run Performance Tests Only
```bash
pytest tests/test_camera_*.py -v -k "performance"
```

## Expected Performance Benchmarks

### Frame Processing Speed
- **Target**: >30 FPS (< 33ms per frame)
- **Test**: `test_pixmap_received_is_fast`
- **Success Criteria**: Process 30 frames in <1 second

### Bandwidth Savings
- **Full Resolution**: ~8.7 MB/s at 30 FPS
- **Quarter Resolution (0.25×)**: ~0.5 MB/s at 30 FPS
- **Savings**: 93% bandwidth reduction
- **Test**: `test_frame_downsampling_reduces_size`

### Auto Exposure Limits
- **Target**: ≤30ms (safe for 30 FPS)
- **Test**: `test_exposure_limit_clamping`
- **Success Criteria**: Never exceeds 30,000 µs or camera maximum

### Thread Safety
- **Test**: `test_concurrent_exposure_changes`
- **Success Criteria**: No race conditions during concurrent access

### UI Responsiveness
- **Test**: `test_button_clicks_during_frame_updates`
- **Success Criteria**: Buttons clickable during 30 FPS streaming

## Test Dependencies

Required packages (in `requirements.txt`):
```
pytest>=7.0
pytest-qt>=4.0
pytest-cov>=4.0
numpy>=1.24
PyQt6>=6.4
```

## Troubleshooting

### Tests Fail with "QApplication not available"
Make sure you're running with pytest-qt:
```bash
pip install pytest-qt
```

### Mock Camera Tests Skip
Some tests require VmbPy to be installed. Install with:
```bash
pip install vmbpy
```

### Performance Tests Fail
Performance tests are sensitive to system load. Run with:
```bash
pytest tests/test_camera_widget_performance.py --benchmark-only
```

## Continuous Integration

These tests should be run:
1. Before committing camera-related changes
2. After updating VmbPy or PyQt6 versions
3. During pre-release validation
4. When performance degradation is suspected

## Medical Device Validation

Per IEC 62304 requirements:
- All safety-critical camera functions have unit tests
- Performance tests validate real-time capabilities
- Thread safety tests prevent race conditions
- UI responsiveness tests ensure operator can intervene

**Test Coverage Target**: >90% for camera-related modules

## Known Issues

1. **FPS Drops Over Time**: Current issue where GUI FPS drops from 16→2 FPS during streaming. Root cause: numpy array signal still being processed alongside QPixmap signal. **Fix in progress**.

2. **Unicode Logging Error**: Arrow character `→` in log messages causes Windows console encoding error. Non-critical, doesn't affect functionality.

## Future Test Additions

- [ ] Load testing with multiple camera instances
- [ ] Memory leak detection during extended streaming
- [ ] Frame drop detection and logging
- [ ] Integration tests with real Allied Vision hardware
- [ ] Automated FPS benchmarking suite
