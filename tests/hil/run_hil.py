import serial
import time
import sys
import re

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
TIMEOUT = 1
TEST_TIMEOUT = 60


def main():

    print(f"Opening {PORT}...")

    try:
        ser = serial.Serial(
            PORT,
            BAUDRATE,
            timeout=TIMEOUT
        )
    except Exception as e:
        print(f"ERROR: Cannot open serial port: {e}")
        sys.exit(1)

    print("Serial port opened.")
    ser.reset_input_buffer()
    # Give the serial connection time to initialize
    time.sleep(1)

    # Reset ESP32
    print("Resetting ESP32...")

    ser.dtr = False
    ser.rts = True
    time.sleep(0.1)
    ser.rts = False

    print("Waiting for Unity tests...")
    print("----------------------------------------")

    start_time = time.time()

    while time.time() - start_time < TEST_TIMEOUT:

        line = ser.readline().decode(
            "utf-8",
            errors="replace"
        ).strip()

        if not line:
            continue

        print(line)
        match = re.search( r"(\d+)\s+Tests\s+(\d+)\s+Failures\s+(\d+)\s+Ignored",line)
        if match:
            tests = int(match.group(1))
            failures = int(match.group(2))
            ignored = int(match.group(3))
            print("----------------------------------------")
            print(f"Tests:    {tests}")
            print(f"failures: {failures}")
            print(f"ignored:  {ignored}")
            if tests > 0 and failures == 0:
                print("HIL TEST RESULT: PASS")
                ser.close()
                sys.exit(0)
            else:
                print("HIL TEST RESULT: FAIL")
                ser.close()
                sys.exit(1)   

    print("----------------------------------------")
    print("HIL TEST RESULT: TIMEOUT")

    ser.close()
    sys.exit(1)


if __name__ == "__main__":
    main()