/*
 * TOSCA Safety Watchdog Timer Firmware v2.0
 * Arduino Uno Safety Controller with Hardware Watchdog
 *
 * NEW FEATURES:
 * - PWM motor speed control (1.5V - 3.0V variable)
 * - I2C accelerometer support (vibration monitoring)
 * - Footpedal safety interlock
 * - Enhanced data logging capabilities
 *
 * Pin Configuration:
 * - D4:  Aiming laser control (output)
 * - D5:  Footpedal switch (input with pullup) - FUTURE
 * - D9:  Smoothing motor PWM control (output, 1.5-3V)
 * - A0:  Photodiode power monitoring (analog input)
 * - A4:  I2C SDA (accelerometer data)
 * - A5:  I2C SCL (accelerometer clock)
 *
 * Serial Protocol (9600 baud):
 * Watchdog:
 * - WDT_RESET              : Reset watchdog timer (heartbeat)
 * - WDT_ENABLE             : Enable watchdog
 * - WDT_DISABLE            : Disable watchdog (TESTING ONLY)
 *
 * Motor Control (PWM):
 * - MOTOR_SPEED:<0-153>    : Set motor speed (0=off, 76=1.5V, 153=3.0V max)
 * - MOTOR_OFF              : Stop motor (PWM=0)
 * - GET_MOTOR_SPEED        : Read current motor PWM value
 *
 * Laser Control:
 * - LASER_ON               : Enable aiming laser (D4 HIGH)
 * - LASER_OFF              : Disable aiming laser (D4 LOW)
 *
 * Sensor Reads:
 * - GET_ACCEL              : Read X,Y,Z acceleration (I2C)
 * - GET_VIBRATION_LEVEL    : Read vibration magnitude
 * - GET_PHOTODIODE         : Read photodiode voltage (A0)
 * - GET_FOOTPEDAL          : Read footpedal state (D5) - FUTURE
 * - GET_STATUS             : Get all sensor states
 *
 * Accelerometer:
 * - ACCEL_INIT             : Initialize accelerometer
 * - ACCEL_CALIBRATE        : Calibrate zero-point
 * - ACCEL_SET_THRESHOLD:<n>: Set vibration threshold
 *
 * Author: TOSCA Development Team
 * Version: 2.0
 * Date: 2025-10-27
 */

#include <avr/wdt.h>
#include <avr/interrupt.h>
#include <Wire.h>

// ===================================================================
// PIN DEFINITIONS
// ===================================================================
#define MOTOR_PWM_PIN 9           // PWM output for motor speed control
#define FOOTPEDAL_PIN 5           // Footpedal safety switch (future)
#define AIMING_LASER_PIN 4        // Aiming laser control
#define PHOTODIODE_PIN A0         // Photodiode analog input
// A4 = SDA (I2C Data) - hardware defined
// A5 = SCL (I2C Clock) - hardware defined

// ===================================================================
// MOTOR PWM CONFIGURATION
// ===================================================================
#define MOTOR_PWM_MIN 0           // 0V (stopped)
#define MOTOR_PWM_MAX 153         // 3.0V (DO NOT EXCEED - motor rating!)
                                  // 76 = 1.5V, 102 = 2.0V, 127 = 2.5V, 153 = 3.0V

// ===================================================================
// I2C ACCELEROMETER CONFIGURATION
// ===================================================================
// Common accelerometer I2C addresses (auto-detect at startup)
#define ACCEL_ADDR_ADXL345 0x53   // ADXL345 default address
#define ACCEL_ADDR_MPU6050 0x68   // MPU6050 default address
#define ACCEL_ADDR_LIS3DH  0x18   // LIS3DH default address

// Detected accelerometer type
uint8_t accel_address = 0;
bool accel_detected = false;

// Calibration offsets
float accel_offset_x = 0.0;
float accel_offset_y = 0.0;
float accel_offset_z = 0.0;

// Vibration threshold (adjustable)
float vibration_threshold = 0.1;  // Default: 0.1g

// ===================================================================
// WATCHDOG CONFIGURATION
// ===================================================================
#define WATCHDOG_TIMEOUT_MS 1000

