import serial
import time

# Simple serial test
try:
    print("Opening COM3...")
    ser = serial.Serial('COM3', 115200, timeout=2)
    time.sleep(2)
    
    print("Port info:")
    print(f"  Port: {ser.port}")
    print(f"  Baudrate: {ser.baudrate}")
    print(f"  Is open: {ser.is_open}")
    print(f"  Timeout: {ser.timeout}")
    
    # Clear any existing data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("\nListening for startup messages...")
    start_time = time.time()
    while time.time() - start_time < 5:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(f"Received: {data}")
    
    print(f"\nBytes waiting: {ser.in_waiting}")
    
    # Try sending HELP command
    print("\nSending HELP command...")
    ser.write(b'HELP\r\n')
    ser.flush()
    
    # Wait for response
    print("Waiting for response...")
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(f"Response: {data}")
        time.sleep(0.1)
    
    print(f"Final bytes waiting: {ser.in_waiting}")
    
    # Try sending START command
    print("\nSending START command...")
    ser.write(b'START\r\n')
    ser.flush()
    
    # Wait for response
    print("Waiting for START response...")
    start_time = time.time()
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(f"START Response: {data}")
        time.sleep(0.1)
    
    print("Test complete.")
    ser.close()
    
except Exception as e:
    print(f"Error: {e}")
    
input("Press Enter to exit...")