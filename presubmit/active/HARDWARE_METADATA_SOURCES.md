# Hardware Metadata Sources

**Created:** 2025-10-28
**Purpose:** Document how to retrieve device metadata from each hardware component
**Related:** Enhancement 3 - Hardware Info Cards

---

## Overview

Each hardware device provides different levels of metadata through their respective APIs. This document details what information is available and how to access it.

---

## 1. Camera (Allied Vision via VmbPy)

### Available Metadata

VmbPy provides **rich metadata** through both static properties and GenICam features:

#### **Static Properties** (accessible outside `with` context):
```python
camera.get_id()           # Camera ID (e.g., "DEV_1AB234567890")
camera.get_model()        # Model name (e.g., "Alvium 1800 U-158c")
camera.get_name()         # User-friendly name
camera.get_serial()       # Serial number
camera.get_extended_id()  # Extended globally unique ID
```

#### **GenICam Features** (accessible inside `with` context):
```python
# Device information
camera.get_feature_by_name("DeviceModelName").get()
camera.get_feature_by_name("DeviceSerialNumber").get()
camera.get_feature_by_name("DeviceFirmwareVersion").get()
camera.get_feature_by_name("DeviceManufacturerInfo").get()

# Sensor information
camera.get_feature_by_name("SensorWidth").get()
camera.get_feature_by_name("SensorHeight").get()
camera.get_feature_by_name("PixelFormat").get()

# Interface information
camera.get_feature_by_name("GevDeviceIPAddress").get()  # If GigE
camera.get_feature_by_name("DeviceTemperature").get()   # If available
```

### Implementation Example

```python
def get_device_info(self) -> dict[str, str]:
    """Get camera device information."""
    if not self.is_connected or not self.camera:
        return {}

    info = {
        "model": self.camera.get_model(),
        "serial": self.camera.get_serial(),
        "id": self.camera.get_id(),
    }

    # Get firmware version (requires camera context)
    try:
        firmware = self.camera.get_feature_by_name("DeviceFirmwareVersion").get()
        info["firmware"] = firmware
    except Exception:
        info["firmware"] = "Unknown"

    # Get sensor resolution
    try:
        width = self.camera.get_feature_by_name("SensorWidth").get()
        height = self.camera.get_feature_by_name("SensorHeight").get()
        info["resolution"] = f"{width}x{height}"
    except Exception:
        # Fallback to frame size if sensor size not available
        width, height = self.get_frame_size()
        info["resolution"] = f"{width}x{height}"

    return info
```

**Calibration Date:** Not stored in camera - must be maintained in application database or config file.

---

## 2. Linear Actuator (Zaber via Serial)

### Available Metadata

Zaber devices provide **moderate metadata** through serial commands:

#### **Device Identification Commands:**
```python
# Zaber ASCII protocol commands:
/1 get device.name         # Device name
/1 get device.serial       # Serial number
/1 get device.id           # Device ID
/1 get firmware.version    # Firmware version
/1 get hardware.version    # Hardware revision

# Travel range
/1 get limit.max           # Maximum position (microsteps)
/1 get motion.accelmax     # Max acceleration
/1 get motion.speedmax     # Max speed
```

### Implementation Example

```python
def get_device_info(self) -> dict[str, str]:
    """Get actuator device information."""
    if not self.is_connected or not self.device:
        return {}

    info = {}

    try:
        # Get device info through Zaber API
        # Note: Exact API depends on zaber-motion library version
        info["model"] = "Zaber Linear Actuator"  # May need device query
        info["serial"] = self.device.get_serial_number() if hasattr(self.device, 'get_serial_number') else "Unknown"

        # Get firmware version
        if hasattr(self.device, 'get_firmware_version'):
            info["firmware"] = self.device.get_firmware_version()

        # Get range from controller state
        info["range"] = f"0-{self.max_position_um / 1000:.1f} mm"

    except Exception as e:
        logger.warning(f"Could not retrieve actuator metadata: {e}")
        info["model"] = "Zaber Linear Actuator"
        info["serial"] = "Unknown"

    return info
```

**Note:** Zaber API methods vary by library version. Check `zaber-motion` documentation for exact method names.

**Calibration Date:** Must be stored in database or config file (not in device).

---

## 3. Laser Systems (Manufacturer-Specific)

### Available Metadata

Laser metadata **depends heavily on manufacturer**:

#### **Common Information:**
- Model number (usually via serial query or hardcoded)
- Serial number (if device supports it)
- Wavelength (often fixed, document in code)
- Max power (device spec, not queryable)

