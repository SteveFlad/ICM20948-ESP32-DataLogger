# ICM20948 Sensor Data Acquisition System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Arduino](https://img.shields.io/badge/Arduino-Compatible-brightgreen.svg)](https://www.arduino.cc/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)

A complete real-time sensor data acquisition system for the ICM20948 9-axis IMU sensor using ESP32 and Python GUI. Features configurable parameters, live data visualization, Bluetooth connectivity, and professional data logging.

## ✨ Features

- 🎯 **Real-time data streaming** from ICM20948 sensor
- ⚙️ **Configurable sensor parameters** (ranges, sample rates, enable/disable axes)
- 📊 **Live data visualization** with matplotlib plotting
- 🔄 **Non-blocking GUI** with threaded operations
- 📱 **Bluetooth connectivity** support
- 🖥️ **Professional Python interface**
- 🔧 **Arduino IDE and PlatformIO compatible**

## 🚀 Quick Start

### Prerequisites
- ESP32 development board (NodeMCU ESP-32S)
- GY-ICM20948V2 sensor module
- Arduino IDE 2.x or PlatformIO
- Python 3.7+

### Installation
1. Clone this repository
2. Upload firmware to ESP32 (see [Upload Guide](ICM20948_Upload_Guide.md))
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run the GUI: `python ICM20948_Controller.py`

This project provides a comprehensive system for configuring and monitoring the ICM20948 9-axis IMU sensor connected to a NodeMCU ESP-32S. The system includes both an ESP32 Arduino program and a Python GUI controller for real-time parameter configuration and data visualization.

## Hardware Requirements

- NodeMCU ESP-32S development board
- GY-ICM20948V2 9-axis IMU sensor module
- Jumper wires for connections

## Hardware Connections

Connect the GY-ICM20948V2 to the NodeMCU ESP-32S as follows:

| GY-ICM20948V2 Pin | ESP32 Pin | Description |
|-------------------|-----------|-------------|
| VCC | 3.3V | Power supply |
| GND | GND | Ground |
| SDA | GPIO21 | I2C Data line |
| SCL | GPIO22 | I2C Clock line |
| AD0 | Leave unconnected or connect to 3.3V | I2C address selection (0x68 or 0x69) |

## Software Components

### 1. ESP32 Arduino Program (`main.cpp`)

The Arduino program provides:

- **Configurable sensor parameters**: Accelerometer range, gyroscope range, magnetometer data rate, sample rate
- **Command parser**: Accepts commands via Serial and Bluetooth
- **Data streaming**: Real-time sensor data output in structured format
- **Dual communication**: USB Serial and Bluetooth Serial support
- **I2C scanning**: Automatic device detection and address configuration

#### Supported Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `SCAN` | Scan I2C bus for devices | None |
| `CONFIG` | Show current configuration | None |
| `START` | Start data streaming | None |
| `STOP` | Stop data streaming | None |
| `SET_ACCEL_RANGE=<0-3>` | Set accelerometer range | 0=±2g, 1=±4g, 2=±8g, 3=±16g |
| `SET_GYRO_RANGE=<0-3>` | Set gyroscope range | 0=±250°/s, 1=±500°/s, 2=±1000°/s, 3=±2000°/s |
| `SET_MAG_RATE=<0-8>` | Set magnetometer data rate | 0=Shutdown, 1=Single, 2=10Hz, 3=20Hz, 4=50Hz, 5=100Hz, 6=200Hz, 7=1Hz, 8=Reserved |
| `SET_SAMPLE_RATE=<1-1000>` | Set sample rate in Hz | 1-1000 Hz |
| `ENABLE_ACCEL=<0/1>` | Enable/disable accelerometer | 0=Disable, 1=Enable |
| `ENABLE_GYRO=<0/1>` | Enable/disable gyroscope | 0=Disable, 1=Enable |
| `ENABLE_MAG=<0/1>` | Enable/disable magnetometer | 0=Disable, 1=Enable |
| `ENABLE_TEMP=<0/1>` | Enable/disable temperature | 0=Disable, 1=Enable |
| `HELP` | Show available commands | None |

