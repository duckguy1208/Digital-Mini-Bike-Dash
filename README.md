# DIY ESP32 Honda-Style Digital Cluster for Pit Bikes

An open-source, low-cost digital dashboard designed for small motorcycles, dirt bikes, and pit bikes (specifically built for a **Lifan 125cc swapped CRF50** And a **Built GX200 swapped RT100**). 

This project emulates the iconic **Honda S2000 AP1 digital tachometer/speedometer arc** and an **EG Civic analog cluster**, running efficiently on an **ESP32 microcontroller** with MicroPython.

> **Note:** The current base code in this repository includes a desktop-based **Tkinter implementation** used for initial prototyping, math verification, and UI layout testing on a PC. Work is underway to port and optimize all drawing routines to MicroPython for the ESP32 hardware.

---

## Features

* **Dual Cluster Modes:** Switch between a digital **S2000 arc style gauge** and an **EG Civic analog needle gauge**.
* **Instant Boot:** Powers on in under 0.5 seconds—no heavy OS boot time on the physical bike.
* **Non-Invasive Electrical Setup:** Designed to run via a standalone USB power bank switched on/off through the bike's stock key ignition switch.
* **Hardware Isolation:** Isolates raw spark plug ignition noise using optocouplers to protect microelectronics.
* **Desktop & Simulator Ready:** Test UI logic via Tkinter on desktop or in **VS Code** using **Wokwi** for ESP32.

---

## Hardware Requirements & Components

| Component | Purpose | Recommended Model / Notes |
| :--- | :--- | :--- |
| **Microcontroller + Screen** | Core brain & visual UI | ESP32 Cheap Yellow Display (CYD 2.8") or Waveshare 2.1" Round Display |
| **Tachometer Isolation** | Ignition noise protection | PC817 1-Channel Optocoupler Module |
| **RPM Pickup** | Spark plug pulse sensing | 22 AWG Solid Core Wire wrapped 4–6 times around the spark plug boot |
| **Speedometer Sensor** | Wheel rotation counting | NJK-5002C Hall Effect Proximity Sensor + Neodymium Magnet |
| **Pull-up Resistor** | Signal stabilization | 10kΩ Resistor |
| **Power Source** | Clean 5V power supply | Compact 5,000mAh USB Power Bank |
| **Key Switch Integration** | Automated power ON/OFF | Switched positive wire tapped into CRF50 Key Harness |

---

## Wiring Overview

### 1. Speedometer (Hall Effect Sensor)
* **VCC:** Connects to `3.3V` on ESP32
* **GND:** Connects to `GND` on ESP32
* **Signal:** Connects to **`GPIO 35`** (with a $10\text{k}\Omega$ pull-up resistor to `3.3V`)

### 2. Tachometer (Spark Plug RPM)
* **High Voltage Side:** Inductive wire wrap around spark plug lead $\rightarrow$ **IN+** on PC817 Optocoupler; Frame Ground $\rightarrow$ **IN-**
* **Low Voltage Side:** * **VCC:** Connects to `3.3V` on ESP32
  * **GND:** Connects to `GND` on ESP32
  * **OUT:** Connects to **`GPIO 22`** on ESP32

### 3. Power Supply
* **Red (+5V Wire):** Routed through the **CRF50 Key Switch** $\rightarrow$ **`VIN` (5V)** pin on ESP32.
* **Black (GND Wire):** Connected directly to **`GND`** on ESP32.

---

## Software & Simulation Setup

### Running Desktop Prototype (Tkinter)
1. Ensure Python 3.x is installed on your computer.
2. Run `python main.py` in your terminal to launch the interactive PC cluster simulator.
   - **Controls:** Move mouse left/right for RPM throttle, scroll wheel for Temp/Fuel, click to swap clusters.

### Testing MicroPython in Wokwi Simulator
The repository is pre-configured with a 320x240 ILI9341 SPI TFT, RPM potentiometer, and mode button in `diagram.json`.

#### Option A: Wokwi Web (Zero Installation)
1. Go to [wokwi.com/micropython/esp32](https://wokwi.com/micropython/esp32).
2. Copy the contents of `diagram.json` into the **diagram.json** tab.
3. Add `ili9341.py` and `esp32_dash.py` (or paste into `main.py`).
4. Click **Play** — watch the startup sweep and turn the RPM potentiometer knob to accelerate!

#### Option B: VS Code Extension
The MicroPython runtime (`firmware.bin`) is pre-installed in the repository.
1. Install the **Wokwi Simulator** extension in VS Code.
2. Press `F1` (or `Cmd+Shift+P`), select **Wokwi: Start Simulator**, and keep the simulator tab visible in the foreground.
3. In your VS Code terminal, execute the dashboard:
   ```bash
   python3 -m mpremote wokwi run esp32_dash.py
   ```
   *(To permanently copy the code to the simulated flash so it boots automatically every time:)*
   ```bash
   python3 -m mpremote wokwi fs cp ili9341.py :ili9341.py + fs cp esp32_dash.py :main.py + repl
   ```

---

## License

This project is open-source under the **MIT License**. Feel free to modify, expand, and adapt it for your own custom bike builds!
