# ESP32 CI/CD with Docker, Unit Tests, HIL, and Automatic Deployment

A simple embedded CI/CD learning project for an **ESP32** using **ESP-IDF**, **Docker**, **GitHub Actions**, **Unity tests**, and a **self-hosted runner connected to physical hardware**.

The goal of this project is to demonstrate how embedded software can be automatically:

1. Unit tested on the host
2. Built for ESP32
3. Tested on real ESP32 hardware (HIL)
4. Packaged as a firmware artifact
5. Released as a versioned GitHub Release
6. Deployed to a physical ESP32

---

## 1. Project Architecture

```text
                         Git Push / Pull Request
                                  |
                                  v
                         GitHub Actions
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
          Host Unit Tests                    HIL Tests
          Ubuntu Runner                  Self-Hosted Runner
                 |                                 |
                 v                                 v
               GCC                           Docker + ESP-IDF
                 |                                 |
                 v                                 v
            PASS / FAIL                      Build Test Firmware
                                                   |
                                                   v
                                             Flash ESP32
                                                   |
                                                   v
                                             Unity Tests
                                                   |
                                                   v
                                           run_hil.py
                                                   |
                                             PASS / FAIL
                 |                                 |
                 +----------------+----------------+
                                  |
                            Both tests PASS
                                  |
                                  v
                         Production Build
                                  |
                                  v
                         Firmware Artifact
                         /              \
                        /                \
                       v                  v
                GitHub Release       Deployment
                                        |
                                        v
                                      ESP32
                                        |
                                        v
                                Boot Verification
```

---

# 2. Tools and Their Roles

| Tool | Role |
|---|---|
| **Git** | Source-code version control |
| **GitHub** | Repository, pull requests, releases, and CI/CD |
| **GitHub Actions** | Runs the automated pipeline |
| **Docker** | Provides a reproducible ESP-IDF build environment |
| **ESP-IDF** | Espressif framework and build system for ESP32 |
| **GCC** | Compiles and runs host-side unit tests |
| **Unity** | Test framework used for ESP32/HIL tests |
| **Python** | Reads ESP32 serial output and decides PASS/FAIL |
| **Self-hosted runner** | GitHub Actions runner with access to physical ESP32 |
| **esptool** | Flashes already-built firmware artifacts to ESP32 |
| **GitHub Artifact** | Stores firmware between workflow jobs |
| **GitHub Release** | Publishes versioned firmware |

---

# 3. Repository Structure

Example structure:

```text
test_ci_cd/
│
├── main/
│   ├── main.c
│   └── CMakeLists.txt
│
├── components/
│   └── math/
│       ├── math.c
│       ├── CMakeLists.txt
│       └── include/
│           └── math.h
│
├── tests/
│   ├── host/
│   │   └── test_logic.c
│   │
│   └── hil/
│       ├── main/
│       │   ├── test_math.c
│       │   └── CMakeLists.txt
│       ├── run_hil.py
│       └── CMakeLists.txt
│
├── .github/
│   └── workflows/
│       └── build.yml
│
├── CMakeLists.txt
├── sdkconfig
└── README.md
```

The important concept is that the same production logic can be tested in two environments:

```text
components/math/
       |
       +--------------------+
       |                    |
       v                    v
tests/host/             tests/hil/
       |                    |
       v                    v
     PC/GCC              ESP32/Unity
```

---

# 4. Host Unit Tests

Host tests test the application logic without requiring an ESP32.

For example:

```c
assert(add(2, 3) == 5);
assert(add(-2, 5) == 3);
assert(multiply(2, 3) == 6);
assert(multiply(-2, -3) == 6);
```

They are compiled with GCC:

```bash
gcc \
  -I components/math/include \
  tests/host/test_logic.c \
  components/math/math.c \
  -o test_logic

./test_logic
```

If a test fails, the program exits with a non-zero status and GitHub Actions marks the job as failed.

### Why host tests?

They are:

- Fast
- Cheap
- Independent of hardware
- Good for testing pure logic

---

# 5. HIL Tests

HIL means:

> **Hardware-In-the-Loop**

Instead of running the test on the PC, the test firmware runs on the real ESP32.

The flow is:

```text
test_math.c
     |
     v
ESP-IDF build
     |
     v
HIL firmware
     |
     v
ESP32
     |
     v
Unity
     |
     v
Serial output
     |
     v
run_hil.py
```

Example Unity output:

```text
./main/test_math.c:62:test_add_positive_numbers:PASS
./main/test_math.c:63:test_add_negative_numbers:PASS
./main/test_math.c:64:test_add_zero:PASS
./main/test_math.c:66:test_multiply_positive_numbers:PASS
./main/test_math.c:67:test_multiply_by_zero:PASS
./main/test_math.c:68:test_multiply_negative_numbers:PASS
./main/test_math.c:70:test_divide_positive_numbers:PASS
./main/test_math.c:71:test_divide_fraction:PASS
./main/test_math.c:72:test_divide_by_zero:PASS

9 Tests 0 Failures 0 Ignored
OK
```