// ===================================================================
// STATE TRACKING
// ===================================================================
uint8_t motor_pwm_value = 0;      // Current motor PWM (0-153)
bool aiming_laser_enabled = false;
bool watchdog_enabled = false;
unsigned long last_heartbeat = 0;

// ===================================================================
// SETUP
// ===================================================================
void setup() {
  // Disable interrupts during setup
  cli();

  // Configure GPIO pins
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(FOOTPEDAL_PIN, INPUT_PULLUP);  // Future: footpedal
  pinMode(AIMING_LASER_PIN, OUTPUT);
  pinMode(PHOTODIODE_PIN, INPUT);

  // Start with all outputs OFF (fail-safe)
  analogWrite(MOTOR_PWM_PIN, 0);
  digitalWrite(AIMING_LASER_PIN, LOW);
  motor_pwm_value = 0;
  aiming_laser_enabled = false;

  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("TOSCA Safety Watchdog v2.0");
  Serial.println("Initializing...");

  // Initialize I2C bus with timeout protection
  Serial.println("I2C bus initializing...");
  Wire.begin();
  Wire.setWireTimeout(3000, true);  // 3 second timeout, reset on timeout
  Serial.println("I2C bus initialized (with timeout protection)");

  // Auto-detect accelerometer (non-blocking)
  Serial.println("Scanning for I2C accelerometer...");
  detectAccelerometer();
  if (accel_detected) {
    Serial.println("Accelerometer found! Initializing...");
    initAccelerometer();
  } else {
    Serial.println("No accelerometer detected (continuing without it)");
  }

  // Enable watchdog timer (1000ms timeout)
  wdt_enable(WDTO_1S);
  watchdog_enabled = true;
  last_heartbeat = millis();

  Serial.println("Watchdog enabled (1000ms timeout)");
  Serial.println("Ready. Send WDT_RESET every 500ms");
  Serial.println("-----------------------------------");

  // Enable interrupts
  sei();
}

// ===================================================================
// MAIN LOOP
// ===================================================================
void loop() {
  // Process serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  delay(10);  // Small delay to prevent buffer overflow
}

// ===================================================================
// I2C ACCELEROMETER FUNCTIONS
// ===================================================================

/**
 * Auto-detect I2C accelerometer by scanning common addresses
 */
void detectAccelerometer() {
  Serial.println("Scanning for I2C accelerometer...");

  // Try common addresses
  uint8_t addresses[] = {ACCEL_ADDR_ADXL345, ACCEL_ADDR_MPU6050, ACCEL_ADDR_LIS3DH};

  for (int i = 0; i < 3; i++) {
    wdt_reset();  // Keep watchdog alive during I2C scan
    Wire.beginTransmission(addresses[i]);
    if (Wire.endTransmission() == 0) {
      accel_address = addresses[i];
      accel_detected = true;
      Serial.print("Accelerometer detected at 0x");
      Serial.println(accel_address, HEX);
      return;
    }
  }

  Serial.println("WARNING: No accelerometer detected");
  accel_detected = false;
}

/**
 * Initialize accelerometer based on detected type
 */
void initAccelerometer() {
  if (!accel_detected) {
    Serial.println("ERROR: Cannot init - no accelerometer detected");
    return;
  }

  wdt_reset();  // Keep watchdog alive during I2C init

  // ADXL345 initialization
  if (accel_address == ACCEL_ADDR_ADXL345) {
    // Set to measurement mode
    Wire.beginTransmission(accel_address);
    Wire.write(0x2D);  // POWER_CTL register
    Wire.write(0x08);  // Measurement mode
    Wire.endTransmission();
    Serial.println("ADXL345 initialized (measurement mode)");
  }

  // MPU6050 initialization
  else if (accel_address == ACCEL_ADDR_MPU6050) {
    // Wake up from sleep mode
    Wire.beginTransmission(accel_address);
    Wire.write(0x6B);  // PWR_MGMT_1 register
    Wire.write(0x00);  // Wake up
    Wire.endTransmission();
    Serial.println("MPU6050 initialized (wake from sleep)");
  }

  // LIS3DH initialization
  else if (accel_address == ACCEL_ADDR_LIS3DH) {
    // Enable all axes, 100Hz
    Wire.beginTransmission(accel_address);
    Wire.write(0x20);  // CTRL_REG1
    Wire.write(0x57);  // 100Hz, all axes enabled
    Wire.endTransmission();
    Serial.println("LIS3DH initialized (100Hz, all axes)");
  }

  wdt_reset();  // Reset after init complete
}

