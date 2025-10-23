#!/usr/bin/env python3
"""
Test script to verify the improved GUI performance optimizations
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
import serial
import serial.tools.list_ports

class SimpleICMTester:
    def __init__(self, root):
        self.root = root
        self.root.title("ICM20948 Connection Tester")
        self.root.geometry("800x400")
        
        # Serial connection
        self.serial_connection = None
        self.connected = False
        self.streaming = False
        self.data_queue = queue.Queue()
        
        self.create_widgets()
        self.update_port_list()
        
    def create_widgets(self):
        # Connection frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection Test")
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Port selection
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, padx=5, pady=2)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(conn_frame, text="Refresh", command=self.update_port_list).grid(row=0, column=2, padx=5, pady=2)
        
        # Connect button
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=1, column=1, padx=5, pady=5)
        
        # Test buttons
        test_frame = ttk.LabelFrame(self.root, text="Communication Test")
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(test_frame, text="SCAN", command=lambda: self.send_command("SCAN")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(test_frame, text="CONFIG", command=lambda: self.send_command("CONFIG")).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Streaming test
        stream_frame = ttk.LabelFrame(self.root, text="Streaming Test")
        stream_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_btn = ttk.Button(stream_frame, text="START", command=self.start_streaming)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(stream_frame, text="STOP", command=self.stop_streaming, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.data_count_label = ttk.Label(stream_frame, text="Data points: 0")
        self.data_count_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Console
        console_frame = ttk.LabelFrame(self.root, text="Console Output")
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.console_text = tk.Text(console_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.data_count = 0
        
    def update_port_list(self):
        """Update the list of available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
        
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.connected:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        """Connect to selected port"""
        port = self.port_var.get()
        if not port:
            self.console_print("No port selected")
            return
            
        try:
            self.console_print(f"Connecting to {port}...")
            
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=0.5,
                write_timeout=1.0
            )
            
            if not self.serial_connection.is_open:
                raise Exception("Failed to open serial port")
                
            time.sleep(2)  # Wait for connection
            
            self.connected = True
            self.connect_btn.config(text="Disconnect")
            self.status_label.config(text="Connected", foreground="green")
            
            # Start reading thread
            self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.reading_thread.start()
            
            # Start data processing
            self.process_serial_data()
            
            self.console_print(f"Connected to {port}")
            
        except Exception as e:
            self.console_print(f"Connection failed: {e}")
            
    def disconnect(self):
        """Disconnect from serial port"""
        self.connected = False
        self.streaming = False
        
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except:
                pass
            self.serial_connection = None
            
        self.connect_btn.config(text="Connect")
        self.status_label.config(text="Disconnected", foreground="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        self.console_print("Disconnected")
        
    def send_command(self, command):
        """Send command to ESP32"""
        if not self.connected:
            self.console_print("Not connected!")
            return
            
        try:
            self.console_print(f"Sending: {command}")
            command_bytes = (command + '\r\n').encode('utf-8')
            self.serial_connection.write(command_bytes)
            self.serial_connection.flush()
            
        except Exception as e:
            self.console_print(f"Send error: {e}")
            
    def start_streaming(self):
        """Start data streaming"""
        if not self.connected:
            self.console_print("Not connected!")
            return
            
        self.console_print("Starting streaming...")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        def start_thread():
            try:
                self.send_command("START")
                self.streaming = True
                self.root.after(10, lambda: self.console_print("Streaming started"))
            except Exception as e:
                self.root.after(10, lambda: self.console_print(f"Start error: {e}"))
                
        threading.Thread(target=start_thread, daemon=True).start()
        
    def stop_streaming(self):
        """Stop data streaming"""
        self.console_print("Stopping streaming...")
        self.streaming = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        def stop_thread():
            try:
                self.send_command("STOP")
                self.root.after(10, lambda: self.console_print("Streaming stopped"))
            except Exception as e:
                self.root.after(10, lambda: self.console_print(f"Stop error: {e}"))
                
        threading.Thread(target=stop_thread, daemon=True).start()
        
    def read_serial_data(self):
        """Read data from serial port"""
        while self.connected and self.serial_connection:
            try:
                time.sleep(0.02)  # 20ms sleep
                
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    raw_line = self.serial_connection.readline()
                    if raw_line:
                        try:
                            line = raw_line.decode('utf-8').strip()
                        except UnicodeDecodeError:
                            line = raw_line.decode('latin-1').strip()
                            
                        if line and len(line) > 0:
                            if self.data_queue.qsize() < 100:
                                self.data_queue.put(line)
                                
            except Exception as e:
                if self.connected:
                    self.console_print(f"Read error: {e}")
                break
                
    def process_serial_data(self):
        """Process received data"""
        try:
            message_count = 0
            while not self.data_queue.empty() and message_count < 5:
                line = self.data_queue.get_nowait()
                message_count += 1
                
                if line.startswith("DATA:"):
                    self.data_count += 1
                    if self.data_count % 10 == 0:  # Show every 10th data point
                        self.console_print(f"Data point #{self.data_count}")
                        self.data_count_label.config(text=f"Data points: {self.data_count}")
                else:
                    self.console_print(f"Received: {line}")
                    
        except queue.Empty:
            pass
        except Exception as e:
            self.console_print(f"Process error: {e}")
            
        if self.connected:
            interval = 200 if self.streaming else 100
            self.root.after(interval, self.process_serial_data)
            
    def console_print(self, message):
        """Print to console"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.console_text.insert(tk.END, formatted_message)
        self.console_text.see(tk.END)
        
        # Limit console size
        lines = int(self.console_text.index('end-1c').split('.')[0])
        if lines > 50:
            self.console_text.delete("1.0", "11.0")

def main():
    root = tk.Tk()
    app = SimpleICMTester(root)
    
    def on_closing():
        if app.connected:
            app.disconnect()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()