# Camera HAL Testing Guide

**Purpose:** Comprehensive testing procedures for Camera Hardware Abstraction Layer

**Hardware Required:** Allied Vision 1800 U-158c camera (USB 3.0)

**Last Updated:** 2025-10-23

---

## Pre-Test Setup

### 1. Hardware Connection
- [ ] Connect Allied Vision camera to USB 3.0 port
- [ ] Ensure camera has power (check LED indicator)
- [ ] Verify no other applications are using the camera

### 2. Software Requirements
- [ ] VmbPy installed: `pip install vmbpy`
- [ ] Vimba SDK installed (VmbPy dependency)
- [ ] Virtual environment activated: `venv\Scripts\activate`
- [ ] Application runs: `python src/main.py`

### 3. Pre-Test Validation
Run quick validation script to ensure camera is detected:
```bash
cd components/camera_module/examples
python 01_list_cameras.py
```

**Expected Output:**
```
Camera detected: DEV_1AB22C04E780
Model: 1800 U-158c
```

If camera not detected, troubleshoot hardware connection before proceeding.

---

## Test Suite

### Test 1: Camera Connection

**Objective:** Verify camera connects successfully

**Steps:**
1. Launch application: `python src/main.py`
2. Navigate to "Camera/Alignment" tab
3. Click "Connect Camera" button

**Expected Results:**
- [ ] Button text changes to "Disconnect"
- [ ] Status label shows "Status: Connected" in green
- [ ] "Start Streaming" button becomes enabled
- [ ] No error messages appear

**Pass Criteria:**
- Connection successful within 2 seconds
- Status correctly reflects connection state

**If Failed:**
- Check camera is not in use by another application
- Check logs in `data/logs/tosca.log` for error details
- Verify VmbPy installation

---

### Test 2: Live Streaming

**Objective:** Verify live video stream works at full frame rate

**Steps:**
1. With camera connected, click "Start Streaming"
2. Observe live feed for 30 seconds
3. Note FPS display

**Expected Results:**
- [ ] Live video feed appears in display area
- [ ] FPS shows 39-40 FPS (camera maximum)
- [ ] Video is smooth with no stuttering
- [ ] Button text changes to "Stop Streaming"
- [ ] Exposure and gain controls become enabled

**Pass Criteria:**
- FPS ≥ 35 FPS sustained for 30 seconds
- No dropped frames or freezing
- Video quality is clear

**If Failed:**
- Check USB bandwidth (close other USB devices)
- Review logs for frame callback errors
- Test with simpler examples in components/camera_module/examples/

---

### Test 3: Exposure Control (Manual)

**Objective:** Verify manual exposure adjustment works

**Steps:**
1. With streaming active, ensure "Auto" exposure is unchecked
2. Move exposure slider from minimum to maximum
3. Use exposure input box to set specific values:
   - Enter 1000 (1ms)
   - Enter 10000 (10ms)
   - Enter 50000 (50ms)

**Expected Results:**
- [ ] Image brightness changes as slider moves
- [ ] Dark image at low exposure (~1ms)
- [ ] Bright image at high exposure (~50ms)
- [ ] Input box updates when slider moves
- [ ] Slider updates when input box value entered
- [ ] Values displayed in label match settings

**Pass Criteria:**
- Exposure changes take effect within 1 second
- Visible brightness difference between min and max
- No crashes or errors

**Notes:**
Record actual exposure range from camera:
- Min exposure: ______ µs
- Max exposure: ______ µs

---

### Test 4: Exposure Control (Auto)

**Objective:** Verify auto-exposure mode works

**Steps:**
1. With streaming active, check "Auto" exposure checkbox
2. Point camera at bright area (window, light)
3. Point camera at dark area
4. Observe image brightness adjustment

**Expected Results:**
- [ ] Manual exposure controls disable when auto enabled
- [ ] Image brightness adjusts automatically
- [ ] Bright scenes → exposure decreases
- [ ] Dark scenes → exposure increases
- [ ] Adjustment happens within 1-2 seconds

**Pass Criteria:**
- Auto-exposure maintains consistent brightness
- No extreme over/under exposure
- Smooth transitions

**If Failed:**
- Check camera supports ExposureAuto feature
- Review logs for feature access errors

