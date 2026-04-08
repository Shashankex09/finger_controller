#include <ESP32Servo.h>

// Pin definitions
const int SERVO_PIN = 13;  // Change this to your servo pin (PWM capable)

// Servo object
Servo myServo;

// Serial settings (must match Python script)
const int BAUD_RATE = 115200;

// Servo limits (must match Python script)
const int SERVO_MIN = 20;
const int SERVO_MAX = 160;
const int SERVO_REST = 90;

// Current servo position
int currentAngle = 90;
int lastAngle = 90;
unsigned long lastMoveTime = 0;
const unsigned long MIN_MOVE_DELAY = 20;  // Minimum 20ms between moves

void setup() {
  // Initialize serial communication
  Serial.begin(BAUD_RATE);
  delay(2000);  // Wait for serial to initialize

  // Configure servo with proper PWM settings for ESP32
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  myServo.setPeriodHertz(50);  // Standard servo frequency
  myServo.attach(SERVO_PIN, SERVO_MIN, SERVO_MAX);

  // Set initial position
  myServo.write(currentAngle);

  Serial.println("ESP32 Servo Controller Ready");
  Serial.println("Format: A###");
  Serial.println("Example: A090");
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
        unsigned long now = millis();
        
        // Check if minimum delay has passed
        if (now - lastMoveTime >= MIN_MOVE_DELAY) {
          // Only move if angle is different
          if (newAngle != currentAngle) {
            myServo.write(newAngle);
            currentAngle = newAngle;
            lastMoveTime = now;
            
            // Send confirmation back to Python
            Serial.print("OK:");
            Serial.println(newAngle);
          }
        }
      } else {
        // Invalid angle
        Serial.print("ERR:Range ");
        Serial.print(SERVO_MIN);
        Serial.print("-");
        Serial.println(SERVO_MAX);
      }
    } else if (command.length() > 0) {
      // Unknown command
      Serial.println("ERR:Format");
    }
  }

  // Small delay to prevent overwhelming the serial buffer
  delayMicroseconds(100);
}
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