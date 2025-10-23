#!/usr/bin/env python3
"""
Simple serial test to check if ESP32 is responding
"""

import serial
import time

def test_esp32_communication():
    try:
        print("Testing ESP32 communication on COM3...")
        
        # Open serial connection
        ser = serial.Serial(
            port='COM3',
            baudrate=115200,
            timeout=2
        )
        
        print("Serial port opened successfully")
        time.sleep(2)  # Wait for ESP32 to boot
        
        # Clear buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print("Sending HELP command...")
        ser.write(b'HELP\r\n')
        ser.flush()
        
        print("Waiting for response...")
        start_time = time.time()
        response_received = False
        
        while time.time() - start_time < 5:  # Wait up to 5 seconds
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Received: {line}")
                    response_received = True
                    
        if not response_received:
            print("No response received - ESP32 may not be running the correct firmware")
            
        # Try sending other commands
        print("\nSending SCAN command...")
        ser.write(b'SCAN\r\n')
        ser.flush()
        
        time.sleep(2)
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"Received: {line}")
        
        ser.close()
        print("\nTest completed")
        
    except Exception as e:
        print(f"Communication test failed: {e}")

if __name__ == "__main__":
    test_esp32_communication()