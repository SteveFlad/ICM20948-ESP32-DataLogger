#!/usr/bin/env python3
"""
ESP32 Simulator for testing the GUI when hardware isn't available
This simulates the ESP32 responses so you can test the improved GUI
"""

import socket
import threading
import time
import random
import math

class ESP32Simulator:
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.running = False
        self.streaming = False
        self.server_socket = None
        self.client_socket = None
        
        # Simulated sensor configuration
        self.config = {
            'accel_range': 1,  # ±4g
            'gyro_range': 0,   # ±250°/s  
            'mag_rate': 2,     # 10Hz
            'sample_rate': 100,
            'enable_accel': True,
            'enable_gyro': True,
            'enable_mag': True,
            'enable_temp': True
        }
        
    def start_server(self):
        """Start the TCP server to simulate serial communication"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            print(f"ESP32 Simulator listening on {self.host}:{self.port}")
            print("Modify your Python GUI to connect to 'socket://localhost:9090' instead of COM3")
            print("-" * 60)
            
            self.running = True
            
            while self.running:
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    print(f"Client connected from {addr}")
                    self.send_startup_messages()
                    self.handle_client()
                except Exception as e:
                    if self.running:
                        print(f"Connection error: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
            
    def send_startup_messages(self):
        """Send initial startup messages like the real ESP32"""
        messages = [
            "ICM20948 Configurable Data Logger",
            "I2C initialized", 
            "Scanning I2C bus...",
            "I2C device found at address 0x69!",
            "Found 1 device(s)",
            "Initializing ICM20948...",
            "ICM20948 found at address 0x69",
            "Configuration applied successfully",
            "Ready! Type HELP for commands",
            self.get_config_string()
        ]
        
        for msg in messages:
            self.send_message(msg)
            time.sleep(0.1)
            
    def send_message(self, message):
        """Send a message to the client"""
        if self.client_socket:
            try:
                self.client_socket.send((message + '\n').encode('utf-8'))
            except:
                pass
                
    def get_config_string(self):
        """Generate CONFIG response"""
        return f"CONFIG:ACCEL_RANGE={self.config['accel_range']},GYRO_RANGE={self.config['gyro_range']},MAG_RATE={self.config['mag_rate']},SAMPLE_RATE={self.config['sample_rate']},EN_ACCEL={int(self.config['enable_accel'])},EN_GYRO={int(self.config['enable_gyro'])},EN_MAG={int(self.config['enable_mag'])},EN_TEMP={int(self.config['enable_temp'])},STREAMING={int(self.streaming)}"
        
    def generate_sensor_data(self):
        """Generate realistic sensor data"""
        timestamp = int(time.time() * 1000) % 1000000
        
        # Simulate accelerometer (with gravity and some noise)
        ax = 0.0 + random.uniform(-0.5, 0.5)  # X axis
        ay = 0.0 + random.uniform(-0.5, 0.5)  # Y axis  
        az = 9.81 + random.uniform(-0.5, 0.5) # Z axis (gravity)
        
        # Simulate gyroscope (mostly zero with small drift)
        gx = random.uniform(-0.1, 0.1)
        gy = random.uniform(-0.1, 0.1)
        gz = random.uniform(-0.1, 0.1)
        
        # Simulate magnetometer (Earth's magnetic field with noise)
        mx = 25.0 + random.uniform(-5, 5)
        my = 15.0 + random.uniform(-5, 5)
        mz = -40.0 + random.uniform(-5, 5)
        
        # Simulate temperature
        temp = 22.5 + random.uniform(-2, 2)
        
        return f"DATA:{timestamp},{ax:.3f},{ay:.3f},{az:.3f},{gx:.3f},{gy:.3f},{gz:.3f},{mx:.3f},{my:.3f},{mz:.3f},{temp:.1f}"
        
    def handle_client(self):
        """Handle client commands"""
        data_thread = None
        
        try:
            while self.running and self.client_socket:
                try:
                    data = self.client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                        
                    print(f"Received command: {data}")
                    self.process_command(data)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Client handling error: {e}")
                    break
                    
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            print("Client disconnected")
            
    def process_command(self, command):
        """Process incoming commands"""
        command = command.upper().strip()
        
        if command == "SCAN":
            self.send_message("DEBUG: SCAN command received")
            self.send_message("Scanning I2C bus...")
            self.send_message("I2C device found at address 0x69!")
            self.send_message("Found 1 device(s)")
            
        elif command == "CONFIG":
            self.send_message("DEBUG: CONFIG command received")
            self.send_message(self.get_config_string())
            
        elif command == "START":
            self.send_message("DEBUG: START command received")
            self.streaming = True
            self.send_message("Started streaming")
            # Start data streaming thread
            threading.Thread(target=self.stream_data, daemon=True).start()
            
        elif command == "STOP":
            self.send_message("DEBUG: STOP command received")
            self.streaming = False
            self.send_message("Stopped streaming")
            
        elif command == "HELP":
            help_lines = [
                "Available commands:",
                "  SCAN - Scan I2C bus",
                "  CONFIG - Show current configuration", 
                "  START - Start data streaming",
                "  STOP - Stop data streaming",
                "  HELP - Show this help"
            ]
            for line in help_lines:
                self.send_message(line)
                
        else:
            self.send_message(f"Unknown command: {command} (Type HELP for commands)")
            
    def stream_data(self):
        """Stream sensor data while streaming is enabled"""
        interval = 1.0 / self.config['sample_rate']  # Convert Hz to seconds
        
        while self.streaming and self.running and self.client_socket:
            try:
                data = self.generate_sensor_data()
                self.send_message(data)
                time.sleep(interval)
            except Exception as e:
                print(f"Streaming error: {e}")
                break
                
    def stop(self):
        """Stop the simulator"""
        self.running = False
        self.streaming = False
        if self.server_socket:
            self.server_socket.close()

def main():
    simulator = ESP32Simulator()
    
    try:
        simulator.start_server()
    except KeyboardInterrupt:
        print("\nShutting down simulator...")
        simulator.stop()

if __name__ == "__main__":
    main()