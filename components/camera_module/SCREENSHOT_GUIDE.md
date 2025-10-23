# Camera Module Screenshot Guide

**Purpose:** Guide for capturing screenshots for documentation

**Target:** Update README.md with visual examples of camera features

**Last Updated:** 2025-10-23

---

## Prerequisites

- Allied Vision camera connected and working
- Application running: `python src/main.py`
- Camera successfully connected and streaming

---

## Screenshot Requirements

### Tool Recommendations

**Windows:**
- **Snipping Tool** (Built-in, press Win+Shift+S)
- **Greenshot** (Free, https://getgreenshot.org/)
- **ShareX** (Free, advanced features)

**Recommended Settings:**
- Format: PNG (lossless)
- Include window borders (for context)
- Crop tightly around relevant area
- Resolution: Full resolution (no downscaling)

---

## Screenshot Checklist

### 1. Main Window Overview
**Filename:** `01_main_window_overview.png`

**What to capture:**
- Full TOSCA main window
- Camera/Alignment tab selected and visible
- Camera connected and streaming
- Live feed showing clear image
- FPS indicator visible (showing 39-40 FPS)

**Setup:**
1. Launch application
2. Go to Camera/Alignment tab
3. Connect camera
4. Start streaming
5. Wait for stable FPS display
6. Capture full window

**Key elements to show:**
- Application title bar
- Tab navigation (with Camera/Alignment selected)
- Live camera feed
- Control panel on right
- Status indicators

---

### 2. Camera Connection Success
**Filename:** `02_connection_success.png`

**What to capture:**
- Close-up of connection controls
- "Status: Connected" in green
- "Disconnect" button (showing connected state)
- "Start Streaming" button enabled

**Setup:**
1. Camera connected (but not streaming yet)
2. Capture just the connection controls section
3. Show green status indicator

**Key elements:**
- Connection status in green
- Button states showing connection

---

### 3. Live Streaming
**Filename:** `03_live_streaming.png`

**What to capture:**
- Full camera display area
- Clear live video feed
- FPS counter showing 39-40 FPS
- Status bar at bottom showing "Connected"
- Recording indicator area (not recording)

**Setup:**
1. Camera streaming
2. Point camera at interesting scene (desk, workspace)
3. Ensure good lighting
4. Wait for FPS to stabilize
5. Capture full display area

**Key elements:**
- Live video feed
- FPS indicator
- Status indicators

---

### 4. Exposure Control - Manual
**Filename:** `04_exposure_manual.png`

**What to capture:**
- Exposure control section
- "Auto" checkbox UNCHECKED
- Exposure slider at specific position
- Exposure value displayed (e.g., "10000 us")
- Input box showing same value

**Setup:**
1. Ensure "Auto" exposure is unchecked
2. Set exposure to 10000 µs using slider
3. Capture just the Camera Settings section
4. Show clear slider position

**Key elements:**
- Exposure slider
- Value label
- Input box
- Auto checkbox state

---

### 5. Exposure Control - Auto
**Filename:** `05_exposure_auto.png`

**What to capture:**
- Exposure control section
- "Auto" checkbox CHECKED
- Slider and input box DISABLED (grayed out)
- Exposure adjusting automatically

**Setup:**
1. Check "Auto" exposure box
2. Point camera at bright area
3. Wait 2 seconds for adjustment
4. Capture exposure controls
5. Show disabled state of manual controls

**Key elements:**
- Auto checkbox checked
- Disabled slider/input
- Visual indication of auto mode

---

### 6. Gain Control
**Filename:** `06_gain_control.png`

**What to capture:**
- Gain control section
- Gain slider at specific position
- Gain value displayed (e.g., "12.0 dB")
- Input box visible

**Setup:**
1. Ensure "Auto" gain is unchecked
2. Set gain to 12.0 dB
3. Capture gain controls section
4. Show clear controls

**Key elements:**
- Gain slider
- Value display
- Input box

---

### 7. White Balance Control
**Filename:** `07_white_balance.png`

**What to capture:**
- White balance section
- "Auto" checkbox checked
- Camera feed showing good color balance

**Setup:**
1. Check "Auto" white balance
2. Point camera at scene with white objects
3. Wait for WB to adjust
4. Capture control and feed
5. Show color-corrected image

**Key elements:**
- Auto WB checkbox
- Color-corrected video feed

---

### 8. Image Capture Controls
**Filename:** `08_image_capture_controls.png`

**What to capture:**
- Still Image Capture section
- Filename input box with "test_capture"
- "Capture Image" button
- Last capture label showing saved file path in green

**Setup:**
1. Enter filename "test_capture"
2. Click "Capture Image"
3. Wait for green success message
4. Capture the controls section
5. Show success feedback

**Key elements:**
- Filename input
- Capture button
- Success message with path

---

### 9. Image Capture - Dev Mode
**Filename:** `09_image_capture_dev_mode.png`

**What to capture:**
- Image capture section in dev mode
- Custom path controls visible
- Browse button visible
- Path input showing custom directory

**Setup:**
1. Enable developer mode
2. Click "Browse..." for image path
3. Select custom directory
4. Capture section showing custom path controls
5. Show dev mode features

**Key elements:**
- Custom path input field
- Browse button
- Selected custom path displayed

---

### 10. Video Recording - Not Recording
**Filename:** `10_video_recording_idle.png`

**What to capture:**
- Video Recording section
- "Start Recording" button
- Status showing "Not recording"
- Filename input with "test_video"

**Setup:**
1. Not recording state
2. Filename entered
3. Capture recording controls
4. Show idle state

**Key elements:**
- Start button
- Idle status
- Filename input

---

### 11. Video Recording - Active
**Filename:** `11_video_recording_active.png`

**What to capture:**
- Video Recording section
- "Stop Recording" button (changed state)
- Status showing "Recording..." in red
- Recording indicator "● REC" in red on main display

**Setup:**
1. Start recording
2. Capture controls immediately
3. Show recording state
4. Show red indicators

**Key elements:**
- Stop button
- Red recording status
- REC indicator

---

### 12. Combined View - All Features
**Filename:** `12_all_features.png`

**What to capture:**
- Full interface with all features active
- Streaming active (30+ FPS)
- Auto exposure enabled
- Auto gain enabled
- Recording active
- All status indicators visible

**Setup:**
1. Connect camera
2. Start streaming
3. Enable auto exposure
4. Enable auto gain
5. Start recording
6. Capture full interface
7. Show everything working together

**Key elements:**
- Live feed
- All auto modes on
- Recording active
- All controls visible
- Performance indicators

---

### 13. Error State - Camera Not Connected
**Filename:** `13_error_not_connected.png`

**What to capture:**
- "Status: Not Connected" in red
- "Connect Camera" button
- Disabled controls
- No video feed (placeholder text)

**Setup:**
1. Camera not connected OR disconnect camera
2. Show error state
3. Capture full tab
4. Show disabled controls

**Key elements:**
- Red error status
- Disabled buttons
- Placeholder text

---

### 14. Performance - High FPS
**Filename:** `14_performance_high_fps.png`

**What to capture:**
- Close-up of status bar
- FPS indicator showing 39-40 FPS
- Connection status
- Recording indicator (if recording)

**Setup:**
1. Streaming at optimal performance
2. Wait for FPS to stabilize at 39-40
3. Capture status bar
4. Show peak performance

**Key elements:**
- FPS counter showing 39-40
- Smooth streaming indicator
- Status displays

---

### 15. Captured Image Result
**Filename:** `15_captured_image_example.png`

**What to capture:**
- An actual captured image file opened in image viewer
- Show good quality
- Show resolution (1456x1088)
- Show clear, focused image

**Setup:**
1. Capture image using the app
2. Navigate to data/images/ folder
3. Open most recent .png file
4. Take screenshot of opened image
5. Include filename in view

**Key elements:**
- Captured image quality
- File properties visible
- Clear resolution

---

### 16. Recorded Video Result
**Filename:** `16_recorded_video_example.png`

**What to capture:**
- Video file opened in video player
- Show playback
- Show duration (e.g., 10 seconds)
- Show good quality

**Setup:**
1. Record 10-second video
2. Navigate to data/videos/ folder
3. Open .mp4 file in VLC or similar
4. Take screenshot during playback
5. Show video info panel if possible

**Key elements:**
- Video playing
- Duration visible
- Quality demonstration

---

## After Capturing Screenshots

### 1. Organize Files

Create screenshots directory:
```bash
mkdir components/camera_module/screenshots
```

Move all screenshots there:
```
components/camera_module/screenshots/
├── 01_main_window_overview.png
├── 02_connection_success.png
├── 03_live_streaming.png
├── 04_exposure_manual.png
├── 05_exposure_auto.png
├── 06_gain_control.png
├── 07_white_balance.png
├── 08_image_capture_controls.png
├── 09_image_capture_dev_mode.png
├── 10_video_recording_idle.png
├── 11_video_recording_active.png
├── 12_all_features.png
├── 13_error_not_connected.png
├── 14_performance_high_fps.png
├── 15_captured_image_example.png
└── 16_recorded_video_example.png
```

### 2. Optimize Screenshots

Optional - reduce file sizes while maintaining quality:
```bash
# Using ImageMagick (if installed)
cd components/camera_module/screenshots
for img in *.png; do
    convert "$img" -quality 85 -resize '1200x800>' "optimized_$img"
done
```

### 3. Update README

Run the README update script or manually add screenshot references to README.md

---

## Screenshot Specifications

### Quality Requirements

- **Format:** PNG
- **Minimum Width:** 800px
- **Maximum Width:** 1920px (full HD)
- **Aspect Ratio:** Maintain original (no distortion)
- **Compression:** PNG-8 or PNG-24 with optimization
- **File Size:** Aim for <500KB per screenshot

### Consistency Requirements

- **Lighting:** Consistent across all screenshots
- **Scene:** Use same test scene where possible
- **Window Size:** Keep application window size consistent
- **Zoom Level:** No browser zoom (100%)
- **OS Theme:** Consistent (don't switch themes)

### Privacy Requirements

- **No Personal Info:** Remove any personal data from scenes
- **No Sensitive Content:** Avoid capturing anything confidential
- **Generic Test Data:** Use generic filenames and paths
- **Clean Desktop:** Hide taskbar/dock if capturing full screen

---

## Troubleshooting Screenshot Issues

### Camera Not Showing Good Image
**Problem:** Camera feed is dark or blurry
**Solution:**
- Adjust exposure manually first
- Ensure good lighting
- Focus camera properly
- Clean camera lens

### FPS Too Low
**Problem:** FPS showing <30
**Solution:**
- Close other applications
- Use USB 3.0 port
- Wait longer for FPS to stabilize
- Check CPU usage

### Can't Capture Recording State
**Problem:** Recording stops before getting screenshot
**Solution:**
- Record longer duration (30+ seconds)
- Use screenshot tool with delay timer
- Have second person help
- Use video screen capture then extract frame

### Window Too Large for Screen
**Problem:** Can't fit full window in screenshot
**Solution:**
- Reduce window size slightly
- Capture in sections and note it
- Use scrolling screenshot tool
- Prioritize most important elements

---

## Quick Capture Workflow

For fastest screenshot capture:

1. **Prepare**
   - Launch app
   - Connect camera
   - Position window nicely
   - Set up scene
   - Open screenshot tool

2. **Capture Session (15 minutes)**
   - Work through list 1-16 systematically
   - Don't worry about perfection on first pass
   - Mark off each screenshot as captured
   - Note any issues

3. **Review (5 minutes)**
   - Check all files captured correctly
   - Verify file names match guide
   - Check image quality
   - Retake any poor screenshots

4. **Organize (5 minutes)**
   - Create screenshots directory
   - Move files to correct location
   - Verify all 16 files present
   - Ready for README update

**Total Time:** ~25-30 minutes

---

## Checklist

Use this to track your progress:

- [ ] 01. Main Window Overview
- [ ] 02. Connection Success
- [ ] 03. Live Streaming
- [ ] 04. Exposure Manual
- [ ] 05. Exposure Auto
- [ ] 06. Gain Control
- [ ] 07. White Balance
- [ ] 08. Image Capture Controls
- [ ] 09. Image Capture Dev Mode
- [ ] 10. Video Recording Idle
- [ ] 11. Video Recording Active
- [ ] 12. All Features Combined
- [ ] 13. Error State
- [ ] 14. Performance High FPS
- [ ] 15. Captured Image Example
- [ ] 16. Recorded Video Example

- [ ] All files organized in screenshots/ directory
- [ ] All filenames correct
- [ ] All images reviewed for quality
- [ ] README.md updated with screenshot references

---

**Ready to capture screenshots!**

Follow the checklist above and capture each screenshot systematically.
Each screenshot helps users understand the camera module features visually.

**Questions?** Refer to troubleshooting section or create issues for unclear instructions.