---

### Test 5: Gain Control (Manual)

**Objective:** Verify manual gain adjustment works

**Steps:**
1. With streaming active, ensure "Auto" gain is unchecked
2. Set exposure to low value (e.g., 5000 µs)
3. Move gain slider from 0 dB to maximum
4. Use gain input box to set specific values:
   - Enter 0.0
   - Enter 12.0
   - Enter 24.0 (or max available)

**Expected Results:**
- [ ] Image brightness changes with gain
- [ ] Dark image at 0 dB gain
- [ ] Brighter image at high gain
- [ ] Some noise visible at high gain (expected)
- [ ] Input box and slider stay synchronized
- [ ] Values displayed in label match settings

**Pass Criteria:**
- Gain changes take effect within 1 second
- Visible brightness increase with gain
- No crashes

**Notes:**
Record actual gain range from camera:
- Min gain: ______ dB
- Max gain: ______ dB

---

### Test 6: Gain Control (Auto)

**Objective:** Verify auto-gain mode works

**Steps:**
1. With streaming active, check "Auto" gain checkbox
2. Set exposure to fixed low value
3. Point camera at bright and dark areas
4. Observe gain adjustment

**Expected Results:**
- [ ] Manual gain controls disable when auto enabled
- [ ] Gain adjusts to maintain brightness
- [ ] Works in conjunction with auto-exposure if both enabled

**Pass Criteria:**
- Auto-gain maintains consistent brightness
- Smooth transitions

---

### Test 7: Auto White Balance

**Objective:** Verify auto white balance works

**Steps:**
1. With streaming active, check "Auto" white balance checkbox
2. Point camera at different lighting conditions:
   - Daylight (bluish)
   - Incandescent light (yellowish)
   - Fluorescent light (greenish)

**Expected Results:**
- [ ] Color tone adjusts for different light sources
- [ ] White objects appear white (not tinted)
- [ ] Adjustment happens within 2-3 seconds

**Pass Criteria:**
- White balance adapts to light source
- Colors appear natural

**If Failed:**
- Check camera supports BalanceWhiteAuto feature
- Some cameras may not support this feature

---

### Test 8: Image Capture

**Objective:** Verify still image capture works

**Steps:**
1. With streaming active, enter custom filename: "test_capture"
2. Click "Capture Image" button
3. Check saved file location displayed in label
4. Navigate to `data/images/` directory
5. Verify image file exists
6. Open image and verify quality

**Expected Results:**
- [ ] Label shows "Saved: [path]" in green text
- [ ] File exists at specified path
- [ ] Filename format: `test_capture_YYYYMMDD_HHMMSS.png`
- [ ] Image opens correctly
- [ ] Image resolution matches camera: 1456x1088
- [ ] Image quality is good (no corruption)
- [ ] Colors are correct (RGB not BGR)

**Pass Criteria:**
- Image saves successfully
- Image quality matches live feed
- Timestamp prevents overwriting

**Test Variations:**
- [ ] Capture with default filename ("capture")
- [ ] Capture multiple images (verify unique timestamps)
- [ ] Change base filename between captures

---

### Test 9: Image Capture (Dev Mode - Custom Path)

**Objective:** Verify custom save path works in dev mode

**Prerequisites:**
- Enable dev mode (check implementation in main_window.py)

**Steps:**
1. Enable developer mode
2. In image capture section, verify "Custom Save Path" is visible
3. Click "Browse..." and select desktop or temp folder
4. Enter filename: "dev_test"
5. Click "Capture Image"
6. Verify file saved to custom path

**Expected Results:**
- [ ] Custom path controls visible in dev mode
- [ ] Browse dialog opens correctly
- [ ] Selected path displays in input box
- [ ] Image saves to custom path
- [ ] File accessible at custom location

**Pass Criteria:**
- Custom path respected
- No permission errors
- File saved successfully

---

### Test 10: Video Recording

**Objective:** Verify video recording works

**Steps:**
1. With streaming active, enter filename: "test_recording"
2. Click "Start Recording" button
3. Record for 10 seconds
4. Move camera or change scene during recording
5. Click "Stop Recording"
6. Navigate to `data/videos/` directory
7. Open video file

