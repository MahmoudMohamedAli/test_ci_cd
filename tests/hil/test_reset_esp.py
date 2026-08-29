import time
import serial

PORT = "/dev/ttyUSB0"  # Replace with your port, e.g., '/dev/ttyUSB0' or 'COM3'
BAUD_RATE = 115200  # Match your ESP-IDF project configuration

# 1. Open serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# 2. Trigger hard reset via RTS line
ser.dtr = False
ser.rts = True
time.sleep(0.1)
ser.rts = False

print("--- ESP32 Reset Triggered. Capturing Output ---")

# 3. Read serial output continuously
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8", errors="ignore")
            print(line, end="")
except KeyboardInterrupt:
    print("\n--- Monitoring Stopped ---")
finally:
    ser.close()