#### Data Format

Data is streamed in the following format:

```text
DATA:timestamp,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,temperature
```

Example:

```text
DATA:12345,1.234567,-0.987654,9.876543,0.123456,-0.654321,0.789012,45.123456,-12.345678,67.890123,25.64
```

### 2. Python GUI Controller (`ICM20948_Controller.py`)

The Python GUI provides:

- **Tabbed interface**: Connection, Configuration, Data Monitor, Data Logging
- **Real-time parameter control**: Interactive widgets for all sensor parameters
- **Live data visualization**: Real-time plotting of all sensor data
- **Data logging**: CSV export with timestamps and metadata
- **Quick presets**: Golf swing, slow motion, and balanced configurations
- **Dual connectivity**: USB Serial and Bluetooth Serial support

#### GUI Tabs

1. **Connection Tab**
   - Serial port selection and connection management
   - Communication testing (SCAN, CONFIG, HELP commands)
   - Console output for all communications

2. **Configuration Tab**
   - Parameter controls for accelerometer, gyroscope, and magnetometer
   - Sensor enable/disable checkboxes
   - Quick preset buttons for common configurations

3. **Data Monitor Tab**
   - Start/stop streaming controls
   - Real-time plots for accelerometer, gyroscope, magnetometer, and temperature
   - Data clearing functionality

4. **Data Logging Tab**
   - Enable/disable data logging
   - Log file selection
   - Export current data to CSV
   - Data summary and logging status

## Installation and Setup

### ESP32 Arduino Program

1. **Install Required Libraries**:
   - Adafruit ICM20X library
   - Adafruit ICM20948 library
   - Adafruit Sensor library
   - Wire library (built-in)
   - BluetoothSerial library (ESP32 built-in)

2. **Configure PlatformIO**:
   The `platformio.ini` file should include:

   ```ini
   [env:esp32dev]
   platform = espressif32
   board = esp32dev
   framework = arduino
   monitor_speed = 115200
   ```

3. **Upload the Program**:
   - Connect ESP32 via USB
   - Build and upload using PlatformIO
   - Open Serial Monitor to verify operation

### Python GUI Controller

1. **Install Required Python Packages**:

   ```bash
   pip install tkinter pyserial matplotlib numpy
   ```

   Note: `tkinter` is usually included with Python installations.

2. **Run the GUI**:

   ```bash
   python ICM20948_Controller.py
   ```

## Usage Instructions

### Initial Setup

1. **Hardware Setup**:
   - Connect the ICM20948 sensor to the ESP32 as shown in the wiring diagram
   - Power on the ESP32

2. **Software Setup**:
   - Upload the Arduino program to the ESP32
   - Run the Python GUI application

3. **Connection**:
   - In the GUI, go to the "Connection" tab
   - Select the correct COM port (usually COM3, COM4, etc.)
   - Set baud rate to 115200
   - Click "Connect"

### Configuration

1. **Test Communication**:
   - Click "Scan I2C" to verify sensor detection
   - Click "Get Config" to retrieve current settings
   - Check console output for responses

2. **Configure Parameters**:
   - Go to the "Configuration" tab
   - Adjust accelerometer range, gyroscope range, magnetometer rate, and sample rate
   - Use checkboxes to enable/disable individual sensors
   - Try quick presets for common use cases

3. **Monitor Data**:
   - Go to the "Data Monitor" tab
   - Click "Start Streaming" to begin data collection
   - Watch real-time plots update
   - Click "Stop Streaming" to pause data collection

### Data Logging

1. **Setup Logging**:
   - Go to the "Data Logging" tab
   - Click "Select Log File" to choose where to save data
   - Enable the "Enable Logging" checkbox

2. **Record Data**:
   - Start streaming in the "Data Monitor" tab
   - Data will automatically save to the selected log file
   - Monitor data count and logging status

