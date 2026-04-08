#include <Servo.h>

// Pin definitions
const int SERVO_PIN = 13;  // Change this to your servo pin

// Servo object
Servo myServo;

// Serial settings (must match Python script)
const int BAUD_RATE = 115200;

// Servo limits (must match Python script)
const int SERVO_MIN = 20;
const int SERVO_MAX = 160;

// Current servo position
int currentAngle = 90;

void setup() {
  // Initialize serial communication
  Serial.begin(BAUD_RATE);
  delay(2000);  // Wait for serial to initialize

  // Attach servo to pin
  myServo.attach(SERVO_PIN);

  // Set initial position
  myServo.write(currentAngle);

  Serial.println("ESP Servo Controller Ready");
  Serial.println("Waiting for commands...");
}

void loop() {
  // Check if data is available on serial
  if (Serial.available() > 0) {
    // Read the incoming line
    String command = Serial.readStringUntil('\n');

    // Remove any whitespace
    command.trim();

    // Check if command starts with 'A' (Angle command)
    if (command.length() >= 4 && command.charAt(0) == 'A') {
      // Extract angle value (characters 1-3)
      String angleStr = command.substring(1, 4);

      // Convert to integer
      int newAngle = angleStr.toInt();

      // Validate angle range
      if (newAngle >= SERVO_MIN && newAngle <= SERVO_MAX) {
        // Move servo to new position
        myServo.write(newAngle);
        currentAngle = newAngle;

        // Send confirmation back to Python
        Serial.print("OK: Servo moved to ");
        Serial.print(newAngle);
        Serial.println(" degrees");
      } else {
        // Invalid angle
        Serial.print("ERROR: Invalid angle ");
        Serial.print(newAngle);
        Serial.print(" (must be ");
        Serial.print(SERVO_MIN);
        Serial.print("-");
        Serial.print(SERVO_MAX);
        Serial.println(")");
      }
    } else {
      // Unknown command
      Serial.print("ERROR: Unknown command '");
      Serial.print(command);
      Serial.println("'");
    }
  }

  // Small delay to prevent overwhelming the serial buffer
  delay(10);
}