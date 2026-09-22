// ============================
// Autonomous Robot Brain - Arduino Layer
// ============================

// Motor pins
int motor_left[] = {5, 6};
int motor_right[] = {7, 8};

// LED for status
int statusLED = 12;

// Sensors
int trigPin = 9;  // Ultrasonic Trigger
int echoPin = 10; // Ultrasonic Echo

// Variables
long duration;
int distance;

// --------------------------- Setup
void setup() {
  Serial.begin(9600);

  // Motors
  for (int i = 0; i < 2; i++) {
    pinMode(motor_left[i], OUTPUT);
    pinMode(motor_right[i], OUTPUT);
  }

  // LED
  pinMode(statusLED, OUTPUT);
  digitalWrite(statusLED, LOW);

  // Ultrasonic
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

// --------------------------- Main Loop
void loop() {
  // Read sensor
  distance = readUltrasonic();

  // Send sensor data to AI
  Serial.print("DISTANCE:");
  Serial.println(distance);

  // Simple local decision (avoid obstacle)
  if (distance < 20) {
    stopMotors();
    turnRight();
  } else {
    driveForward();
  }

  delay(100); // Small delay for loop
}

// --------------------------- Functions

int readUltrasonic() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  int dist = duration * 0.034 / 2;
  return dist;
}

void driveForward() {
  digitalWrite(motor_left[0], HIGH);
  digitalWrite(motor_left[1], LOW);
  digitalWrite(motor_right[0], HIGH);
  digitalWrite(motor_right[1], LOW);
}

void stopMotors() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(motor_left[i], LOW);
    digitalWrite(motor_right[i], LOW);
  }
}

void turnRight() {
  digitalWrite(motor_left[0], HIGH);
  digitalWrite(motor_left[1], LOW);
  digitalWrite(motor_right[0], LOW);
  digitalWrite(motor_right[1], HIGH);
}
