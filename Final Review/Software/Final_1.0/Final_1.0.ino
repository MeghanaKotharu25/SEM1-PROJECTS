#include <Servo.h>

Servo bladeServo;
int servoPin = 9;

void setup() {
  bladeServo.attach(servoPin);
  Serial.begin(9600);
  bladeServo.write(90); // Initialize servo to 90 degrees
}

void loop() {
  if (Serial.available() > 0) {
    String angleInput = Serial.readStringUntil('\n'); // Read until newline
    int angle = angleInput.toInt(); // Convert input to integer
    if (angle >= 0 && angle <= 180) {
      bladeServo.write(angle); // Set the servo to the angle
      Serial.println("ACK"); // Send acknowledgment to Python
    } else {
      Serial.println("ERROR: Angle out of range"); // Error handling
    }
  }
}