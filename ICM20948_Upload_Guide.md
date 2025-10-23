# Complete ICM20948 Firmware Upload Guide

## 🔧 Required Libraries Installation

**BEFORE uploading the firmware, install these libraries through Arduino IDE:**

### Method 1: Arduino Library Manager (Recommended)

1. Open Arduino IDE
2. Go to **Tools → Manage Libraries** (Ctrl+Shift+I)
3. Search and install the following libraries:

   - **Adafruit ICM20X** (by Adafruit)
   - **Adafruit Unified Sensor** (by Adafruit)
   - **Adafruit BusIO** (automatically installed with ICM20X)

### Method 2: Manual Installation

If Library Manager fails, manually install:

1. Download from: <https://github.com/adafruit/Adafruit_ICM20X>
2. Extract to: `Documents\Arduino\libraries\`

## 📁 File Location

**Sketch file:** `ICM20948_Full_Arduino\ICM20948_Full_Arduino.ino`

## 🚀 Upload Process

### Step 1: Open the Complete Sketch

1. Open Arduino IDE
2. File → Open → Navigate to `ICM20948_Full_Arduino.ino`

### Step 2: Verify Board Settings

- **Board:** "ESP32 Dev Module"
- **Port:** COM3 (your working port)
- **Upload Speed:** 921600
- **CPU Frequency:** 240MHz (WiFi/BT)
- **Flash Frequency:** 80MHz
- **Flash Mode:** QIO
- **Flash Size:** 4MB
- **Partition Scheme:** Default 4MB

### Step 3: Put ESP32 in Programming Mode

**CRITICAL STEPS:**

1. Hold **BOOT** button on ESP32
2. Press **EN** (reset) button briefly while holding BOOT
3. Release **EN** button (keep holding BOOT)
4. Click **Upload** in Arduino IDE immediately
5. Release **BOOT** button when upload starts

### Step 4: Verify Upload

- Look for "Hard resetting via RTS pin..." at end
- ESP32 should restart automatically
- Open Serial Monitor (Ctrl+Shift+M) at 115200 baud

## 🔍 Expected Output After Upload

```
=== ICM20948 Configurable Data Logger ===
I2C initialized
Scanning I2C bus...
I2C device found at address 0x68!
Found 1 device(s)
Initializing ICM20948...
ICM20948 found at address 0x68
Applying configuration...
Configuration applied successfully
Ready! Type HELP for commands
CONFIG:ACCEL_RANGE=1,GYRO_RANGE=0,MAG_RATE=6,SAMPLE_RATE=100,EN_ACCEL=1,EN_GYRO=1,EN_MAG=1,EN_TEMP=1,STREAMING=0
```

## ✅ Testing Commands

Type these in Serial Monitor to test:

- `HELP` - Show all available commands
- `SCAN` - Scan I2C bus for sensor
- `STATUS` - Show ESP32 status
- `CONFIG` - Show current sensor configuration
- `START` - Begin data streaming
- `STOP` - Stop data streaming

## 🎯 Success Indicators

**✅ Sensor Working:**

- I2C scan finds device at 0x68 or 0x69
- "ICM20948 found" message appears
- CONFIG command shows sensor settings

**✅ Data Streaming:**

- START command begins data flow
- DATA: lines with timestamp and sensor values
- Format: `DATA:timestamp,ax,ay,az,gx,gy,gz,mx,my,mz,temp`

## 🔧 Troubleshooting

**If libraries missing:**

- Install Adafruit ICM20X and dependencies
- Restart Arduino IDE after installation

**If sensor not found:**

- Check I2C wiring (SDA=21, SCL=22)
- Try both 0x68 and 0x69 addresses
- Use SCAN command to verify I2C devices

**If upload fails:**

- Double-check programming mode procedure
- Verify COM port selection
- Try lower upload speed (460800)

## 🔗 Next Steps After Upload

1. **Test Sensor Detection:** Use SCAN and STATUS commands
2. **Verify Data Streaming:** Use START command
3. **Test Python GUI:** Run the optimized ICM20948_Controller.py
4. **Check Bluetooth:** "ESP32_ICM20948_Config" device should appear

---

**Ready to upload? Follow the programming mode procedure carefully!**
