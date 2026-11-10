# DIY Raspberry Pi Honda-Style Digital Cluster for Pit Bikes

An open-source, low-cost digital dashboard designed for small motorcycles, dirt bikes, and pit bikes (specifically built for a **125cc Mini Jeep** **Lifan 125cc swapped CRF50** And a **Built GX200 swapped RT100**). 

This project emulates the iconic **Honda S2000 AP1 digital tachometer/speedometer arc** **EG Civic analog cluster** and a **Del Sol analog cluster** with more on the way.

---

## Features

* **Dual Cluster Modes:** Switch between a digital **S2000 arc style gauge** and an **EG Civic analog needle gauge**.
* **Instant Boot:** Powers on in under 0.5 seconds—no heavy OS boot time on the physical bike.
* **Non-Invasive Electrical Setup:** Designed to run via a standalone USB power bank switched on/off through the bike's stock key ignition switch.
* **Hardware Isolation:** Isolates raw spark plug ignition noise using optocouplers to protect microelectronics.

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

## License

This project is open-source under the **MIT License**. Feel free to modify, expand, and adapt it for your own custom bike builds!
