#include <Servo.h>

// ----- MOTOR SETUP -----
Servo leftMotor;
Servo rightMotor;
int leftMotorPin = 9;
int rightMotorPin = 10;

// ----- SENSOR SETUP -----
int ultrasonicTrig = 7;
int ultrasonicEcho = 6;
float distance = 0;

void setup() {
  Serial.begin(115200);
  
  // Motors
  leftMotor.attach(leftMotorPin);
  rightMotor.attach(rightMotorPin);
  
  // Sensors
  pinMode(ultrasonicTrig, OUTPUT);
  pinMode(ultrasonicEcho, INPUT);
}

void loop() {
  // Read Ultrasonic Sensor
  digitalWrite(ultrasonicTrig, LOW);
  delayMicroseconds(2);
  digitalWrite(ultrasonicTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(ultrasonicTrig, LOW);

  long duration = pulseIn(ultrasonicEcho, HIGH);
  distance = duration * 0.034 / 2; // cm

  // Send sensor data to Python
  Serial.println(distance);

  // Receive motor commands from Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "FORWARD") { moveForward(); }
    else if (command == "BACKWARD") { moveBackward(); }
    else if (command == "LEFT") { turnLeft(); }
    else if (command == "RIGHT") { turnRight(); }
    else if (command == "STOP") { stopMotors(); }
  }

  delay(50);
}

// ----- MOTOR FUNCTIONS -----
void moveForward() {
  leftMotor.write(180);
  rightMotor.write(0);
}

void moveBackward() {
  leftMotor.write(0);
  rightMotor.write(180);
}

void turnLeft() {
  leftMotor.write(0);
  rightMotor.write(0);
  rightMotor.write(0);
}

void turnRight() {
  leftMotor.write(180);
  rightMotor.write(180);
}

void stopMotors() {
  leftMotor.write(90);
  rightMotor.write(90);
}
