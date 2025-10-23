#!/usr/bin/env python3
"""
ESP32 Bluetooth Communication Test
Test communication with the paired ESP32_BNO055 on COM4
"""

import serial
import time

def test_esp32_bluetooth():
    """Test communication with ESP32 via Bluetooth on COM4"""
    print("🔍 Testing ESP32 Bluetooth Communication on COM4")
    print("=" * 60)
    
    try:
        print("📱 Opening Bluetooth connection to ESP32_BNO055...")
        
        # Try different baud rates - Bluetooth devices sometimes use different rates
        baud_rates = [115200, 9600, 38400, 57600]
        
        for baud in baud_rates:
            print(f"\n🔄 Trying baud rate: {baud}")
            
            try:
                ser = serial.Serial(
                    port='COM4',
                    baudrate=baud,
                    timeout=2,
                    write_timeout=2
                )
                
                print(f"✅ Connected at {baud} baud")
                
                # Clear buffers
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(1)
                
                print("👂 Listening for startup messages...")
                start_time = time.time()
                received_data = False
                
                # Listen for any automatic data
                while time.time() - start_time < 3:
                    if ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting())
                        try:
                            text = data.decode('utf-8', errors='ignore').strip()
                            if text:
                                print(f"📨 Received: {text}")
                                received_data = True
                        except:
                            print(f"📨 Raw data: {data}")
                            received_data = True
                    time.sleep(0.1)
                
                if not received_data:
                    print("🔇 No automatic data received")
                
                # Try sending commands
                print("\n📤 Testing commands...")
                test_commands = [
                    'HELP\r\n',
                    'CONFIG\r\n', 
                    'SCAN\r\n',
                    'AT\r\n',
                    '\r\n'
                ]
                
                for cmd in test_commands:
                    print(f"📤 Sending: {repr(cmd)}")
                    ser.write(cmd.encode())
                    ser.flush()
                    
                    time.sleep(1)
                    
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting())
                        try:
                            text = response.decode('utf-8', errors='ignore').strip()
                            print(f"📥 Response: {text}")
                        except:
                            print(f"📥 Raw response: {response}")
                    else:
                        print("📭 No response")
                
                ser.close()
                print(f"\n✅ Test completed for {baud} baud")
                break  # If we got this far, this baud rate works
                
            except serial.SerialException as e:
                print(f"❌ Failed at {baud} baud: {e}")
                continue
                
    except Exception as e:
        print(f"🔴 General error: {e}")

def check_bluetooth_status():
    """Check the current Bluetooth connection status"""
    print("\n🔍 Checking Bluetooth Status")
    print("=" * 40)
    
    try:
        import subprocess
        result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                              capture_output=True, text=True)
        print("Network interfaces:")
        print(result.stdout)
    except:
        print("Could not check network interfaces")

def main():
    """Main function"""
    print("🎯 ESP32 Bluetooth Communication Tester")
    print("=" * 60)
    print("Target: ESP32_BNO055 on COM4")
    print("Note: Make sure the ESP32 is powered on and Bluetooth is active")
    print("=" * 60)
    
    test_esp32_bluetooth()
    
    print("\n" + "=" * 60)
    print("📋 Analysis:")
    print("• If connection works: You can use COM4 for wireless communication")
    print("• If no response: The ESP32 might not be running the expected firmware")
    print("• If connection fails: The Bluetooth pairing might need to be refreshed")
    print("=" * 60)

if __name__ == "__main__":
    main()