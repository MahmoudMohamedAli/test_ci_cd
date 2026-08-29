import serial
import time
import sys

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

        # Test passed
        if "ALL TESTS PASSED" in line:
            print("----------------------------------------")
            print("HIL TEST RESULT: PASS")

            ser.close()
            sys.exit(0)

        # Test failed
        if "FAILURES" in line:
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