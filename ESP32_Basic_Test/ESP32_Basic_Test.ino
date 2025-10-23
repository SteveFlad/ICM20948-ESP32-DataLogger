/*
  ESP32 Basic Communication Test
  Simple sketch to test Arduino IDE upload and serial communication
  Upload this first to verify everything works before the full ICM20948 code
*/

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("=== ESP32 Basic Test ===");
  Serial.println("Arduino IDE Upload Successful!");
  Serial.println("ESP32 is running and responding");
  Serial.println("Type 'help' for commands");
  Serial.println("Ready for communication test");
}

void loop() {
  // Handle serial commands
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    command.toUpperCase();
    
    Serial.println("Received: " + command);
    
    if (command == "HELP") {
      Serial.println("Available commands:");
      Serial.println("  HELP - Show this help");
      Serial.println("  STATUS - Show ESP32 status");
      Serial.println("  TEST - Run connection test");
      Serial.println("  HELLO - Say hello");
    }
    else if (command == "STATUS") {
      Serial.println("=== ESP32 Status ===");
      Serial.println("Chip: " + String(ESP.getChipModel()));
      Serial.println("CPU Frequency: " + String(ESP.getCpuFreqMHz()) + " MHz");
      Serial.println("Flash Size: " + String(ESP.getFlashChipSize()) + " bytes");
      Serial.println("Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
      Serial.println("Uptime: " + String(millis() / 1000) + " seconds");
    }
    else if (command == "TEST") {
      Serial.println("=== Connection Test ===");
      for (int i = 1; i <= 5; i++) {
        Serial.println("Test message " + String(i) + "/5");
        delay(200);
      }
      Serial.println("Test completed successfully!");
    }
    else if (command == "HELLO") {
      Serial.println("Hello! ESP32 is working perfectly!");
      Serial.println("Arduino IDE upload was successful!");
    }
    else {
      Serial.println("Unknown command: " + command);
      Serial.println("Type 'help' for available commands");
    }
  }
  
  // Send heartbeat every 5 seconds
  static unsigned long lastHeartbeat = 0;
  if (millis() - lastHeartbeat > 5000) {
    lastHeartbeat = millis();
    Serial.println("Heartbeat: " + String(millis() / 1000) + "s - ESP32 alive");
  }
  
  delay(100);
}