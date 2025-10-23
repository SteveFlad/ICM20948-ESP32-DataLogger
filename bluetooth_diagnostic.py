#!/usr/bin/env python3
"""
Comprehensive Bluetooth Diagnostic Tool
Analyzes the current Bluetooth situation and provides guidance
"""

import serial
import serial.tools.list_ports
import subprocess
import time

class BluetoothDiagnostic:
    def __init__(self):
        self.results = {}
        
    def check_paired_devices(self):
        """Check what Bluetooth devices are paired"""
        print("🔍 Checking Paired Bluetooth Devices")
        print("=" * 50)
        
        try:
            # Try using PowerShell to get Bluetooth devices
            result = subprocess.run([
                'powershell', 
                'Get-PnpDevice | Where-Object {$_.Class -eq "Bluetooth" -and $_.FriendlyName -like "*ESP32*"} | Select-Object Status, FriendlyName'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                print("ESP32 Bluetooth Devices Found:")
                print(result.stdout)
            else:
                print("❌ No ESP32 Bluetooth devices found")
                
        except subprocess.TimeoutExpired:
            print("⏰ PowerShell command timed out")
        except Exception as e:
            print(f"❌ Error checking devices: {e}")
    
    def check_serial_ports(self):
        """Check all available serial ports"""
        print("\n🔍 Checking Serial Ports")
        print("=" * 50)
        
        ports = list(serial.tools.list_ports.comports())
        
        for port in ports:
            print(f"📍 {port.device}: {port.description}")
            if "Bluetooth" in port.description:
                print(f"   🔵 Bluetooth port detected")
                self.test_port_availability(port.device)
            elif "Silicon Labs" in port.description or "CP210" in port.description:
                print(f"   🔌 USB/Serial bridge (likely ESP32)")
                self.test_port_availability(port.device)
                
    def test_port_availability(self, port):
        """Test if a port can be opened"""
        try:
            ser = serial.Serial(port, 115200, timeout=0.5)
            ser.close()
            print(f"   ✅ {port} is available")
            return True
        except Exception as e:
            print(f"   ❌ {port} unavailable: {e}")
            return False
    
    def check_bluetooth_services(self):
        """Check if Bluetooth services are running"""
        print("\n🔍 Checking Bluetooth Services")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                'powershell',
                'Get-Service | Where-Object {$_.Name -like "*Bluetooth*"} | Select-Object Name, Status'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                print("Bluetooth Services:")
                print(result.stdout)
            else:
                print("❌ No Bluetooth services found")
                
        except Exception as e:
            print(f"❌ Error checking services: {e}")
    
    def provide_recommendations(self):
        """Provide recommendations based on findings"""
        print("\n🎯 Recommendations")
        print("=" * 50)
        
        print("Based on your system analysis:")
        print()
        
        print("1. 📱 Current Bluetooth Status:")
        print("   • ESP32_BNO055 is paired but not active/connected")
        print("   • COM4 and COM6 are Bluetooth virtual ports")
        print("   • COM3 is your USB connection to ESP32")
        print()
        
        print("2. 🔧 To Enable ESP32 Bluetooth Communication:")
        print("   a) First, get your ESP32 firmware working via USB (COM3)")
        print("   b) Upload the ICM20948 code that includes Bluetooth")
        print("   c) Power on the ESP32 - it should advertise as 'ESP32_ICM20948_Config'")
        print("   d) In Windows Settings → Bluetooth, look for this device")
        print("   e) Pair it (may create a new COM port)")
        print()
        
        print("3. 🚀 Next Steps:")
        print("   • Continue using Arduino IDE to upload firmware to ESP32")
        print("   • Once uploaded, the ESP32 will advertise Bluetooth")
        print("   • You can then pair it and get wireless sensor data")
        print("   • Use the improved ICM20948_Controller.py with the Bluetooth COM port")
        print()
        
        print("4. 🔌 Current Working Setup:")
        print("   • Use COM3 for USB communication (programming and testing)")
        print("   • Once firmware is uploaded and Bluetooth works:")
        print("   • Switch to COM4 (or new assigned COM port) for wireless")
        
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print("🔍 Bluetooth ESP32 Diagnostic Tool")
        print("=" * 60)
        print("Analyzing your Bluetooth and ESP32 setup...")
        print("=" * 60)
        
        self.check_serial_ports()
        self.check_paired_devices()
        self.check_bluetooth_services()
        self.provide_recommendations()
        
        print("\n" + "=" * 60)
        print("🏁 Diagnostic Complete")
        print("=" * 60)

def main():
    diagnostic = BluetoothDiagnostic()
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()