/**
 * Read raw acceleration data from I2C accelerometer
 * Returns: X, Y, Z in g's (approximately)
 */
void readAcceleration(float &x, float &y, float &z) {
  if (!accel_detected) {
    x = y = z = 0.0;
    return;
  }

  wdt_reset();  // Keep watchdog alive during I2C read

  int16_t raw_x = 0, raw_y = 0, raw_z = 0;

  // ADXL345 read (registers 0x32-0x37)
  if (accel_address == ACCEL_ADDR_ADXL345) {
    Wire.beginTransmission(accel_address);
    Wire.write(0x32);  // Start at DATAX0
    Wire.endTransmission();
    Wire.requestFrom(accel_address, (uint8_t)6);

    if (Wire.available() >= 6) {
      raw_x = Wire.read() | (Wire.read() << 8);
      raw_y = Wire.read() | (Wire.read() << 8);
      raw_z = Wire.read() | (Wire.read() << 8);
    }

    // ADXL345: 256 LSB/g at ±2g range
    x = raw_x / 256.0 - accel_offset_x;
    y = raw_y / 256.0 - accel_offset_y;
    z = raw_z / 256.0 - accel_offset_z;
  }

  // MPU6050 read (registers 0x3B-0x40)
  else if (accel_address == ACCEL_ADDR_MPU6050) {
    Wire.beginTransmission(accel_address);
    Wire.write(0x3B);  // Start at ACCEL_XOUT_H
    Wire.endTransmission();
    Wire.requestFrom(accel_address, (uint8_t)6);

    if (Wire.available() >= 6) {
      raw_x = (Wire.read() << 8) | Wire.read();
      raw_y = (Wire.read() << 8) | Wire.read();
      raw_z = (Wire.read() << 8) | Wire.read();
    }

    // MPU6050: 16384 LSB/g at ±2g range
    x = raw_x / 16384.0 - accel_offset_x;
    y = raw_y / 16384.0 - accel_offset_y;
    z = raw_z / 16384.0 - accel_offset_z;
  }

  // LIS3DH read (registers 0x28-0x2D)
  else if (accel_address == ACCEL_ADDR_LIS3DH) {
    Wire.beginTransmission(accel_address);
    Wire.write(0x28 | 0x80);  // Auto-increment
    Wire.endTransmission();
    Wire.requestFrom(accel_address, (uint8_t)6);

    if (Wire.available() >= 6) {
      raw_x = Wire.read() | (Wire.read() << 8);
      raw_y = Wire.read() | (Wire.read() << 8);
      raw_z = Wire.read() | (Wire.read() << 8);
    }

    // LIS3DH: Depends on scale (assume ±2g, ~16000 LSB/g)
    x = (raw_x >> 4) / 1000.0 - accel_offset_x;
    y = (raw_y >> 4) / 1000.0 - accel_offset_y;
    z = (raw_z >> 4) / 1000.0 - accel_offset_z;
  }
}

/**
 * Calculate vibration magnitude from acceleration
 */
float calculateVibrationMagnitude() {
  float x, y, z;
  readAcceleration(x, y, z);

  // Remove gravity component (assume Z-axis aligned with gravity)
  float vibration = sqrt(x*x + y*y + (z-1.0)*(z-1.0));
  return vibration;
}

/**
 * Calibrate accelerometer (zero-point)
 */
