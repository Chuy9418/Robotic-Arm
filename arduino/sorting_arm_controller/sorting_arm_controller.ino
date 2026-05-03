// arduino/sorting_arm_controller/sorting_arm_controller.ino

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// PCA9685 servo driver object
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Adjust these if your servos do not reach correct angles
#define SERVOMIN 150
#define SERVOMAX 600

// Optional electromagnet pin
#define MAGNET_PIN 8

int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void setup() {
  Serial.begin(9600);

  // Start PCA9685
  pwm.begin();
  pwm.setPWMFreq(50);  // Standard servo frequency

  // Electromagnet setup
  pinMode(MAGNET_PIN, OUTPUT);
  digitalWrite(MAGNET_PIN, LOW);

  delay(500);
  Serial.println("Arduino ready");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    int channel;
    int angle;

    // Example command: MOVE 0 90
    if (command.startsWith("MOVE")) {
      sscanf(command.c_str(), "MOVE %d %d", &channel, &angle);

      channel = constrain(channel, 0, 15);
      angle = constrain(angle, 0, 180);

      pwm.setPWM(channel, 0, angleToPulse(angle));

      Serial.print("OK MOVE ");
      Serial.print(channel);
      Serial.print(" ");
      Serial.println(angle);
    }

    // Example command: MAGNET ON
    else if (command == "MAGNET ON") {
      digitalWrite(MAGNET_PIN, HIGH);
      Serial.println("OK MAGNET ON");
    }

    // Example command: MAGNET OFF
    else if (command == "MAGNET OFF") {
      digitalWrite(MAGNET_PIN, LOW);
      Serial.println("OK MAGNET OFF");
    }

    // Example command: HOME
    else if (command == "HOME") {
      pwm.setPWM(0, 0, angleToPulse(90));
      pwm.setPWM(1, 0, angleToPulse(90));
      pwm.setPWM(2, 0, angleToPulse(90));
      pwm.setPWM(3, 0, angleToPulse(90));

      digitalWrite(MAGNET_PIN, LOW);

      Serial.println("OK HOME");
    }

    else {
      Serial.print("ERROR Unknown command: ");
      Serial.println(command);
    }
  }
}
