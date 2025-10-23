// Simple ESP32 Test Sketch
// This minimal code just tests basic serial communication

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("ESP32 Test Starting...");
  Serial.println("Type 'hello' to test communication");
  Serial.println("Ready!");
}

void loop() {
  // Echo any received serial data
  if (Serial.available()) {
    String input = Serial.readString();
    input.trim();
    Serial.println("Received: " + input);
    
    if (input.equalsIgnoreCase("hello")) {
      Serial.println("Hello back! ESP32 is working!");
    }
  }
  
  // Send a heartbeat every 5 seconds
  static unsigned long lastHeartbeat = 0;
  if (millis() - lastHeartbeat > 5000) {
    lastHeartbeat = millis();
    Serial.println("Heartbeat: " + String(millis()/1000) + " seconds");
  }
  
  delay(100);
}