void calibrateAccelerometer() {
  if (!accel_detected) {
    Serial.println("ERROR:NO_ACCELEROMETER");
    return;
  }

  Serial.println("Calibrating... Keep device still!");
  delay(500);
  wdt_reset();  // Reset before long calibration

  float sum_x = 0, sum_y = 0, sum_z = 0;
  const int samples = 50;

  for (int i = 0; i < samples; i++) {
    wdt_reset();  // Keep alive during calibration loop

    float x, y, z;

    // Temporarily disable offsets for calibration
    float temp_x = accel_offset_x;
    float temp_y = accel_offset_y;
    float temp_z = accel_offset_z;
    accel_offset_x = accel_offset_y = accel_offset_z = 0.0;

    readAcceleration(x, y, z);

    // Restore offsets
    accel_offset_x = temp_x;
    accel_offset_y = temp_y;
    accel_offset_z = temp_z;

    sum_x += x;
    sum_y += y;
    sum_z += z;
    delay(20);
  }

  accel_offset_x = sum_x / samples;
  accel_offset_y = sum_y / samples;
  accel_offset_z = (sum_z / samples) - 1.0;  // Z should read +1g

  Serial.print("Calibration complete: X=");
  Serial.print(accel_offset_x, 3);
  Serial.print(" Y=");
  Serial.print(accel_offset_y, 3);
  Serial.print(" Z=");
  Serial.println(accel_offset_z, 3);
  Serial.println("OK:CALIBRATED");
}

