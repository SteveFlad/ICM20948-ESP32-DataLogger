#!/usr/bin/env python3
"""
Bluetooth COM Port Investigation Tool
Tests COM4 and COM6 to see what Bluetooth devices they're connected to
"""

import serial
import serial.tools.list_ports
import time
import threading

class BluetoothComTester:
    def __init__(self):
        self.test_results = {}
        
    def test_com_port(self, port, timeout=5):
        """Test a specific COM port for Bluetooth communication"""
        print(f"\n{'='*50}")
        print(f"Testing {port}...")
        print(f"{'='*50}")
        
        try:
            # Try to open the port
            ser = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=1,
                write_timeout=2
            )
            
            print(f"✓ Successfully opened {port}")
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Listen for any incoming data
            print("Listening for incoming data...")
            data_received = False
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    try:
                        data = ser.read(ser.in_waiting)
                        text = data.decode('utf-8', errors='ignore')
                        print(f"📡 Received: {repr(text)}")
                        data_received = True
                    except Exception as e:
                        print(f"🔴 Decode error: {e}")
                        
                time.sleep(0.1)
            
            if not data_received:
                print("🔇 No incoming data detected")
                
            # Try sending some test commands
            test_commands = [
                b'AT\r\n',           # Standard AT command
                b'HELP\r\n',         # Our ESP32 help command
                b'CONFIG\r\n',       # Our ESP32 config command
                b'SCAN\r\n',         # Our ESP32 scan command
                b'\r\n',             # Simple newline
                b'hello\r\n',        # Simple hello
            ]
            
            print("\nTesting various commands...")
            for cmd in test_commands:
                try:
                    print(f"📤 Sending: {cmd}")
                    ser.write(cmd)
                    ser.flush()
                    
                    # Wait for response
                    time.sleep(0.5)
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting)
                        print(f"📥 Response: {repr(response.decode('utf-8', errors='ignore'))}")
                    else:
                        print("📭 No response")
                        
                except Exception as e:
                    print(f"🔴 Send error: {e}")
                    
            ser.close()
            self.test_results[port] = "Connected but no clear device identification"
            
        except serial.SerialException as e:
            print(f"🔴 Failed to open {port}: {e}")
            self.test_results[port] = f"Failed: {e}"
        except Exception as e:
            print(f"🔴 Unexpected error with {port}: {e}")
            self.test_results[port] = f"Error: {e}"
    
    def test_esp32_bluetooth_discovery(self):
        """Try to discover if our ESP32 ICM20948 device is available via Bluetooth"""
        print(f"\n{'='*60}")
        print("ESP32 ICM20948 Bluetooth Discovery")
        print(f"{'='*60}")
        
        # Check if our ESP32 is advertising Bluetooth
        print("Note: Your ESP32 should be programmed with Bluetooth enabled")
        print("Device name should be: 'ESP32_ICM20948_Config'")
        print("\nTo pair your ESP32:")
        print("1. Make sure ESP32 is powered and running our firmware")
        print("2. Go to Windows Settings → Devices → Bluetooth")
        print("3. Look for 'ESP32_ICM20948_Config' in available devices")
        print("4. Pair the device")
        print("5. Note which COM port gets assigned")
        
    def run_full_test(self):
        """Run complete Bluetooth COM port investigation"""
        print("🔍 Bluetooth COM Port Investigation Tool")
        print(f"{'='*60}")
        
        # Get list of all COM ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        print(f"Found COM ports: {ports}")
        
        # Test Bluetooth COM ports specifically
        bluetooth_ports = ['COM4', 'COM6']
        
        for port in bluetooth_ports:
            if port in ports:
                self.test_com_port(port)
            else:
                print(f"\n{port} not available")
                self.test_results[port] = "Not available"
        
        # Show summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        for port, result in self.test_results.items():
            print(f"{port}: {result}")
            
        self.test_esp32_bluetooth_discovery()

def main():
    tester = BluetoothComTester()
    tester.run_full_test()
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print("1. If no devices responded, pair your ESP32 via Windows Bluetooth settings")
    print("2. Look for 'ESP32_ICM20948_Config' device name")
    print("3. Once paired, note the new COM port that appears")
    print("4. Modify your ICM20948_Controller.py to use that COM port")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()