# Camera HAL Testing - Quick Start

**Quick reference for testing Camera Hardware Abstraction Layer**

---

## Step 1: Prepare Hardware

1. Connect Allied Vision camera to USB 3.0 port
2. Verify camera LED is on
3. Close any other camera applications

---

## Step 2: Quick Validation (2 minutes)

Run automated validation script:

```bash
cd components/camera_module
python test_hal_integration.py
```

**Expected Output:**
```
✓ PASS - Camera Connection
✓ PASS - Camera Information
✓ PASS - Exposure/Gain Ranges
✓ PASS - Brief Streaming
✓ PASS - Exposure Control
✓ PASS - Gain Control

Total: 6 passed, 0 failed out of 6 tests
✓ All tests passed! Camera HAL is working correctly.
```

**If all tests pass:** Proceed to Step 3 (GUI testing)

**If tests fail:**
- Check hardware connection
- Review `data/logs/tosca.log` for errors
- Run basic examples: `cd examples && python 01_list_cameras.py`

---

## Step 3: Full GUI Testing (30 minutes)

Launch full application:

```bash
python src/main.py
```

### Quick Test Sequence:

1. **Connection** (1 min)
   - Go to "Camera/Alignment" tab
   - Click "Connect Camera"
   - Verify: Status shows "Connected" (green)

2. **Streaming** (2 min)
   - Click "Start Streaming"
   - Verify: Live video feed appears, FPS shows 39-40

3. **Manual Controls** (5 min)
   - Move exposure slider → verify brightness changes
   - Move gain slider → verify brightness changes
   - Try input boxes → verify values update

4. **Auto Controls** (5 min)
   - Check "Auto" exposure → verify auto-adjustment
   - Check "Auto" gain → verify auto-adjustment
   - Check "Auto" white balance → verify color adjustment

5. **Image Capture** (2 min)
   - Enter filename: "test"
   - Click "Capture Image"
   - Verify: Label shows save path in green
   - Check file exists: `data/images/test_*.png`

6. **Video Recording** (5 min)
   - Enter filename: "test_video"
   - Click "Start Recording"
   - Record for 10 seconds
   - Click "Stop Recording"
   - Check file exists: `data/videos/test_video_*.mp4`
   - Open video file and verify playback

7. **Long Duration** (10 min)
   - Leave streaming for 10 minutes
   - Monitor FPS (should stay 39-40)
   - Check memory usage (Task Manager)
   - Verify no crashes or slowdowns

---

## Step 4: Document Results

1. Open `CAMERA_HAL_TEST_GUIDE.md`
2. Check off completed tests
3. Fill in performance benchmarks
4. Note any issues or anomalies
5. Save results for records

---

## Common Issues & Solutions

### Issue: "No cameras detected"
**Solution:**
- Check USB connection (try different port)
- Verify Vimba SDK installed
- Run: `cd examples && python 01_list_cameras.py`

### Issue: Low FPS (<30)
**Solution:**
- Close other USB devices
- Check CPU usage (should be <30%)
- Try: `python examples/05_continuous_stream.py`

### Issue: "Camera already in use"
**Solution:**
- Close all camera applications
- Restart application
- Unplug/replug camera

### Issue: Image/video save fails
**Solution:**
- Check disk space
- Verify output directory writable
- Review logs: `data/logs/tosca.log`

---

## Test Files Reference

| File | Purpose | Time Required |
|------|---------|---------------|
| `test_hal_integration.py` | Automated validation | 2 min |
| `CAMERA_HAL_TEST_GUIDE.md` | Comprehensive test procedures | 30-60 min |
| `examples/01_list_cameras.py` | Basic camera detection | 10 sec |
| `examples/05_continuous_stream.py` | Basic streaming test | 30 sec |
| `examples/test_camera_performance.py` | Performance metrics | 10 sec |

---

## Success Criteria

**Camera HAL is ready for production if:**

✅ All automated tests pass (test_hal_integration.py)
✅ GUI streaming maintains 35+ FPS
✅ Image capture works reliably
✅ Video recording works reliably
✅ No crashes during 10-minute streaming
✅ All controls (exposure, gain, white balance) functional

---

## Next Steps After Testing

**If all tests pass:**
- Update PROJECT_STATUS.md: Camera HAL Phase 1 VALIDATED
- Proceed to Phase 2 (Ring Detection) or other modules

**If issues found:**
- Document in LESSONS_LEARNED.md
- Create GitHub issues for bugs
- Fix critical issues before proceeding

---

**Questions or issues during testing?**
- Check `CAMERA_HAL_TEST_GUIDE.md` for detailed procedures
- Review `components/camera_module/README.md` for API details
- Check `components/camera_module/LESSONS_LEARNED.md` for known quirks
- Review logs in `data/logs/tosca.log`

---

**Good luck with testing!**