#### **Possible Serial Commands:**
```python
# Example for typical laser controller:
*IDN?              # Identity query (SCPI standard)
SERIAL?            # Serial number query
VERSION?           # Firmware version
STATUS?            # Operational status
```

### Implementation Example

```python
def get_device_info(self) -> dict[str, str]:
    """Get laser device information."""
    if not self.is_connected:
        return {}

    info = {
        "model": "Treatment Laser",  # Update with actual model
        "wavelength": "808 nm",      # Update with actual wavelength
        "max_power": "5 W",          # Update with actual spec
    }

    # Try to get serial number if supported
    try:
        # This depends on your laser's protocol
        # Example: serial_cmd = self.device.query("SERIAL?")
        info["serial"] = "Contact manufacturer for details"
    except Exception:
        info["serial"] = "Not available"

    return info
```

**Calibration Date:** Critical for laser systems - must be stored in database with timestamps.

---

## 4. GPIO (Raspberry Pi / Arduino)

### Available Metadata

GPIO devices have **very limited** metadata:

#### **Available Information:**
- OS-level device information only
- No serial numbers or firmware versions
- Device capabilities (input/output pins)

### Implementation Example

```python
def get_device_info(self) -> dict[str, str]:
    """Get GPIO device information."""
    if not self.is_connected:
        return {}

    info = {
        "model": "Raspberry Pi GPIO",
        "pins": "40-pin header",
        "voltage": "3.3V logic",
        "serial": "Host system",
    }

    # Add connected sensor information
    if self.smoothing_motor_connected:
        info["smoothing_motor"] = "Connected"
    if self.photodiode_connected:
        info["photodiode"] = "Connected"

    return info
```

**Calibration Date:** Store sensor calibration dates in database.

---

## 5. Calibration Date Storage

### Database Schema

Since most hardware doesn't store calibration dates, maintain them in the application database:

```sql
CREATE TABLE hardware_calibration (
    id INTEGER PRIMARY KEY,
    device_type TEXT NOT NULL,  -- 'camera', 'laser', 'actuator', 'gpio'
    device_serial TEXT,          -- Serial number (if available)
    calibration_date TEXT NOT NULL,  -- ISO format: '2025-10-15'
    calibrated_by TEXT,          -- Technician name
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Python Access Example

```python
def get_last_calibration_date(self, device_type: str, serial: str = None) -> str:
    """Get last calibration date from database."""
    query = """
        SELECT calibration_date
        FROM hardware_calibration
        WHERE device_type = ?
        ORDER BY calibration_date DESC
        LIMIT 1
    """

    result = db.execute(query, (device_type,)).fetchone()
    return result[0] if result else "Never calibrated"
```

---

## Summary: Metadata Availability

| Device | Model | Serial | Firmware | Calibration | Implementation Difficulty |
|--------|-------|--------|----------|-------------|--------------------------|
| **Camera** | ✅ Rich | ✅ Yes | ✅ Yes | 🗄️ Database | ⭐ Easy |
| **Actuator** | ✅ Yes | ✅ Likely | ✅ Yes | 🗄️ Database | ⭐⭐ Medium |
| **Laser** | ⚠️ Limited | ⚠️ Maybe | ⚠️ Maybe | 🗄️ Database | ⭐⭐⭐ Hard |
| **GPIO** | ⚠️ Generic | ❌ No | ❌ No | 🗄️ Database | ⭐ Easy |

**Legend:**
- ✅ Readily available from device
- ⚠️ Depends on manufacturer/model
- ❌ Not available
- 🗄️ Must be stored in application database

---

## Recommended Implementation Approach

### Phase 1: Camera Only (Quick Win)
Implement `get_device_info()` for camera first - it has the richest metadata and is easiest to implement.

### Phase 2: Actuator (Medium Effort)
Add actuator metadata once Zaber API methods are confirmed.

### Phase 3: Laser & GPIO (Lower Priority)
Implement placeholder info cards for laser and GPIO with manual entry options.

### Phase 4: Calibration Database (Future Enhancement)
Add calibration tracking system with database backend.

---

## Next Steps

1. **Implement camera `get_device_info()`** - 30 min
2. **Test with real hardware** - 15 min
3. **Create HardwareInfoCard widget** - 45 min
4. **Wire to Hardware tab** - 30 min
5. **Add database schema for calibration** - Future

**Total Estimated Effort:** 2 hours (excluding database integration)