**Expected Results:**
- [ ] Button text changes to "Stop Recording"
- [ ] Recording indicator shows "● REC" in red
- [ ] Status shows "Recording..." in red
- [ ] File saves to data/videos/
- [ ] Filename format: `test_recording_YYYYMMDD_HHMMSS.mp4`
- [ ] Video plays correctly
- [ ] Video duration ~10 seconds
- [ ] Video frame rate: ~30 FPS
- [ ] Audio: none (expected - camera has no audio)

**Pass Criteria:**
- Video records without errors
- Video quality matches live feed
- No frame drops or corruption

**Test Variations:**
- [ ] Record short video (5 seconds)
- [ ] Record longer video (60 seconds)
- [ ] Verify file size reasonable (~1-2 MB per 10 sec)

---

### Test 11: Video Recording (Dev Mode - Custom Path)

**Objective:** Verify custom video save path in dev mode

**Steps:**
1. Enable developer mode
2. In recording section, click "Browse..." for video path
3. Select custom directory
4. Enter filename: "custom_video"
5. Start and stop recording
6. Verify file at custom location

**Expected Results:**
- [ ] Custom path controls visible
- [ ] Video saves to custom path
- [ ] No permission errors

**Pass Criteria:**
- Custom path works for video
- File accessible

---

### Test 12: Simultaneous Image Capture and Recording

**Objective:** Verify capture works during recording

**Steps:**
1. Start video recording
2. While recording, capture 3 still images
3. Stop recording
4. Verify all files saved

**Expected Results:**
- [ ] Images captured successfully during recording
- [ ] Video recording not interrupted
- [ ] All files exist and are valid

**Pass Criteria:**
- Both features work simultaneously
- No conflicts or errors

---

### Test 13: Stop/Start Streaming Cycles

**Objective:** Verify streaming can be stopped and restarted

**Steps:**
1. Start streaming
2. Stop streaming
3. Repeat 5 times
4. Verify each cycle works

**Expected Results:**
- [ ] Each start/stop cycle works
- [ ] No memory leaks (monitor task manager)
- [ ] No degradation over cycles
- [ ] No crashes

**Pass Criteria:**
- Reliable start/stop behavior
- No resource leaks

---

### Test 14: Disconnect/Reconnect Camera

**Objective:** Verify graceful handling of connection cycles

**Steps:**
1. Connect camera
2. Start streaming
3. Stop streaming
4. Disconnect camera
5. Reconnect camera
6. Verify works after reconnect

**Expected Results:**
- [ ] Disconnect completes cleanly
- [ ] Reconnect works without app restart
- [ ] All features work after reconnect

**Pass Criteria:**
- Clean connection management
- No residual state issues

---

### Test 15: Error Handling - Camera Unplugged During Streaming

**Objective:** Verify graceful error handling

**WARNING: WARNING:** This test intentionally causes an error

**Steps:**
1. Start streaming
2. Physically unplug camera USB cable
3. Observe application behavior
4. Reconnect camera
5. Try to reconnect via GUI

**Expected Results:**
- [ ] Application does not crash
- [ ] Error message displayed to user
- [ ] Connection status updates to "Not Connected"
- [ ] Streaming stops gracefully
- [ ] Logs contain error details
- [ ] Can reconnect after plugging camera back in

**Pass Criteria:**
- No application crash
- Clear error messaging
- Recoverable state

**If Failed:**
- Check exception handling in streaming thread
- Review disconnect/cleanup code

---

### Test 16: Long-Duration Streaming

**Objective:** Verify stability over extended operation

**Steps:**
1. Start streaming
2. Leave running for 10 minutes
3. Monitor FPS and performance
4. Check memory usage (Task Manager)

**Expected Results:**
- [ ] FPS remains stable (39-40 FPS)
- [ ] No memory leaks (memory usage stable)
- [ ] No frame drops
- [ ] No crashes or freezes
- [ ] CPU usage reasonable (<30%)

**Pass Criteria:**
- Sustained performance
- No resource leaks
- Stable operation

**Notes:**
Initial memory: ______ MB
After 10 min: ______ MB
Average FPS: ______ FPS
CPU usage: ______ %

---

### Test 17: Multiple Features Simultaneously

**Objective:** Verify all features work together