The Python script monitors the serial port and detects:

```text
9 Tests 0 Failures 0 Ignored
```

If failures are zero:

```text
HIL TEST RESULT: PASS
```

The script exits with:

```text
exit code 0
```

GitHub therefore marks the HIL job as successful.

If failures occur or the ESP32 doesn't respond before the timeout:

```text
HIL TEST RESULT: FAIL
```

or:

```text
HIL TEST RESULT: TIMEOUT
```

The script exits with:

```text
exit code 1
```

and GitHub marks the job as failed.

---

# 6. Docker

The ESP32 build uses the official Espressif Docker image:

```bash
docker run --rm \
  -v "${PWD}:/project" \
  -w /project \
  espressif/idf \
  idf.py build
```

### What each part means

```text
docker run
```

Start a container.

```text
--rm
```

Remove the container after the command finishes.

```text
-v "${PWD}:/project"
```

Mount the current repository into the container.

```text
-w /project
```

Use `/project` as the working directory.

```text
espressif/idf
```

Use the ESP-IDF Docker image.

```text
idf.py build
```

Run the ESP-IDF build.

Docker gives the CI system a controlled ESP-IDF environment instead of depending on whatever ESP-IDF version happens to be installed on the runner.

For production CI, it is better to pin the image version instead of relying on:

```text
espressif/idf:latest
```

For example, use the ESP-IDF version that the project has been validated with.

---

# 7. Self-Hosted Runner

The normal GitHub-hosted runner cannot physically access your ESP32.

Therefore the HIL job uses:

```yaml
runs-on: [self-hosted]
```

The self-hosted machine has:

```text
GitHub Actions Runner
        |
        +--- Docker
        |
        +--- Python
        |
        +--- USB
              |
              v
            ESP32
```

The ESP32 appears as:

```text
/dev/ttyUSB0
```

The workflow can therefore flash and monitor the physical device.

---

# 8. Flashing the HIL Firmware

The HIL firmware is built from:

```text
tests/hil/
```

The workflow builds it with:

```bash
docker run --rm \
  -v "${PWD}:/project" \
  -w /project/tests/hil \
  espressif/idf \
  idf.py build
```

Then it is flashed:

```bash
docker run --rm \
  --device=/dev/ttyUSB0 \
  -v "${PWD}:/project" \
  -w /project/tests/hil \
  espressif/idf \
  idf.py -p /dev/ttyUSB0 flash
```

Important:

> This is the **test firmware**, not the production firmware.

It contains the Unity test application.

---

# 9. HIL Serial Monitoring

After the firmware is flashed, `run_hil.py` monitors:

```text
/dev/ttyUSB0
```

at:

```text
115200 baud
```

The basic logic is:

```text
Open serial port
       |
       v
Wait for Unity output
       |
       v
Find test summary
       |
       +---- Failures = 0 ---> PASS
       |
       +---- Failures > 0 ---> FAIL
       |
       +---- Timeout --------> FAIL
```

This converts the physical ESP32 result into a GitHub Actions result.

---

# 10. Production Build

The production application is built separately from the HIL firmware.

After both host tests and HIL tests pass:

```text
Host Test     PASS
     +
HIL Test      PASS
     |
     v
Production Build
```

The workflow uses:

```yaml
needs:
  - host-test
  - hil-test
```

This is important because production firmware should not be produced as a successful pipeline output if validation failed.

---

# 11. Firmware Artifact

The production build creates firmware files such as:

```text
firmware/
├── app.bin
├── bootloader.bin
├── partition-table.bin
└── version.txt
```

The workflow uploads them with:

```yaml
uses: actions/upload-artifact@v4
```

An artifact is useful for passing files between GitHub Actions jobs.

For example:

```text
production-build
       |
       v
esp32-firmware
       |
       +----> release
       |
       +----> deployment
```

---

# 12. GitHub Releases

A normal push to `main` runs CI:

```text
Push
 |
 +--> Host tests
 |
 +--> HIL
 |
 +--> Production build
 |
 +--> Artifact
```

A version tag triggers the same validation plus release/deployment:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow recognizes:

```yaml
tags:
  - 'v*'
```

The release job is protected with:

```yaml
if: startsWith(github.ref, 'refs/tags/v')
```

Therefore:

```text
Normal push:
Release -> skipped

v1.0.0 tag:
Release -> runs
```

A release can contain:

```text
ESP32 Firmware v1.0.0

Assets:
├── app.bin
├── bootloader.bin
├── partition-table.bin
└── version.txt
```

---

# 13. Production Deployment

Deployment uses the exact firmware artifact produced by the production build.

This is important.

We do NOT rebuild the production firmware during deployment.

Instead:

```text
Production build
      |
      v
Firmware artifact
      |
      +----------------+
      |                |
      v                v
GitHub Release      Deployment
                       |
                       v
                     ESP32
```

The deployment job downloads:

```text
esp32-firmware
```

