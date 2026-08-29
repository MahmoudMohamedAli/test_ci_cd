import serial
import time
import sys

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
TIMEOUT = 1
TEST_TIMEOUT = 60

PASS_STRING = "ALL TESTS PASSED"
FAIL_STRING = "FAIL"


def main():
    print(f"Opening {PORT}...")

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=TIMEOUT
        )
    except Exception as e:
        print(f"ERROR: Could not open serial port: {e}")
        sys.exit(1)

    # Opening the serial port can reset some ESP32 boards.
    # Give the ESP32 time to boot.
    time.sleep(2)

    print("Waiting for Unity test result...")
    print("----------------------------------------")

    start_time = time.time()

    while time.time() - start_time < TEST_TIMEOUT:

        line = ser.readline().decode("utf-8", errors="replace").strip()

        if not line:
            continue

        print(line)

        if PASS_STRING in line:
            print("----------------------------------------")
            print("HIL TEST RESULT: PASS")
            ser.close()
            sys.exit(0)

        if FAIL_STRING in line:
            print("----------------------------------------")
            print("HIL TEST RESULT: FAIL")
            ser.close()
            sys.exit(1)

    print("----------------------------------------")
    print("HIL TEST RESULT: TIMEOUT")

    ser.close()
    sys.exit(1)


if __name__ == "__main__":
    main()