**Steps:**
1. Connect camera and start streaming
2. Enable auto-exposure
3. Enable auto-gain
4. Enable auto-white-balance
5. Start video recording
6. Capture 5 still images during recording
7. Stop recording
8. Verify all files saved

**Expected Results:**
- [ ] All auto features work together
- [ ] Recording works with auto features
- [ ] Image capture works during recording
- [ ] Performance remains good (30+ FPS)
- [ ] All files valid and correct

**Pass Criteria:**
- No feature conflicts
- Stable performance
- All files correct

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| **Connection Time** | <1s | <2s | >2s |
| **Streaming FPS** | 39-40 | 35-39 | <35 |
| **Exposure Response** | <500ms | <1s | >1s |
| **Gain Response** | <500ms | <1s | >1s |
| **Image Capture Time** | <200ms | <500ms | >500ms |
| **Video Start Time** | <500ms | <1s | >1s |
| **CPU Usage (idle)** | <5% | <10% | >10% |
| **CPU Usage (streaming)** | <20% | <30% | >30% |
| **Memory Usage** | <200MB | <300MB | >300MB |

### Record Your Results

**Camera Info:**
- Model: ______________
- Serial: ______________
- Max Resolution: ______________
- Max FPS: ______________

**Performance:**
- Connection time: ______ ms
- Average FPS: ______ FPS
- Image capture time: ______ ms
- CPU usage streaming: ______ %
- Memory usage: ______ MB

---

## Test Results Summary

**Date Tested:** ______________
**Tester:** ______________
**Camera Model:** ______________
**OS:** Windows ______

### Overall Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Connection | ☐ Pass ☐ Fail | |
| 2. Live Streaming | ☐ Pass ☐ Fail | |
| 3. Exposure (Manual) | ☐ Pass ☐ Fail | |
| 4. Exposure (Auto) | ☐ Pass ☐ Fail | |
| 5. Gain (Manual) | ☐ Pass ☐ Fail | |
| 6. Gain (Auto) | ☐ Pass ☐ Fail | |
| 7. White Balance | ☐ Pass ☐ Fail | |
| 8. Image Capture | ☐ Pass ☐ Fail | |
| 9. Image (Custom Path) | ☐ Pass ☐ Fail | |
| 10. Video Recording | ☐ Pass ☐ Fail | |
| 11. Video (Custom Path) | ☐ Pass ☐ Fail | |
| 12. Simultaneous Ops | ☐ Pass ☐ Fail | |
| 13. Stop/Start Cycles | ☐ Pass ☐ Fail | |
| 14. Reconnect | ☐ Pass ☐ Fail | |
| 15. Error Handling | ☐ Pass ☐ Fail | |
| 16. Long Duration | ☐ Pass ☐ Fail | |
| 17. Multiple Features | ☐ Pass ☐ Fail | |

**Total Passed:** _____ / 17
**Total Failed:** _____ / 17

---

## Known Issues

Document any issues found during testing:

1. **Issue:**
   - **Severity:** Critical / High / Medium / Low
   - **Reproducible:** Yes / No
   - **Workaround:**

2. **Issue:**
   - **Severity:**
   - **Reproducible:**
   - **Workaround:**

---

## Post-Test Actions

After completing tests:

- [ ] Review all test results
- [ ] Document any failures in LESSONS_LEARNED.md
- [ ] Create issues for bugs found
- [ ] Update WORK_LOG.md with test results
- [ ] Update PROJECT_STATUS.md if major milestone reached
- [ ] Save test results file for records

---

## Troubleshooting Guide

### Camera Not Detected
- Check USB connection (try different port)
- Verify Vimba SDK installed
- Check Windows Device Manager
- Run: `components/camera_module/examples/01_list_cameras.py`

### Low Frame Rate
- Close other USB devices (bandwidth)
- Check CPU usage
- Disable unnecessary features
- Try lower resolution

### Exposure/Gain Not Working
- Check camera supports feature
- Review logs for errors
- Try manual examples first: `04_explore_features.py`

### Image/Video Save Fails
- Check disk space
- Verify write permissions
- Check output directory exists
- Review logs for errors

---

**Testing Complete!**

Camera HAL validation requires all 17 tests to pass for production readiness.
Document any failures and create action items for fixes.
