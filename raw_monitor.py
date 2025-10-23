#!/usr/bin/env python3
"""
Raw serial monitor to see if anything is coming from ESP32
"""

import serial
import time

def raw_serial_monitor():
    try:
        print("Opening COM3...")
        ser = serial.Serial('COM3', 115200, timeout=1)
        print("Serial port opened. Monitoring for 10 seconds...")
        print("Press Ctrl+C to stop early")
        print("-" * 50)
        
        start_time = time.time()
        data_received = False
        
        try:
            while time.time() - start_time < 10:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    try:
                        text = data.decode('utf-8', errors='ignore')
                        print(f"Received: {repr(text)}")
                        data_received = True
                    except:
                        print(f"Raw bytes: {data}")
                        data_received = True
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            
        if not data_received:
            print("No data received in 10 seconds")
            print("\nTrying to send a simple command...")
            ser.write(b'\r\n')
            ser.flush()
            time.sleep(1)
            
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"Response to newline: {data}")
            else:
                print("Still no response")
        
        ser.close()
        print("Serial monitor closed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    raw_serial_monitor()