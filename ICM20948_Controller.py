import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import csv
import queue
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ICM20948Controller:
    def __init__(self, root):
        self.root = root
        self.root.title("ICM20948 Parameter Controller")
        self.root.geometry("1200x900")
        
        # Serial connection
        self.serial_connection = None
        self.connected = False
        self.data_queue = queue.Queue()
        self.streaming = False
        
        # Data storage
        self.data_log = []
        self.max_plot_points = 500
        self.last_plot_update = 0  # Rate limiting for plot updates
        
        # Configuration mappings
        self.accel_ranges = {
            0: "±2g", 1: "±4g", 2: "±8g", 3: "±16g"
        }
        self.gyro_ranges = {
            0: "±250°/s", 1: "±500°/s", 2: "±1000°/s", 3: "±2000°/s"
        }
        self.mag_rates = {
            0: "Shutdown", 1: "Single", 2: "10Hz", 3: "20Hz", 
            4: "50Hz", 5: "100Hz", 6: "200Hz", 7: "1Hz", 8: "Reserved"
        }
        
        self.create_widgets()
        self.update_port_list()
        
    def create_widgets(self):
        # Create main frame with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Connection tab
        self.conn_frame = ttk.Frame(notebook)
        notebook.add(self.conn_frame, text="Connection")
        self.create_connection_widgets()
        
        # Configuration tab
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="Configuration")
        self.create_config_widgets()
        
        # Data Monitoring tab
        self.monitor_frame = ttk.Frame(notebook)
        notebook.add(self.monitor_frame, text="Data Monitor")
        self.create_monitor_widgets()
        
        # Data Logging tab
        self.log_frame = ttk.Frame(notebook)
        notebook.add(self.log_frame, text="Data Logging")
        self.create_logging_widgets()
        
    def create_connection_widgets(self):
        # Port selection
        port_frame = ttk.LabelFrame(self.conn_frame, text="Serial Connection")
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(port_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(port_frame, text="Refresh", command=self.update_port_list).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(port_frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.baud_var = tk.StringVar(value="115200")
        baud_combo = ttk.Combobox(port_frame, textvariable=self.baud_var, 
                                  values=["9600", "57600", "115200", "230400"], width=15)
        baud_combo.grid(row=1, column=1, padx=5, pady=2)
        
        self.connect_btn = ttk.Button(port_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        self.status_label = ttk.Label(port_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Console output
        console_frame = ttk.LabelFrame(self.conn_frame, text="Console Output")
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, height=15, width=80)
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_config_widgets(self):
        # Parameter configuration
        param_frame = ttk.LabelFrame(self.config_frame, text="Sensor Parameters")
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Accelerometer range
        ttk.Label(param_frame, text="Accelerometer Range:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.accel_range_var = tk.IntVar(value=1)
        accel_combo = ttk.Combobox(param_frame, textvariable=self.accel_range_var, 
                                   values=list(range(4)), width=20)
        accel_combo.grid(row=0, column=1, padx=5, pady=2)
        accel_label = ttk.Label(param_frame, text="0=±2g, 1=±4g, 2=±8g, 3=±16g")
        accel_label.grid(row=0, column=3, padx=5, pady=2)
        ttk.Button(param_frame, text="Set", 
                  command=lambda: self.send_command(f"SET_ACCEL_RANGE={self.accel_range_var.get()}")).grid(row=0, column=2, padx=5, pady=2)
        
        # Gyroscope range
        ttk.Label(param_frame, text="Gyroscope Range:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.gyro_range_var = tk.IntVar(value=0)
        gyro_combo = ttk.Combobox(param_frame, textvariable=self.gyro_range_var,
                                  values=list(range(4)), width=20)
        gyro_combo.grid(row=1, column=1, padx=5, pady=2)
        gyro_label = ttk.Label(param_frame, text="0=±250°/s, 1=±500°/s, 2=±1000°/s, 3=±2000°/s")
        gyro_label.grid(row=1, column=3, padx=5, pady=2)
        ttk.Button(param_frame, text="Set",
                  command=lambda: self.send_command(f"SET_GYRO_RANGE={self.gyro_range_var.get()}")).grid(row=1, column=2, padx=5, pady=2)
        
        # Magnetometer data rate
        ttk.Label(param_frame, text="Magnetometer Rate:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.mag_rate_var = tk.IntVar(value=2)
        mag_combo = ttk.Combobox(param_frame, textvariable=self.mag_rate_var,
                                 values=list(range(9)), width=20)
        mag_combo.grid(row=2, column=1, padx=5, pady=2)
        mag_label = ttk.Label(param_frame, text="0=Off, 1=Single, 2=10Hz, 3=20Hz, 4=50Hz, 5=100Hz, 6=200Hz")
        mag_label.grid(row=2, column=3, padx=5, pady=2)
        ttk.Button(param_frame, text="Set",
                  command=lambda: self.send_command(f"SET_MAG_RATE={self.mag_rate_var.get()}")).grid(row=2, column=2, padx=5, pady=2)
        
        # Sample rate
        ttk.Label(param_frame, text="Sample Rate (Hz):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.sample_rate_var = tk.IntVar(value=100)
        sample_spin = tk.Spinbox(param_frame, from_=1, to=1000, textvariable=self.sample_rate_var, width=18)
        sample_spin.grid(row=3, column=1, padx=5, pady=2)
        ttk.Button(param_frame, text="Set",
                  command=lambda: self.send_command(f"SET_SAMPLE_RATE={self.sample_rate_var.get()}")).grid(row=3, column=2, padx=5, pady=2)
        
        # Sensor enables
        enable_frame = ttk.LabelFrame(self.config_frame, text="Sensor Enable/Disable")
        enable_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.enable_accel_var = tk.BooleanVar(value=True)
        self.enable_gyro_var = tk.BooleanVar(value=True)
        self.enable_mag_var = tk.BooleanVar(value=True)
        self.enable_temp_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(enable_frame, text="Accelerometer", variable=self.enable_accel_var,
                      command=lambda: self.send_command(f"ENABLE_ACCEL={int(self.enable_accel_var.get())}")).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Checkbutton(enable_frame, text="Gyroscope", variable=self.enable_gyro_var,
                      command=lambda: self.send_command(f"ENABLE_GYRO={int(self.enable_gyro_var.get())}")).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Checkbutton(enable_frame, text="Magnetometer", variable=self.enable_mag_var,
                      command=lambda: self.send_command(f"ENABLE_MAG={int(self.enable_mag_var.get())}")).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Checkbutton(enable_frame, text="Temperature", variable=self.enable_temp_var,
                      command=lambda: self.send_command(f"ENABLE_TEMP={int(self.enable_temp_var.get())}")).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Quick presets
        preset_frame = ttk.LabelFrame(self.config_frame, text="Quick Presets")
        preset_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(preset_frame, text="Golf Swing (High G)", command=self.preset_golf_swing).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(preset_frame, text="Slow Motion (Low G)", command=self.preset_slow_motion).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(preset_frame, text="Balanced", command=self.preset_balanced).pack(side=tk.LEFT, padx=5, pady=5)
        
    def create_monitor_widgets(self):
        # Streaming controls
        stream_frame = ttk.LabelFrame(self.monitor_frame, text="Data Streaming")
        stream_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_btn = ttk.Button(stream_frame, text="Start Streaming", command=self.start_streaming)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(stream_frame, text="Stop Streaming", command=self.stop_streaming)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(stream_frame, text="Clear Data", command=self.clear_data).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Real-time plot
        plot_frame = ttk.LabelFrame(self.monitor_frame, text="Real-time Data Plot")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fig = Figure(figsize=(12, 6), dpi=80)
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize plot data
        self.time_data = []
        self.accel_data = {'x': [], 'y': [], 'z': []}
        self.gyro_data = {'x': [], 'y': [], 'z': []}
        self.mag_data = {'x': [], 'y': [], 'z': []}
        self.temp_data = []
        
    def create_logging_widgets(self):
        # Logging controls
        log_control_frame = ttk.LabelFrame(self.log_frame, text="Data Logging Controls")
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(log_control_frame, text="Enable Logging", variable=self.log_enabled_var).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(log_control_frame, text="Select Log File", command=self.select_log_file).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(log_control_frame, text="Export Current Data", command=self.export_data).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.log_file_label = ttk.Label(log_control_frame, text="No log file selected")
        self.log_file_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Data summary
        summary_frame = ttk.LabelFrame(self.log_frame, text="Data Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.data_count_label = ttk.Label(summary_frame, text="Data points: 0")
        self.data_count_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.logging_status_label = ttk.Label(summary_frame, text="Logging: Disabled")
        self.logging_status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
    def update_port_list(self):
        """Update the list of available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
    
    def toggle_connection(self):
        """Toggle serial connection"""
        if not self.connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """Connect to serial port"""
        try:
            port = self.port_var.get()
            baud = int(self.baud_var.get())
            
            self.console_print(f"Attempting to connect to {port} at {baud} baud...")
            
            # First, ensure any existing connection is properly closed
            if self.serial_connection:
                try:
                    self.serial_connection.close()
                    time.sleep(0.5)  # Give time for port to be released
                except:
                    pass
                self.serial_connection = None
            
            # Create serial connection with proper timeouts
            self.serial_connection = serial.Serial(
                port=port,                                
                baudrate=baud, 
                timeout=1,           # Read timeout
                write_timeout=2,     # Write timeout 
                bytesize=8,
                parity='N',
                stopbits=1
            )
            
            # Verify connection is open
            if not self.serial_connection.is_open:
                raise Exception("Failed to open serial port")
            
            # Clear any existing data
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
            time.sleep(2)  # Wait for connection to establish
            
            self.connected = True
            self.connect_btn.config(text="Disconnect")
            self.status_label.config(text="Connected", foreground="green")
            
            # Start reading thread
            self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.reading_thread.start()
            
            # Start data processing loop
            self.process_serial_data()
            
            self.console_print(f"Connected to {port} at {baud} baud")
            
            # Request initial configuration after a delay
            self.root.after(1000, lambda: self.send_command("CONFIG"))
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.console_print(f"Connection failed: {str(e)}")
            self.connected = False
            if self.serial_connection:
                try:
                    self.serial_connection.close()
                except:
                    pass
                self.serial_connection = None
    
    def disconnect(self):
        """Disconnect from serial port"""
        self.console_print("Disconnecting...")
        self.connected = False
        
        # Wait for reading thread to stop
        if hasattr(self, 'reading_thread') and self.reading_thread.is_alive():
            self.console_print("Waiting for reading thread to stop...")
            time.sleep(0.5)
        
        if self.serial_connection:
            try:
                self.serial_connection.close()
                self.console_print("Serial connection closed")
            except Exception as e:
                self.console_print(f"Error closing serial: {e}")
            finally:
                self.serial_connection = None
        
        self.connect_btn.config(text="Connect")
        self.status_label.config(text="Disconnected", foreground="red")
        self.console_print("Disconnected")
    
    def test_connection(self):
        """Test if connection is working by checking basic properties"""
        if not self.connected or not self.serial_connection:
            self.console_print("Not connected!")
            return
            
        try:
            self.console_print(f"Port: {self.serial_connection.port}")
            self.console_print(f"Baudrate: {self.serial_connection.baudrate}")
            self.console_print(f"Is open: {self.serial_connection.is_open}")
            self.console_print(f"Bytes waiting: {self.serial_connection.in_waiting}")
            self.console_print(f"Timeout: {self.serial_connection.timeout}")
            
            # Try to send a simple character and wait longer
            self.console_print("Sending test character...")
            self.serial_connection.write(b'\r\n')
            self.serial_connection.flush()
            
            # Wait longer and check multiple times
            for i in range(10):
                time.sleep(0.5)
                waiting = self.serial_connection.in_waiting
                self.console_print(f"Bytes waiting after {(i+1)*0.5}s: {waiting}")
                if waiting > 0:
                    # Try to read what's there
                    data = self.serial_connection.read(waiting)
                    self.console_print(f"Received data: {data}")
                    break
            
            # Try sending a specific command
            self.console_print("Sending HELP command for test...")
            self.serial_connection.write(b'HELP\r\n')
            self.serial_connection.flush()
            
            time.sleep(2)
            waiting = self.serial_connection.in_waiting
            self.console_print(f"Bytes waiting after HELP: {waiting}")
            if waiting > 0:
                data = self.serial_connection.read(waiting)
                self.console_print(f"HELP response: {data}")
            
        except Exception as e:
            self.console_print(f"Connection test failed: {str(e)}")
    
    def send_command(self, command):
        """Send command to ESP32"""
        if not self.connected or not self.serial_connection:
            messagebox.showwarning("Not Connected", "Please connect to a device first")
            return
        
        try:
            self.console_print(f"=== SENDING COMMAND: {command} ===")
            
            # Check if port is still open
            if not self.serial_connection.is_open:
                self.console_print("Serial port is closed. Attempting to reconnect...")
                self.disconnect()
                return
            
            # Clear any pending input before sending command
            try:
                if self.serial_connection.in_waiting > 0:
                    waiting_bytes = self.serial_connection.in_waiting
                    self.console_print(f"Clearing {waiting_bytes} waiting bytes...")
                    self.serial_connection.reset_input_buffer()
            except Exception as buffer_error:
                self.console_print(f"Buffer clear error: {buffer_error}")
            
            # Send command with proper encoding and termination
            command_bytes = (command + '\r\n').encode('utf-8')
            self.console_print(f"Sending {len(command_bytes)} bytes: {command_bytes}")
            
            # Use write timeout to prevent hanging
            old_timeout = self.serial_connection.write_timeout
            self.serial_connection.write_timeout = 1.0  # 1 second write timeout
            
            bytes_written = self.serial_connection.write(command_bytes)
            self.serial_connection.flush()  # Ensure data is sent
            
            # Restore original timeout
            self.serial_connection.write_timeout = old_timeout
            
            self.console_print(f"Successfully sent {bytes_written} bytes: {command}")
            
            # Give a moment for the ESP32 to process
            time.sleep(0.1)
            
        except serial.SerialTimeoutException:
            self.console_print(f"Timeout sending command: {command}")
            messagebox.showerror("Timeout Error", f"Timeout sending command: {command}")
        except Exception as e:
            self.console_print(f"Failed to send command '{command}': {str(e)}")
            messagebox.showerror("Communication Error", f"Failed to send command: {str(e)}")
            # If there's a serious error, disconnect
            if "access is denied" in str(e).lower() or "invalid handle" in str(e).lower():
                self.console_print("Port access error detected. Disconnecting...")
                self.disconnect()
    
    def read_serial_data(self):
        """Read data from serial port with improved error handling"""
        while self.connected and self.serial_connection:
            try:
                # Use a longer sleep to prevent excessive CPU usage
                time.sleep(0.02)  # 20ms sleep - less aggressive polling
                
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    try:
                        # Read with timeout to prevent hanging
                        raw_line = self.serial_connection.readline()
                        if raw_line:
                            try:
                                line = raw_line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                # Fallback to latin-1 which can decode any byte sequence
                                line = raw_line.decode('latin-1').strip()
                                if len(self.data_log) % 100 == 0:  # Reduced spam
                                    self.console_print(f"Debug: Received latin-1 data")
                            
                            if line and len(line) > 0:
                                # Use a limited queue size to prevent memory issues
                                if self.data_queue.qsize() < 1000:  # Limit queue size
                                    self.data_queue.put(line)
                                else:
                                    # Queue is full, remove old items
                                    try:
                                        self.data_queue.get_nowait()
                                        self.data_queue.put(line)
                                    except queue.Empty:
                                        pass
                    except Exception as decode_error:
                        # If all else fails, skip this line
                        if len(self.data_log) % 100 == 0:  # Reduced error spam
                            self.console_print(f"Debug: Skipped undecodable data")
                        continue
                        
            except Exception as e:
                if self.connected:
                    self.console_print(f"Read error: {str(e)}")
                    # If we get repeated errors, disconnect to prevent hanging
                    if "access is denied" in str(e).lower():
                        self.console_print("Serial port access error - disconnecting")
                        self.root.after(10, self.disconnect)
                break
        
        self.console_print("Serial reading thread stopped")
    
    def process_serial_data(self):
        """Process received serial data"""
        try:
            data_processed = False
            # Process multiple messages at once but limit to prevent blocking
            message_count = 0
            max_messages_per_cycle = 10  # Limit messages processed per cycle
            
            while not self.data_queue.empty() and message_count < max_messages_per_cycle:
                line = self.data_queue.get_nowait()
                data_processed = True
                message_count += 1
                
                # Only show every 10th data message to reduce console spam
                if line.startswith("DATA:"):
                    if len(self.data_log) % 10 == 0:  # Show every 10th data point
                        self.console_print(f"Processing DATA... (point #{len(self.data_log)})")
                    self.parse_data_line(line)
                elif line.startswith("CONFIG:"):
                    self.console_print("Processing CONFIG line...")
                    self.parse_config_line(line)
                elif line.startswith("DEBUG:"):
                    self.console_print(f"ESP32 Debug: {line}")
                elif line.startswith("I2C device found"):
                    self.console_print(f"I2C Scan: {line}")
                elif "Available commands:" in line or line.startswith("  "):
                    self.console_print(f"Help: {line}")
                elif any(word in line.lower() for word in ["started", "stopped", "applied", "enabled", "disabled", "scanning", "rate set"]):
                    self.console_print(f"ESP32 Status: {line}")
                elif line.strip() == "":
                    # Ignore empty lines
                    pass
                else:
                    # Only show "Unknown format" for truly unexpected lines
                    if len(line.strip()) > 0:  # Don't show for empty lines
                        self.console_print(f"ESP32 Message: {line}")
                    
        except queue.Empty:
            pass
        except Exception as e:
            self.console_print(f"Data processing error: {str(e)}")
        
        # Schedule next update with adaptive timing
        if self.connected:
            # Use longer interval when streaming to prevent GUI blocking
            interval = 200 if self.streaming else 100
            self.root.after(interval, self.process_serial_data)
    
    def parse_data_line(self, line):
        """Parse incoming data line"""
        try:
            # Format: DATA:timestamp,ax,ay,az,gx,gy,gz,mx,my,mz,temp
            parts = line.split(':')[1].split(',')
            
            if len(parts) >= 11:
                timestamp = int(parts[0])
                ax, ay, az = float(parts[1]), float(parts[2]), float(parts[3])
                gx, gy, gz = float(parts[4]), float(parts[5]), float(parts[6])
                mx, my, mz = float(parts[7]), float(parts[8]), float(parts[9])
                temp = float(parts[10])
                
                # Store data
                current_time = time.time()
                data_point = {
                    'timestamp': timestamp,
                    'time': current_time,
                    'accel': {'x': ax, 'y': ay, 'z': az},
                    'gyro': {'x': gx, 'y': gy, 'z': gz},
                    'mag': {'x': mx, 'y': my, 'z': mz},
                    'temp': temp
                }
                
                self.data_log.append(data_point)
                
                # Limit data size to prevent memory issues
                if len(self.data_log) > self.max_plot_points:
                    self.data_log.pop(0)
                
                # Update plots with more aggressive rate limiting (max 5 FPS when streaming)
                current_time = time.time()
                update_interval = 0.2 if self.streaming else 0.1  # 5 FPS when streaming, 10 FPS otherwise
                if current_time - self.last_plot_update > update_interval:
                    # Schedule plot update in next GUI cycle to prevent blocking
                    self.root.after_idle(self.update_plots)
                    self.last_plot_update = current_time
                
                # Log to file if enabled
                if self.log_enabled_var.get() and hasattr(self, 'log_file'):
                    self.write_to_log(data_point)
                
                # Update data count less frequently to reduce GUI overhead
                if len(self.data_log) % 5 == 0:  # Update every 5 data points
                    self.data_count_label.config(text=f"Data points: {len(self.data_log)}")
            else:
                if len(self.data_log) % 50 == 0:  # Only show occasional parsing errors
                    self.console_print(f"Invalid data format - expected 11 parts, got {len(parts)}")
                
        except Exception as e:
            if len(self.data_log) % 50 == 0:  # Only show occasional parsing errors
                self.console_print(f"Data parsing error: {str(e)}")
                self.console_print(f"Problematic line: {line}")
                current_time = time.time()
                if current_time - self.last_plot_update > 0.1:  # 100ms = 10 FPS
                    self.update_plots()
                    self.last_plot_update = current_time
                
                # Log to file if enabled
                if self.log_enabled_var.get() and hasattr(self, 'log_file'):
                    self.write_to_log(data_point)
                
                # Update data count
                self.data_count_label.config(text=f"Data points: {len(self.data_log)}")
            else:
                self.console_print(f"Invalid data format - expected 11 parts, got {len(parts)}")
                
        except Exception as e:
            self.console_print(f"Data parsing error: {str(e)}")
            self.console_print(f"Problematic line: {line}")
    
    def parse_config_line(self, line):
        """Parse configuration response"""
        try:
            # Format: CONFIG:ACCEL_RANGE=1,GYRO_RANGE=0,MAG_RATE=2,SAMPLE_RATE=100,...
            self.console_print(f"Parsing CONFIG line: {line}")
            config_str = line.split(':')[1]
            config_pairs = config_str.split(',')
            self.console_print(f"Found {len(config_pairs)} config parameters")
            
            for pair in config_pairs:
                key, value = pair.split('=')
                if key == "ACCEL_RANGE":
                    self.accel_range_var.set(int(value))
                elif key == "GYRO_RANGE":
                    self.gyro_range_var.set(int(value))
                elif key == "MAG_RATE":
                    self.mag_rate_var.set(int(value))
                elif key == "SAMPLE_RATE":
                    self.sample_rate_var.set(int(value))
                elif key == "EN_ACCEL":
                    self.enable_accel_var.set(bool(int(value)))
                elif key == "EN_GYRO":
                    self.enable_gyro_var.set(bool(int(value)))
                elif key == "EN_MAG":
                    self.enable_mag_var.set(bool(int(value)))
                elif key == "EN_TEMP":
                    self.enable_temp_var.set(bool(int(value)))
            
            self.console_print("✅ Configuration successfully updated from device!")
            
        except Exception as e:
            self.console_print(f"Config parsing error: {str(e)} - Line was: {line}")
    
    def update_plots(self):
        """Update real-time plots with thread safety and performance optimization"""
        if not self.data_log:
            return
        
        try:
            # Extract recent data (use fewer points for better performance)
            recent_data = self.data_log[-30:]  # Only last 30 points for smooth performance
            if len(recent_data) < 2:
                return
                
            times = [d['time'] - recent_data[0]['time'] for d in recent_data]
            
            # Clear plots
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()
            
            # Plot accelerometer data with reduced line complexity
            accel_x = [d['accel']['x'] for d in recent_data]
            accel_y = [d['accel']['y'] for d in recent_data]
            accel_z = [d['accel']['z'] for d in recent_data]
            
            self.ax1.plot(times, accel_x, 'r-', label='X', linewidth=1, alpha=0.8)
            self.ax1.plot(times, accel_y, 'g-', label='Y', linewidth=1, alpha=0.8)
            self.ax1.plot(times, accel_z, 'b-', label='Z', linewidth=1, alpha=0.8)
            self.ax1.set_title('Accelerometer (m/s²)', fontsize=10)
            self.ax1.legend(fontsize=8)
            self.ax1.grid(True, alpha=0.3)
            
            # Plot gyroscope data
            gyro_x = [d['gyro']['x'] for d in recent_data]
            gyro_y = [d['gyro']['y'] for d in recent_data]
            gyro_z = [d['gyro']['z'] for d in recent_data]
            
            self.ax2.plot(times, gyro_x, 'r-', label='X', linewidth=1, alpha=0.8)
            self.ax2.plot(times, gyro_y, 'g-', label='Y', linewidth=1, alpha=0.8)
            self.ax2.plot(times, gyro_z, 'b-', label='Z', linewidth=1, alpha=0.8)
            self.ax2.set_title('Gyroscope (rad/s)', fontsize=10)
            self.ax2.legend(fontsize=8)
            self.ax2.grid(True, alpha=0.3)
            
            # Plot magnetometer data
            mag_x = [d['mag']['x'] for d in recent_data]
            mag_y = [d['mag']['y'] for d in recent_data]
            mag_z = [d['mag']['z'] for d in recent_data]
            
            self.ax3.plot(times, mag_x, 'r-', label='X', linewidth=1, alpha=0.8)
            self.ax3.plot(times, mag_y, 'g-', label='Y', linewidth=1, alpha=0.8)
            self.ax3.plot(times, mag_z, 'b-', label='Z', linewidth=1, alpha=0.8)
            self.ax3.set_title('Magnetometer (µT)', fontsize=10)
            self.ax3.legend(fontsize=8)
            self.ax3.grid(True, alpha=0.3)
            
            # Plot temperature
            temps = [d['temp'] for d in recent_data]
            self.ax4.plot(times, temps, 'orange', linewidth=2, alpha=0.8)
            self.ax4.set_title('Temperature (°C)', fontsize=10)
            self.ax4.grid(True, alpha=0.3)
            
            # Use draw_idle() for non-blocking update
            self.canvas.draw_idle()
            
        except Exception as e:
            # Don't let plot errors crash the GUI, but log less frequently
            if len(self.data_log) % 100 == 0:
                self.console_print(f"Plot update error: {str(e)}")
            pass
    
    def start_streaming(self):
        """Start data streaming (non-blocking)"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to a device first")
            self.console_print("Cannot start streaming - not connected")
            return
            
        self.console_print("Starting data streaming...")
        
        # Update GUI immediately to show responsiveness
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Use threading to prevent GUI freeze
        def start_stream_thread():
            try:
                self.send_command("START")
                self.streaming = True
                # Update GUI elements in main thread
                self.root.after(10, lambda: self.console_print("Streaming started successfully"))
            except Exception as e:
                self.streaming = False
                self.root.after(10, lambda: [
                    self.console_print(f"Error starting stream: {e}"),
                    self.start_btn.config(state="normal"),
                    self.stop_btn.config(state="disabled")
                ])
        
        # Start in separate thread to prevent blocking
        threading.Thread(target=start_stream_thread, daemon=True).start()
        self.console_print("Streaming command initiated...")
    
    def stop_streaming(self):
        """Stop data streaming (non-blocking)"""
        self.console_print("Stopping data streaming...")
        
        # Update GUI immediately to show responsiveness
        self.streaming = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # Use threading to prevent GUI freeze
        def stop_stream_thread():
            try:
                self.send_command("STOP")
                # Update GUI elements in main thread
                self.root.after(10, lambda: self.console_print("Streaming stopped successfully"))
            except Exception as e:
                self.root.after(10, lambda: self.console_print(f"Error stopping stream: {e}"))
        
        # Start in separate thread to prevent blocking
        threading.Thread(target=stop_stream_thread, daemon=True).start()
        self.console_print("Stop command initiated...")
    
    def clear_data(self):
        """Clear all collected data"""
        self.data_log.clear()
        self.data_count_label.config(text="Data points: 0")
        
        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.canvas.draw()
    
    def preset_golf_swing(self):
        """Apply golf swing preset"""
        self.accel_range_var.set(3)  # ±16g
        self.gyro_range_var.set(3)   # ±2000°/s
        self.mag_rate_var.set(5)     # 100Hz
        self.sample_rate_var.set(500) # 500Hz
        
        self.send_command("SET_ACCEL_RANGE=3")
        self.send_command("SET_GYRO_RANGE=3")
        self.send_command("SET_MAG_RATE=5")
        self.send_command("SET_SAMPLE_RATE=500")
        
        self.console_print("Applied golf swing preset")
    
    def preset_slow_motion(self):
        """Apply slow motion preset"""
        self.accel_range_var.set(0)  # ±2g
        self.gyro_range_var.set(0)   # ±250°/s
        self.mag_rate_var.set(2)     # 10Hz
        self.sample_rate_var.set(50) # 50Hz
        
        self.send_command("SET_ACCEL_RANGE=0")
        self.send_command("SET_GYRO_RANGE=0")
        self.send_command("SET_MAG_RATE=2")
        self.send_command("SET_SAMPLE_RATE=50")
        
        self.console_print("Applied slow motion preset")
    
    def preset_balanced(self):
        """Apply balanced preset"""
        self.accel_range_var.set(1)  # ±4g
        self.gyro_range_var.set(1)   # ±500°/s
        self.mag_rate_var.set(3)     # 20Hz
        self.sample_rate_var.set(100) # 100Hz
        
        self.send_command("SET_ACCEL_RANGE=1")
        self.send_command("SET_GYRO_RANGE=1")
        self.send_command("SET_MAG_RATE=3")
        self.send_command("SET_SAMPLE_RATE=100")
        
        self.console_print("Applied balanced preset")
    
    def select_log_file(self):
        """Select log file for data recording"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select log file"
        )
        
        if filename:
            self.log_file = filename
            self.log_file_label.config(text=f"Log file: {filename}")
            
            # Create CSV with headers
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'System_Time', 'Accel_X', 'Accel_Y', 'Accel_Z',
                               'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Temperature'])
    
    def write_to_log(self, data_point):
        """Write data point to log file"""
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data_point['timestamp'],
                    data_point['time'],
                    data_point['accel']['x'], data_point['accel']['y'], data_point['accel']['z'],
                    data_point['gyro']['x'], data_point['gyro']['y'], data_point['gyro']['z'],
                    data_point['mag']['x'], data_point['mag']['y'], data_point['mag']['z'],
                    data_point['temp']
                ])
        except Exception as e:
            self.console_print(f"Logging error: {str(e)}")
    
    def export_data(self):
        """Export current data to file"""
        if not self.data_log:
            messagebox.showwarning("No Data", "No data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export data"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'System_Time', 'Accel_X', 'Accel_Y', 'Accel_Z',
                                   'Gyro_X', 'Gyro_Y', 'Gyro_Z', 'Mag_X', 'Mag_Y', 'Mag_Z', 'Temperature'])
                    
                    for data_point in self.data_log:
                        writer.writerow([
                            data_point['timestamp'],
                            data_point['time'],
                            data_point['accel']['x'], data_point['accel']['y'], data_point['accel']['z'],
                            data_point['gyro']['x'], data_point['gyro']['y'], data_point['gyro']['z'],
                            data_point['mag']['x'], data_point['mag']['y'], data_point['mag']['z'],
                            data_point['temp']
                        ])
                
                messagebox.showinfo("Export Complete", f"Data exported to {filename}")
                self.console_print(f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def console_print(self, message):
        """Print message to console with timestamp - optimized for performance"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
            formatted_message = f"[{timestamp}] {message}\n"
            
            # Use insert and see operations efficiently
            self.console_text.insert(tk.END, formatted_message)
            
            # Only auto-scroll if we're near the bottom (to not interrupt user reading)
            if self.console_text.yview()[1] > 0.9:
                self.console_text.see(tk.END)
            
            # Limit console size more efficiently - check less frequently
            lines = int(self.console_text.index('end-1c').split('.')[0])
            if lines > 150:  # Allow more lines before cleanup
                # Remove multiple lines at once for efficiency
                self.console_text.delete("1.0", "26.0")  # Remove 25 lines at once
        except Exception as e:
            # Don't let console errors crash the app
            pass

def main():
    root = tk.Tk()
    app = ICM20948Controller(root)
    
    def on_closing():
        if app.connected:
            app.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()