3. **Export Data**:
   - Click "Export Current Data" to save current session data
   - Choose filename and location for export

## Communication Protocol

### Command Structure

Commands are sent as plain text strings terminated with newline (`\n`):

- Simple commands: `SCAN`, `CONFIG`, `START`, `STOP`, `HELP`
- Parameter commands: `SET_ACCEL_RANGE=1`, `ENABLE_GYRO=0`

### Response Format

- **Configuration responses**: `CONFIG:ACCEL_RANGE=1,GYRO_RANGE=0,MAG_RATE=2,...`
- **Data responses**: `DATA:timestamp,ax,ay,az,gx,gy,gz,mx,my,mz,temp`
- **Status messages**: Plain text confirmations and error messages

### Error Handling

- Invalid commands return "Unknown command" message
- Parameter validation ensures values are within acceptable ranges
- Connection errors are displayed in GUI console
- Data parsing errors are logged and handled gracefully

## Quick Presets

### Golf Swing Preset

- Accelerometer: ±16g (high impact)
- Gyroscope: ±2000°/s (fast rotation)
- Magnetometer: 100Hz (high sample rate)
- Sample Rate: 500Hz (fast data capture)

### Slow Motion Preset

- Accelerometer: ±2g (gentle movements)
- Gyroscope: ±250°/s (slow rotation)
- Magnetometer: 10Hz (low sample rate)
- Sample Rate: 50Hz (moderate data capture)

### Balanced Preset

- Accelerometer: ±4g (moderate range)
- Gyroscope: ±500°/s (moderate rotation)
- Magnetometer: 20Hz (moderate sample rate)
- Sample Rate: 100Hz (standard data capture)

## Troubleshooting

### Connection Issues

1. **No COM ports available**:
   - Check USB cable connection
   - Install ESP32 drivers
   - Try different USB port

2. **Connection failed**:
   - Verify correct COM port selection
   - Ensure no other applications are using the port
   - Check baud rate setting (should be 115200)

3. **Bluetooth connection**:
   - Pair with "ESP32_ICM20948_Config" device
   - Use Bluetooth COM port in GUI

### Sensor Issues

1. **I2C device not found**:
   - Check wiring connections
   - Verify power supply (3.3V)
   - Try both I2C addresses (0x68, 0x69)

2. **No data streaming**:
   - Send START command
   - Check sensor enable settings
   - Verify configuration with CONFIG command

### Data Issues

1. **Plots not updating**:
   - Ensure streaming is started
   - Check data parsing in console
   - Verify sensor enables

2. **Logging not working**:
   - Select log file first
   - Enable logging checkbox
   - Check file permissions

## Advanced Features

### Custom Parameter Ranges

The system supports the full range of ICM20948 capabilities:

- Multiple accelerometer ranges for different applications
- Variable gyroscope sensitivity for rotation measurement
- Configurable magnetometer data rates for compass applications
- Adjustable sample rates from 1Hz to 1000Hz

### Real-time Visualization

The GUI provides real-time plotting with:

- Separate plots for each sensor type
- Automatic scaling and grid lines
- Color-coded X, Y, Z axes
- Live update during streaming

### Data Export

CSV files include:

- Timestamp from ESP32 (milliseconds)
- System timestamp (Python time)
- All sensor data with full precision
- Temperature measurements
- Configuration metadata

## Technical Specifications

### Performance

- Maximum sample rate: 1000Hz
- Data precision: 6 decimal places for IMU data
- Temperature precision: 2 decimal places
- Real-time plotting: Up to 100 points displayed
- Data storage: Limited by available system memory

### Compatibility

- ESP32 platforms: NodeMCU ESP-32S, ESP32 DevKit, etc.
- Python versions: 3.6 and above
- Operating systems: Windows, macOS, Linux
- Communication: USB Serial, Bluetooth Serial

This system provides a complete solution for configurable ICM20948 sensor operation with real-time monitoring and data logging capabilities.
