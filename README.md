#  DIY ESP32 Honda-Style Digital Cluster for Pit Bikes

An open-source, low-cost digital dashboard designed for small motorcycles, dirt bikes, and pit bikes (specifically built and tested for a **Lifan 125cc swapped CRF50**). 

This project emulates the iconic **Honda S2000 AP1 digital tachometer/speedometer arc** and an **EG Civic analog cluster**, running efficiently on an **ESP32 microcontroller** with MicroPython.

---

##  Features

* **Dual Cluster Modes:** Switch between a digital **S2000 arc style gauge** and an **EG Civic analog needle gauge**.
* **Instant Boot:** Powers on in under 0.5 seconds—no heavy OS boot time.
* **Non-Invasive Electrical Setup:** Designed to run via a standalone USB power bank switched on/off through the bike's stock key ignition switch.
* **Hardware Isolation:** Isolates raw spark plug ignition noise using optocouplers to protect microelectronics.
* **Built-in Desktop Simulator:** Test and refine code in **VS Code** using **Wokwi** without plugging in physical hardware.

---

##  Hardware Requirements & Components

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

##  Wiring Overview

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
