#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include "BluetoothSerial.h"

Adafruit_ICM20948 icm;
BluetoothSerial SerialBT;

// Configuration parameters
struct ICMConfig {
  uint8_t accel_range = ICM20948_ACCEL_RANGE_4_G;
  uint8_t gyro_range = ICM20948_GYRO_RANGE_250_DPS;
  uint8_t mag_data_rate = AK09916_MAG_DATARATE_10_HZ;
  uint16_t sample_rate = 100; // Sample rate in Hz
  bool enable_accel = true;
  bool enable_gyro = true;
  bool enable_mag = true;
  bool enable_temp = true;
  bool streaming = false;
} config;

unsigned long lastSampleTime = 0;
unsigned long sampleInterval = 10; // Default 100Hz (10ms interval)

// Command parsing
String inputString = "";
bool stringComplete = false;

// I2C Scanner function
void scanI2C() {
  Serial.println("Scanning I2C bus...");
  SerialBT.println("Scanning I2C bus...");
  byte error, address;
  int nDevices = 0;
  
  for(address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    
    if (error == 0) {
      String msg = "I2C device found at address 0x";
      if (address < 16) msg += "0";
      msg += String(address, HEX) + "!";
      Serial.println(msg);
      SerialBT.println(msg);
      nDevices++;
    }
  }
  
  String result = nDevices == 0 ? "No I2C devices found" : 
                  "Found " + String(nDevices) + " device(s)";
  Serial.println(result);
  SerialBT.println(result);
}

// Apply configuration to sensor
void applyConfiguration() {
  Serial.println("Applying configuration...");
  SerialBT.println("Applying configuration...");
  
  // Set accelerometer range
  icm.setAccelRange((icm20948_accel_range_t)config.accel_range);
  
  // Set gyroscope range  
  icm.setGyroRange((icm20948_gyro_range_t)config.gyro_range);
  
  // Set magnetometer data rate
  icm.setMagDataRate((ak09916_data_rate_t)config.mag_data_rate);
  
  // Calculate sample interval from sample rate
  sampleInterval = 1000 / config.sample_rate;
  
  Serial.println("Configuration applied successfully");
  SerialBT.println("Configuration applied successfully");
}

// Send current configuration
void sendConfiguration() {
  String cfg = "CONFIG:";
  cfg += "ACCEL_RANGE=" + String(config.accel_range) + ",";
  cfg += "GYRO_RANGE=" + String(config.gyro_range) + ",";
  cfg += "MAG_RATE=" + String(config.mag_data_rate) + ",";
  cfg += "SAMPLE_RATE=" + String(config.sample_rate) + ",";
  cfg += "EN_ACCEL=" + String(config.enable_accel) + ",";
  cfg += "EN_GYRO=" + String(config.enable_gyro) + ",";
  cfg += "EN_MAG=" + String(config.enable_mag) + ",";
  cfg += "EN_TEMP=" + String(config.enable_temp) + ",";
  cfg += "STREAMING=" + String(config.streaming);
  
  Serial.println(cfg);
  SerialBT.println(cfg);
}

