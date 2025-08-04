// Define L298N module 10 Pin
#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11

int speedA = 0;
int speedB = 0;

// Setup function - runs once at startup
void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
}

// Accelerate motors gradually
void accelerate() {
  for (int speed = 0; speed <= 255; speed += 15) {
    analogWrite(ENA, speed);
    analogWrite(ENB, speed);
    delay(50);
  }
  Serial.println("Accelerated to full speed");
}

// Decelerate motors gradually
void decelerate() {
  for (int speed = 255; speed >= 0; speed -= 15) {
    analogWrite(ENA, speed);
    analogWrite(ENB, speed);
    delay(50);
  }
  Serial.println("Decelerated to stop");
}

// Move Forward
void forward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  accelerate();
  Serial.println("Forward");
}

// Move Backward
void back() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  accelerate();
  Serial.println("Back");
}

// Turn Left
void left() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  accelerate();
  Serial.println("Left");
}

// Turn Right
void right() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  accelerate();
  Serial.println("Right");
}

// Loop function - repeats forever
void loop() {
  forward();
  delay(1000);
  decelerate();
  delay(500);

  back();
  delay(1000);
  decelerate();
  delay(500);

  left();
  delay(1000);
  decelerate();
  delay(500);

  right();
  delay(1000);
  decelerate();
  delay(500);

}
