#include <Arduino.h>

// Simple ESP32 communication test
String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  delay(1000);
  Serial.println("ESP32 Communication Test");
  Serial.println("Ready for commands!");
  Serial.println("Type HELP for available commands");
}

void loop() {
  // Check for commands from Serial
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Process complete command
  if (stringComplete) {
    inputString.trim();
    Serial.println("Received command: '" + inputString + "'");
    
    if (inputString == "HELP") {
      Serial.println("Available commands: HELP, TEST, HELLO");
    }
    else if (inputString == "TEST") {
      Serial.println("Test response - ESP32 is working!");
    }
    else if (inputString == "HELLO") {
      Serial.println("Hello from ESP32!");
    }
    else {
      Serial.println("Unknown command: " + inputString);
    }
    
    inputString = "";
    stringComplete = false;
  }
  
  delay(10);
}