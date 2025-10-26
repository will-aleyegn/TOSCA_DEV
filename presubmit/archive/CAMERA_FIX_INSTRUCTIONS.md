# Camera Display Bug Fix Instructions

## Problem
The camera widget is showing only the top half of the image with glitching due to incorrect stride/bytes_per_line calculation in the QImage conversion.

## File to Edit
`C:/Users/wille/Desktop/TOSCA-dev/src/ui/widgets/camera_widget.py`

## Lines to Replace
Lines 583-596

## Steps to Apply Fix

### 1. Close TOSCA Application
If TOSCA is currently running, close it completely. The file cannot be edited while the application is running.

### 2. Open the File
Open `src/ui/widgets/camera_widget.py` in your text editor

### 3. Find the Code to Replace
Navigate to lines 583-596 and locate this code:

```python
            # Convert to QImage
            if len(frame.shape) == 2:
                # Grayscale
                bytes_per_line = width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
                )
            else:
                # RGB
                channels = frame.shape[2]
                bytes_per_line = channels * width
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )
```

### 4. Replace with Fixed Code
Replace the above code with:

```python
            # Convert to QImage
            # Ensure frame is C-contiguous for QImage
            frame = np.ascontiguousarray(frame)

            if len(frame.shape) == 2:
                # Grayscale
                bytes_per_line = frame.strides[0]
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8
                )
            else:
                # RGB - use actual stride from numpy array
                bytes_per_line = frame.strides[0]
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )
```

### 5. Save the File
Save the changes to `camera_widget.py`

### 6. Restart TOSCA
Launch the TOSCA application and test the camera display.

## What the Fix Does

### Root Cause
The original code calculated `bytes_per_line` manually as `width` (grayscale) or `channels * width` (RGB). However, numpy arrays may have padding between rows (stride), and QImage needs the actual memory stride to correctly interpret the image data.

### The Solution
1. **`np.ascontiguousarray(frame)`**: Ensures the frame data is C-contiguous in memory, removing any unexpected padding or non-standard memory layout
2. **`frame.strides[0]`**: Uses the actual row stride from the numpy array instead of calculating it manually. `strides[0]` gives the number of bytes to step to the next row in memory.

This ensures QImage correctly interprets the memory layout of the frame data, preventing the "half image" display bug.

## Expected Result
After applying this fix:
- Camera display will show the full image correctly
- No glitching or artifacts
- Both grayscale and RGB images will display properly