// ===================================================================
// COMMAND PROCESSING
// ===================================================================
void processCommand(String cmd) {
  // -------------------------
  // WATCHDOG COMMANDS
  // -------------------------
  if (cmd == "WDT_RESET") {
    wdt_reset();
    last_heartbeat = millis();
    Serial.println("OK:WDT_RESET");
  }
  else if (cmd == "WDT_ENABLE") {
    wdt_enable(WDTO_1S);
    watchdog_enabled = true;
    last_heartbeat = millis();
    Serial.println("OK:WDT_ENABLED");
  }
  else if (cmd == "WDT_DISABLE") {
    wdt_disable();
    watchdog_enabled = false;
    Serial.println("WARNING:WDT_DISABLED");
  }

  // -------------------------
  // MOTOR PWM COMMANDS
  // -------------------------
  else if (cmd.startsWith("MOTOR_SPEED:")) {
    int pwm_value = cmd.substring(12).toInt();

    // Safety limit: max 153 (3.0V)
    if (pwm_value < 0) pwm_value = 0;
    if (pwm_value > MOTOR_PWM_MAX) {
      pwm_value = MOTOR_PWM_MAX;
      Serial.println("WARNING:PWM_CLAMPED_TO_MAX");
    }

    analogWrite(MOTOR_PWM_PIN, pwm_value);
    motor_pwm_value = pwm_value;

    Serial.print("OK:MOTOR_SPEED:");
    Serial.println(pwm_value);
  }
  else if (cmd == "MOTOR_OFF") {
    analogWrite(MOTOR_PWM_PIN, 0);
    motor_pwm_value = 0;
    Serial.println("OK:MOTOR_OFF");
  }
  else if (cmd == "GET_MOTOR_SPEED") {
    Serial.print("MOTOR_SPEED:");
    Serial.println(motor_pwm_value);
  }

  // -------------------------
  // LASER COMMANDS
  // -------------------------
  else if (cmd == "LASER_ON") {
    digitalWrite(AIMING_LASER_PIN, HIGH);
    aiming_laser_enabled = true;
    Serial.println("OK:LASER_ON");
  }
  else if (cmd == "LASER_OFF") {
    digitalWrite(AIMING_LASER_PIN, LOW);
    aiming_laser_enabled = false;
    Serial.println("OK:LASER_OFF");
  }

  // -------------------------
  // ACCELEROMETER COMMANDS
  // -------------------------
  else if (cmd == "ACCEL_INIT") {
    wdt_reset();  // Reset before I2C operations
    detectAccelerometer();
    if (accel_detected) {
      initAccelerometer();
      Serial.println("OK:ACCEL_INITIALIZED");
    } else {
      Serial.println("ERROR:NO_ACCEL_FOUND");
    }
    wdt_reset();  // Reset after complete
  }
  else if (cmd == "ACCEL_CALIBRATE") {
    wdt_reset();  // Reset before calibration
    calibrateAccelerometer();
    wdt_reset();  // Reset after calibration
  }
  else if (cmd.startsWith("ACCEL_SET_THRESHOLD:")) {
    float threshold = cmd.substring(20).toFloat();
    if (threshold >= 0.0 && threshold <= 10.0) {
      vibration_threshold = threshold;
      Serial.print("OK:THRESHOLD_SET:");
      Serial.println(threshold, 3);
    } else {
      Serial.println("ERROR:THRESHOLD_OUT_OF_RANGE");
    }
  }
  else if (cmd == "GET_ACCEL") {
    if (!accel_detected) {
      Serial.println("ERROR:NO_ACCELEROMETER");
      return;
    }

    wdt_reset();  // Reset before I2C read
    float x, y, z;
    readAcceleration(x, y, z);

    Serial.print("ACCEL:");
    Serial.print(x, 3);
    Serial.print(",");
    Serial.print(y, 3);
    Serial.print(",");
    Serial.println(z, 3);
  }
  else if (cmd == "GET_VIBRATION_LEVEL") {
    if (!accel_detected) {
      Serial.println("ERROR:NO_ACCELEROMETER");
      return;
    }

    wdt_reset();  // Reset before I2C read
    float magnitude = calculateVibrationMagnitude();
    Serial.print("VIBRATION:");
    Serial.println(magnitude, 3);
  }

  // -------------------------
  // SENSOR READS
  // -------------------------
  else if (cmd == "GET_PHOTODIODE") {
    int raw = analogRead(PHOTODIODE_PIN);
    float voltage = (raw / 1023.0) * 5.0;
    Serial.print("PHOTODIODE:");
    Serial.println(voltage, 3);
  }
  else if (cmd == "GET_FOOTPEDAL") {
    bool pressed = !digitalRead(FOOTPEDAL_PIN);  // Active LOW
    Serial.print("FOOTPEDAL:");
    Serial.println(pressed ? "1" : "0");
  }

  // -------------------------
  // STATUS QUERY
  // -------------------------
  else if (cmd == "GET_STATUS") {
    Serial.println("STATUS:");

    // Motor
    Serial.print("  Motor PWM: ");
    Serial.print(motor_pwm_value);
    Serial.print(" (");
    float motor_voltage = (motor_pwm_value / 255.0) * 5.0;
    Serial.print(motor_voltage, 2);
    Serial.println("V)");

    // Aiming laser
    Serial.print("  Aiming Laser: ");
    Serial.println(aiming_laser_enabled ? "ON" : "OFF");

    // Accelerometer
    Serial.print("  Accelerometer: ");
    if (accel_detected) {
      Serial.print("0x");
      Serial.print(accel_address, HEX);

      float x, y, z;
      readAcceleration(x, y, z);
      Serial.print(" X=");
      Serial.print(x, 2);
      Serial.print("g Y=");
      Serial.print(y, 2);
      Serial.print("g Z=");
      Serial.print(z, 2);
      Serial.println("g");

      float vib = calculateVibrationMagnitude();
      Serial.print("  Vibration: ");
      Serial.print(vib, 3);
      Serial.print("g (threshold: ");
      Serial.print(vibration_threshold, 3);
      Serial.println("g)");
    } else {
      Serial.println("NOT_DETECTED");
    }

    // Photodiode
    Serial.print("  Photodiode: ");
    int raw = analogRead(PHOTODIODE_PIN);
    float voltage = (raw / 1023.0) * 5.0;
    Serial.print(voltage, 3);
    Serial.println("V");

    // Footpedal
    Serial.print("  Footpedal: ");
    Serial.println(!digitalRead(FOOTPEDAL_PIN) ? "PRESSED" : "RELEASED");

    // Watchdog
    Serial.print("  Watchdog: ");
    Serial.println(watchdog_enabled ? "ENABLED" : "DISABLED");
    unsigned long since_heartbeat = millis() - last_heartbeat;
    Serial.print("  Last Heartbeat: ");
    Serial.print(since_heartbeat);
    Serial.println("ms ago");

    Serial.println("OK:STATUS");
  }

  // -------------------------
  // UNKNOWN COMMAND
  // -------------------------
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
  }
}

// ===================================================================
// WATCHDOG TIMEOUT ISR
// ===================================================================
ISR(WDT_vect) {
  // Disable interrupts
  cli();

  // Emergency shutdown: Set all outputs to safe state
  analogWrite(MOTOR_PWM_PIN, 0);           // Motor OFF
  digitalWrite(AIMING_LASER_PIN, LOW);     // Aiming laser OFF

  // Halt system (infinite loop - requires power cycle)
  while(1) {
    // System halted - power cycle required
  }
}
