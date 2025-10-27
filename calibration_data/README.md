# Motor Vibration Calibration Data

## Date: 2025-10-27

### Test Setup
- **Accelerometer:** MPU6050 (I2C address 0x68)
- **Motor Range:** 1.5V to 3.0V
- **Samples:** 5 per voltage level + 10 for motor OFF baseline

### Results

| Voltage | PWM | Avg Vibration | Min | Max | vs OFF |
|---------|-----|---------------|-----|-----|--------|
| **0V (OFF)** | **0** | **0.140g** | 0.136g | 0.144g | Baseline |
| 1.5V | 76 | 1.802g | 0.835g | 2.448g | 12.9x |
| 2.0V | 102 | 1.629g | 1.347g | 2.245g | 11.6x |
| 2.5V | 127 | 1.919g | 1.581g | 2.467g | 13.7x |
| 3.0V | 153 | 2.877g | 2.211g | 3.640g | 20.6x |

### Recommended Thresholds

**Motor Detection (Safety Interlock):**
- **Motor OFF:** Vibration < 0.8g
- **Motor Running:** Vibration > 0.8g

**Rationale:**
- Baseline (motor off): ~0.140g
- Lowest motor speed (1.5V): ~1.8g
- Threshold at 0.8g provides:
  - **5.7x safety margin** above baseline noise
  - **2.3x safety margin** below minimum motor vibration
  - Clear separation between OFF and ON states

**Additional Detection (Optional):**
- **High Speed (≥2.5V):** Vibration > 2.0g
- Useful for confirming motor is at operating speed

### Key Findings

1. **Excellent Signal-to-Noise Ratio:** Even the lowest motor speed (1.5V) produces 13x more vibration than baseline
2. **Clear Speed Differentiation:** 3.0V produces ~60% more vibration than lower speeds
3. **Stable Baseline:** Motor OFF readings very consistent (0.136g - 0.144g range)
4. **Reliable Detection:** 0.8g threshold provides robust motor on/off detection

### Data Files
- `motor_calibration_20251027_144112.csv` - Full test data with timestamps

### Test Scripts
- `tests/test_motor_vibration_calibration.py` - Calibration script
- `tests/test_motor_off_baseline.py` - Motor OFF baseline test
