#include <Servo.h>

const int trigPin = A5;
const int echoPin = A4;
Servo myServo;

void setup() {
  Serial.begin(9600);
  myServo.attach(3); // Servo pin

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

long getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  long distance = duration * 0.034 / 2; // cm
  return distance;
}

void loop() {
  for (int angle = 0; angle <= 180; angle += 2) {
    myServo.write(angle);
    delay(50); // allow servo to reach

    long dist = getDistance();
    Serial.print(angle);
    Serial.print(",");
    Serial.println(dist);

    delay(20);
  }
}

