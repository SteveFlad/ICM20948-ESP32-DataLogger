#!/usr/bin/env python3
"""
Quick COM port availability test
"""

import serial
import time

def test_port_availability():
    print("Testing COM3 availability...")
    
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}/3...")
            ser = serial.Serial('COM3', 115200, timeout=1)
            print("✅ COM3 opened successfully!")
            
            # Quick test
            time.sleep(1)
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"📨 Received: {data.decode('utf-8', errors='ignore')}")
            
            ser.close()
            print("✅ Test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retry
    
    print("\n🔧 Troubleshooting:")
    print("1. Close Arduino IDE Serial Monitor")
    print("2. Or completely close Arduino IDE")
    print("3. Make sure no other programs are using COM3")
    return False

if __name__ == "__main__":
    test_port_availability()