// Process incoming commands
void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command == "SCAN") {
    scanI2C();
  }
  else if (command == "CONFIG") {
    sendConfiguration();
  }
  else if (command == "START") {
    Serial.println("DEBUG: START command received");
    SerialBT.println("DEBUG: START command received");
    config.streaming = true;
    Serial.println("Started streaming");
    SerialBT.println("Started streaming");
  }
  else if (command == "STOP") {
    Serial.println("DEBUG: STOP command received");
    SerialBT.println("DEBUG: STOP command received");
    config.streaming = false;
    Serial.println("Stopped streaming");
    SerialBT.println("Stopped streaming");
  }
  else if (command.startsWith("SET_ACCEL_RANGE=")) {
    int value = command.substring(16).toInt();
    if (value >= 0 && value <= 3) {
      config.accel_range = value;
      applyConfiguration();
    }
  }
  else if (command.startsWith("SET_GYRO_RANGE=")) {
    int value = command.substring(15).toInt();
    if (value >= 0 && value <= 3) {
      config.gyro_range = value;
      applyConfiguration();
    }
  }
  else if (command.startsWith("SET_MAG_RATE=")) {
    int value = command.substring(13).toInt();
    if (value >= 0 && value <= 8) {
      config.mag_data_rate = value;
      applyConfiguration();
    }
  }
  else if (command.startsWith("SET_SAMPLE_RATE=")) {
    int value = command.substring(16).toInt();
    if (value >= 1 && value <= 1000) {
      config.sample_rate = value;
      sampleInterval = 1000 / value;
      Serial.println("Sample rate set to " + String(value) + " Hz");
      SerialBT.println("Sample rate set to " + String(value) + " Hz");
    }
  }
  else if (command.startsWith("ENABLE_ACCEL=")) {
    config.enable_accel = command.substring(13).toInt() == 1;
    Serial.println("Accelerometer " + String(config.enable_accel ? "enabled" : "disabled"));
    SerialBT.println("Accelerometer " + String(config.enable_accel ? "enabled" : "disabled"));
  }
  else if (command.startsWith("ENABLE_GYRO=")) {
    config.enable_gyro = command.substring(12).toInt() == 1;
    Serial.println("Gyroscope " + String(config.enable_gyro ? "enabled" : "disabled"));
    SerialBT.println("Gyroscope " + String(config.enable_gyro ? "enabled" : "disabled"));
  }
  else if (command.startsWith("ENABLE_MAG=")) {
    config.enable_mag = command.substring(11).toInt() == 1;
    Serial.println("Magnetometer " + String(config.enable_mag ? "enabled" : "disabled"));
    SerialBT.println("Magnetometer " + String(config.enable_mag ? "enabled" : "disabled"));
  }
  else if (command.startsWith("ENABLE_TEMP=")) {
    config.enable_temp = command.substring(12).toInt() == 1;
    Serial.println("Temperature " + String(config.enable_temp ? "enabled" : "disabled"));
    SerialBT.println("Temperature " + String(config.enable_temp ? "enabled" : "disabled"));
  }
  else if (command == "HELP") {
    Serial.println("Available commands:");
    Serial.println("  SCAN - Scan I2C bus");
    Serial.println("  CONFIG - Show current configuration");
    Serial.println("  START - Start data streaming");
    Serial.println("  STOP - Stop data streaming");
    Serial.println("  SET_ACCEL_RANGE=<0-3> - Set accelerometer range");
    Serial.println("  SET_GYRO_RANGE=<0-3> - Set gyroscope range");
    Serial.println("  SET_MAG_RATE=<0-8> - Set magnetometer data rate");
    Serial.println("  SET_SAMPLE_RATE=<1-1000> - Set sample rate in Hz");
    Serial.println("  ENABLE_ACCEL=<0/1> - Enable/disable accelerometer");
    Serial.println("  ENABLE_GYRO=<0/1> - Enable/disable gyroscope");
    Serial.println("  ENABLE_MAG=<0/1> - Enable/disable magnetometer");
    Serial.println("  ENABLE_TEMP=<0/1> - Enable/disable temperature");
    Serial.println("  HELP - Show this help");
    
    SerialBT.println("Available commands:");
    SerialBT.println("  SCAN, CONFIG, START, STOP, SET_ACCEL_RANGE=<0-3>");
    SerialBT.println("  SET_GYRO_RANGE=<0-3>, SET_MAG_RATE=<0-8>");
    SerialBT.println("  SET_SAMPLE_RATE=<1-1000>, ENABLE_ACCEL/GYRO/MAG/TEMP=<0/1>");
    SerialBT.println("  HELP - Show help");
  }
  else {
    Serial.println("Unknown command: " + command);
    SerialBT.println("Unknown command: " + command + " (Type HELP for commands)");
  }
}

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_ICM20948_Config"); // Bluetooth device name
  
  while (!Serial) delay(10);
  
  Serial.println("ICM20948 Configurable Data Logger");
  SerialBT.println("ICM20948 Configurable Data Logger");
  
  // Initialize I2C
  Wire.begin(21, 22); // SDA=21, SCL=22 for ESP32
  Wire.setClock(100000); // 100kHz for reliability
  
  Serial.println("I2C initialized");
  SerialBT.println("I2C initialized");
  delay(1000);
  
  // Scan I2C bus first
  scanI2C();
  
  // Try to initialize the sensor at both addresses
  Serial.println("Initializing ICM20948...");
  SerialBT.println("Initializing ICM20948...");
  
  if (!icm.begin_I2C(0x68)) {
    if (!icm.begin_I2C(0x69)) {
      Serial.println("Failed to find ICM20948 chip!");
      SerialBT.println("Failed to find ICM20948 chip!");
      while (1) delay(10);
    } else {
      Serial.println("ICM20948 found at address 0x69");
      SerialBT.println("ICM20948 found at address 0x69");
    }
  } else {
    Serial.println("ICM20948 found at address 0x68");
    SerialBT.println("ICM20948 found at address 0x68");
  }
  
  // Apply initial configuration
  applyConfiguration();
  
  Serial.println("Ready! Type HELP for commands");
  SerialBT.println("Ready! Type HELP for commands");
  
  // Send initial configuration
  sendConfiguration();
}

void loop() {
  // Always yield to prevent watchdog issues
  yield();
  
  // Check for commands from Serial
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Check for commands from Bluetooth
  while (SerialBT.available()) {
    char inChar = (char)SerialBT.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Process complete command
  if (stringComplete) {
    // Remove newline and carriage return characters
    inputString.trim();
    Serial.println("DEBUG: Processing command: '" + inputString + "'");
    SerialBT.println("DEBUG: Processing command: '" + inputString + "'");
    
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Stream data if enabled
  if (config.streaming && (millis() - lastSampleTime >= sampleInterval)) {
    lastSampleTime = millis();
    
    // Get sensor events - remove debug messages to reduce blocking time
    sensors_event_t accel, gyro, mag, temp;
    
    // Try to get sensor data quickly
    icm.getEvent(&accel, &gyro, &temp, &mag);
    
    // Build data string efficiently
    String dataString = "DATA:";
    dataString += String(millis()) + ",";
    
    if (config.enable_accel) {
      dataString += String(accel.acceleration.x, 3) + ",";  // Reduced precision for speed
      dataString += String(accel.acceleration.y, 3) + ",";
      dataString += String(accel.acceleration.z, 3) + ",";
    } else {
      dataString += "0,0,0,";
    }
    
    if (config.enable_gyro) {
      dataString += String(gyro.gyro.x, 3) + ",";
      dataString += String(gyro.gyro.y, 3) + ",";
      dataString += String(gyro.gyro.z, 3) + ",";
    } else {
      dataString += "0,0,0,";
    }
    
    if (config.enable_mag) {
      dataString += String(mag.magnetic.x, 3) + ",";
      dataString += String(mag.magnetic.y, 3) + ",";
      dataString += String(mag.magnetic.z, 3) + ",";
    } else {
      dataString += "0,0,0,";
    }
    
    if (config.enable_temp) {
      dataString += String(temp.temperature, 1);
    } else {
      dataString += "0";
    }
    
    // Send data quickly without waiting
    Serial.println(dataString);
    SerialBT.println(dataString);
  }
  
  // Small delay and yield to prevent blocking
  yield();
  delay(1);
}