and flashes:

```text
bootloader.bin
partition-table.bin
app.bin
```

using `esptool`.

Example:

```bash
esptool \
  --port /dev/ttyUSB0 \
  write_flash \
  0x1000 bootloader.bin \
  0x8000 partition-table.bin \
  0x10000 app.bin
```

### Why use esptool here instead of `idf.py flash`?

`idf.py flash` normally works with an ESP-IDF project and its `build/` directory.

Deployment is different:

```text
CI artifact
    |
    +-- app.bin
    +-- bootloader.bin
    +-- partition-table.bin
```

There is no need to rebuild the project.

`esptool` directly flashes the already-built artifact.

This also makes it clear that the **same artifact that was tested/released is the artifact being deployed**.

---

# 14. CI vs CD

## Continuous Integration (CI)

CI answers:

> "Does the code work?"

```text
Commit
  |
  v
Host Unit Tests
  |
  v
HIL Tests
  |
  v
Production Build
```

## Continuous Delivery/Deployment (CD)

CD answers:

> "Can we package and deploy the validated firmware?"

```text
Validated firmware
       |
       v
Artifact
       |
       v
GitHub Release
       |
       v
ESP32 Deployment
```

---

# 15. Complete Pipeline

The final system is:

```text
                    Developer
                        |
                        v
                   git push
                        |
                        v
                GitHub Repository
                        |
                        v
                 GitHub Actions
                        |
             +----------+----------+
             |                     |
             v                     v
        Host Unit Test          HIL Test
             |                     |
            GCC               Self-hosted PC
             |                     |
             |                  Docker
             |                     |
             |                 ESP-IDF
             |                     |
             |                  ESP32
             |                     |
             |                   Unity
             |                     |
             |                run_hil.py
             |                     |
             +----------+----------+
                        |
                   Tests PASS
                        |
                        v
                Production Build
                        |
                        v
                Firmware Artifact
                   /          \
                  /            \
                 v              v
        GitHub Release       Deploy
             v                  |
          v1.0.0               v
                            ESP32
                              |
                              v
                       Boot Verification
```

---

# 16. Recommended Improvements

The basic system is working. The next improvements should be:

### 1. Pin Docker versions

Avoid:

```text
espressif/idf:latest
```

Use a known ESP-IDF version.

### 2. Protect the physical hardware

Use GitHub Actions concurrency so two jobs don't access the same ESP32 simultaneously:

```yaml
concurrency:
  group: esp32-hardware
  cancel-in-progress: false
```

### 3. Add production boot verification

After deployment:

```text
Flash production firmware
        |
        v
Reset ESP32
        |
        v
Monitor serial
        |
        v
Find APP_STARTED
        |
    +---+---+
    |       |
   YES      NO
    |       |
   PASS    FAIL
```

### 4. Add more realistic tests

As the application grows, add tests for:

- Boundary values
- Invalid inputs
- Error handling
- Hardware drivers
- Communication interfaces
- State machines
- Timeouts
- Recovery behavior

---

# 17. Useful Commands

### Run production build locally

```bash
docker run --rm \
  -v "${PWD}:/project" \
  -w /project \
  espressif/idf \
  idf.py build
```

### Build HIL firmware locally

```bash
docker run --rm \
  -v "${PWD}:/project" \
  -w /project/tests/hil \
  espressif/idf \
  idf.py build
```

### Flash HIL firmware

```bash
docker run --rm \
  --device=/dev/ttyUSB0 \
  -v "${PWD}:/project" \
  -w /project/tests/hil \
  espressif/idf \
  idf.py -p /dev/ttyUSB0 flash
```

### Run HIL monitor

```bash
python3 tests/hil/run_hil.py
```

### Monitor ESP32 manually

```bash
python3 -m serial.tools.miniterm /dev/ttyUSB0 115200
```

### Create a release

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

# 18. Key Lessons

The main lessons from this project are:

1. **Unit tests and HIL tests serve different purposes.**
2. **Host tests are fast and should catch logic problems early.**
3. **HIL tests verify behavior on real hardware.**
4. **Docker provides a reproducible ESP-IDF environment.**
5. **A self-hosted GitHub runner is needed to access physical hardware.**
6. **Python can convert serial test results into CI PASS/FAIL status.**
7. **Production firmware should only be built after validation passes.**
8. **The production artifact should be reused for release and deployment.**
9. **Version tags provide controlled firmware releases.**
10. **Deployment should verify that the device actually boots successfully.**

---

## Final Result

This project demonstrates a complete basic embedded pipeline:

```text
CODE
  ↓
UNIT TEST
  ↓
HIL TEST
  ↓
PRODUCTION BUILD
  ↓
ARTIFACT
  ↓
VERSIONED RELEASE
  ↓
DEPLOY TO ESP32
  ↓
DEVICE VERIFICATION
```

This is a foundation that can later be extended to multiple ESP32 devices, different hardware configurations, automated regression testing, firmware signing, OTA updates, and production device fleets.
