/*
 * TOSCA Safety Watchdog Timer Firmware
 * Arduino Nano Safety Controller with Hardware Watchdog
 *
 * Features:
 * - Hardware watchdog timer (1000ms timeout)
 * - Serial heartbeat protocol ("WDT_RESET\n")
 * - Emergency shutdown on watchdog timeout
 * - GPIO control for safety interlocks
 *
 * Pin Configuration:
 * - D2: Smoothing motor control (output)
 * - D3: Vibration sensor (input with pullup)
 * - D4: Aiming laser control (output)
 * - A0: Photodiode power monitoring (analog input)
 *
 * Serial Protocol (9600 baud):
 * - WDT_RESET          : Reset watchdog timer (heartbeat)
 * - MOTOR_ON           : Enable smoothing motor (D2 HIGH)
 * - MOTOR_OFF          : Disable smoothing motor (D2 LOW)
 * - LASER_ON           : Enable aiming laser (D4 HIGH)
 * - LASER_OFF          : Disable aiming laser (D4 LOW)
 * - GET_VIBRATION      : Read vibration sensor (D3)
 * - GET_PHOTODIODE     : Read photodiode voltage (A0)
 * - GET_STATUS         : Get all pin states
 *
 * Author: TOSCA Development Team
 * Version: 1.0
 * Date: 2025-10-25
 */

#include <avr/wdt.h>
#include <avr/interrupt.h>

// Pin definitions
#define MOTOR_PIN 2
#define VIBRATION_PIN 3
#define AIMING_LASER_PIN 4
#define PHOTODIODE_PIN A0

// Watchdog configuration
#define WATCHDOG_TIMEOUT_MS 1000
#define HEARTBEAT_REQUIRED true

// State tracking
bool motor_enabled = false;
bool aiming_laser_enabled = false;
bool watchdog_enabled = false;
unsigned long last_heartbeat = 0;

void setup() {
  // Disable interrupts during setup
  cli();

  // Configure pins
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(VIBRATION_PIN, INPUT_PULLUP);  // Pullup for sensor
  pinMode(AIMING_LASER_PIN, OUTPUT);
  pinMode(PHOTODIODE_PIN, INPUT);

  // Start with all outputs OFF (fail-safe)
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(AIMING_LASER_PIN, LOW);
  motor_enabled = false;
  aiming_laser_enabled = false;

  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("TOSCA Safety Watchdog v1.0");
  Serial.println("Initializing...");

  // Enable watchdog timer (1000ms timeout)
  // WDTO_1S = 1 second timeout
  wdt_enable(WDTO_1S);
  watchdog_enabled = true;
  last_heartbeat = millis();

  Serial.println("Watchdog enabled (1000ms timeout)");
  Serial.println("Ready. Send WDT_RESET every 500ms");
  Serial.println("-----------------------------------");

  // Enable interrupts
  sei();
}

void loop() {
  // Process serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace

    processCommand(command);
  }

  // Small delay to prevent overwhelming the serial buffer
  delay(10);
}

void processCommand(String cmd) {
  // Watchdog heartbeat
  if (cmd == "WDT_RESET") {
    wdt_reset();  // Reset watchdog timer
    last_heartbeat = millis();
    Serial.println("OK:WDT_RESET");
  }

  // Motor control
  else if (cmd == "MOTOR_ON") {
    digitalWrite(MOTOR_PIN, HIGH);
    motor_enabled = true;
    Serial.println("OK:MOTOR_ON");
  }
  else if (cmd == "MOTOR_OFF") {
    digitalWrite(MOTOR_PIN, LOW);
    motor_enabled = false;
    Serial.println("OK:MOTOR_OFF");
  }

  // Aiming laser control
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

  // Sensor reads
  else if (cmd == "GET_VIBRATION") {
    bool vibration = !digitalRead(VIBRATION_PIN);  // Inverted (pullup)
    Serial.print("VIBRATION:");
    Serial.println(vibration ? "1" : "0");
  }
  else if (cmd == "GET_PHOTODIODE") {
    int raw = analogRead(PHOTODIODE_PIN);
    float voltage = (raw / 1023.0) * 5.0;  // Convert to voltage
    Serial.print("PHOTODIODE:");
    Serial.println(voltage, 3);  // 3 decimal places
  }

  // Status query
  else if (cmd == "GET_STATUS") {
    Serial.println("STATUS:");
    Serial.print("  Motor: ");
    Serial.println(motor_enabled ? "ON" : "OFF");
    Serial.print("  Aiming Laser: ");
    Serial.println(aiming_laser_enabled ? "ON" : "OFF");
    Serial.print("  Vibration: ");
    Serial.println(!digitalRead(VIBRATION_PIN) ? "DETECTED" : "NONE");
    Serial.print("  Photodiode: ");
    int raw = analogRead(PHOTODIODE_PIN);
    float voltage = (raw / 1023.0) * 5.0;
    Serial.print(voltage, 3);
    Serial.println("V");
    Serial.print("  Watchdog: ");
    Serial.println(watchdog_enabled ? "ENABLED" : "DISABLED");
    unsigned long since_heartbeat = millis() - last_heartbeat;
    Serial.print("  Last Heartbeat: ");
    Serial.print(since_heartbeat);
    Serial.println("ms ago");
    Serial.println("OK:STATUS");
  }

  // Watchdog control (for testing only)
  else if (cmd == "WDT_DISABLE") {
    wdt_disable();
    watchdog_enabled = false;
    Serial.println("WARNING:WDT_DISABLED");
  }
  else if (cmd == "WDT_ENABLE") {
    wdt_enable(WDTO_1S);
    watchdog_enabled = true;
    last_heartbeat = millis();
    Serial.println("OK:WDT_ENABLED");
  }

  // Unknown command
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(cmd);
  }
}

/*
 * Watchdog Timeout Interrupt Service Routine
 *
 * This ISR is called when the watchdog timer expires (no heartbeat for 1000ms).
 * Performs emergency shutdown:
 * - Sets all outputs LOW (motor OFF, laser OFF)
 * - Disables all interrupts
 * - Halts system in infinite loop (requires power cycle to recover)
 *
 * CRITICAL: This code must be minimal and fast.
 * Do not use Serial.print() or other slow operations.
 */
ISR(WDT_vect) {
  // Disable interrupts immediately
  cli();

  // Emergency shutdown: Set all outputs LOW
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(AIMING_LASER_PIN, LOW);

  // Halt system (infinite loop - requires power cycle)
  // This prevents any further operation until manual intervention
  while(1) {
    // Infinite loop - system is halted
    // Power cycle required to recover
  }
}
