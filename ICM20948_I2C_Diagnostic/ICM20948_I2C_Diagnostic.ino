/*
  ICM20948 I2C Diagnostic Tool
  Tests different I2C configurations to find working setup
*/

#include <Wire.h>

// Test different I2C pin combinations
struct I2CPins {
  int sda;
  int scl;
  String name;
};

I2CPins pinConfigs[] = {
  {21, 22, "Standard (21,22)"},
  {4, 5, "Alternative 1 (4,5)"},
  {16, 17, "Alternative 2 (16,17)"},
  {25, 26, "Alternative 3 (25,26)"},
  {32, 33, "Alternative 4 (32,33)"}
};

void scanI2CWithPins(int sda, int scl, String configName) {
  Serial.println("\n=== Testing " + configName + " ===");
  
  // Initialize I2C with specific pins
  Wire.end(); // End previous I2C
  delay(100);
  Wire.begin(sda, scl);
  
  // Try different clock speeds
  int clockSpeeds[] = {100000, 50000, 10000}; // 100kHz, 50kHz, 10kHz
  String speedNames[] = {"100kHz", "50kHz", "10kHz"};
  
  for (int s = 0; s < 3; s++) {
    Wire.setClock(clockSpeeds[s]);
    Serial.println("Clock speed: " + speedNames[s]);
    
    byte error, address;
    int nDevices = 0;
    
    for(address = 1; address < 127; address++) {
      Wire.beginTransmission(address);
      error = Wire.endTransmission();
      
      if (error == 0) {
        Serial.print("Device found at 0x");
        if (address < 16) Serial.print("0");
        Serial.println(address, HEX);
        nDevices++;
      }
      else if (error == 4) {
        Serial.print("Unknown error at 0x");
        if (address < 16) Serial.print("0");
        Serial.println(address, HEX);
      }
    }
    
    if (nDevices == 0) {
      Serial.println("No I2C devices found");
    } else {
      Serial.println("Found " + String(nDevices) + " device(s)");
      if (nDevices > 0) {
        Serial.println("*** SUCCESS WITH " + configName + " at " + speedNames[s] + " ***");
      }
    }
    delay(1000);
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("=== ICM20948 I2C Diagnostic Tool ===");
  Serial.println("Testing different I2C pin configurations...");
  delay(2000);
  
  // Test each pin configuration
  for (int i = 0; i < 5; i++) {
    scanI2CWithPins(pinConfigs[i].sda, pinConfigs[i].scl, pinConfigs[i].name);
    delay(2000);
  }
  
  Serial.println("\n=== Diagnostic Complete ===");
  Serial.println("If any configuration found devices, use those pins.");
  Serial.println("Type HELP for additional commands.");
}

void loop() {
  // Check for commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command == "HELP") {
      Serial.println("Available commands:");
      Serial.println("  RESCAN - Run diagnostic again");
      Serial.println("  VOLTAGE - Check power supply");
      Serial.println("  PULLUP - Check pull-up resistors");
      Serial.println("  HELP - Show this help");
    }
    else if (command == "RESCAN") {
      Serial.println("Re-running I2C diagnostic...");
      for (int i = 0; i < 5; i++) {
        scanI2CWithPins(pinConfigs[i].sda, pinConfigs[i].scl, pinConfigs[i].name);
        delay(1000);
      }
    }
    else if (command == "VOLTAGE") {
      Serial.println("=== Power Supply Check ===");
      Serial.println("ESP32 VCC: ~3.3V");
      Serial.println("Verify ICM20948 gets 3.3V on VCC pin");
      Serial.println("Check GND connection");
      Serial.println("Some modules need 5V on VIN instead of 3.3V on VCC");
    }
    else if (command == "PULLUP") {
      Serial.println("=== Pull-up Resistor Check ===");
      Serial.println("I2C needs pull-up resistors on SDA and SCL");
      Serial.println("Many ICM20948 modules have built-in 10kΩ pull-ups");
      Serial.println("If not, add 4.7kΩ or 10kΩ resistors:");
      Serial.println("  SDA pin → 3.3V via resistor");
      Serial.println("  SCL pin → 3.3V via resistor");
    }
    else {
      Serial.println("Unknown command. Type HELP for commands.");
    }
  }
  
  delay(100);
}