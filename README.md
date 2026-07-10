# Custom Digital Dashboard for Mini Bikes and Dirt Bikes

A rugged, trail-ready digital dashboard powered by a **Raspberry Pi 4 / Zero 2 W** and a **7-inch HDMI Touchscreen**. This system runs a custom **Python Tkinter GUI** to provide real-time telemetry (Speedometer, Tachometer, and Engine Temperature) with dynamic touchscreen skin-swapping (S2000 sweeping tachometer and CRX Del Sol circular gauge).

Designed to seamlessly swap between a custom **Mini Jeep**, a **Honda CRF50**, and a **Gx200 Mini Bike** using a unified multi-pin waterproof wiring harness.

---

##  System Architecture & Component List

### Core Electronics
* **Single Board Computer:** Raspberry Pi 4 (2GB/4GB) or Raspberry Pi Zero 2 W
* **Display:** 7-inch HDMI IPS Touchscreen Display (1024x600 native resolution)
* **Storage:** 32GB or 64GB High-End Endurance MicroSD Card
* **Video:** Short Micro-HDMI to HDMI Cable

### Power Management & Safe Shutdown
* **Smart Shutdown Switch:** Mausberry Circuits Automotive USB Switch or CarPiHat
* **Voltage Regulator:** 12V-to-5V Step-Down Buck Converter (for constant battery line protection)

### Telemetry Sensors
* **Speedometer:** A3144 Hall Effect Sensor Module + Neodymium Hub Magnets
* **Tachometer:** PC817 Optocoupler Module (for high-voltage spark plug inductive isolation)
* **Engine Temperature:** MAX6675 SPI Module with a K-Type Thermocouple Ring Probe

### Fabrication & Housing
* **Enclosure:** Heavy-duty ABS Plastic Project Box (sealed with clear silicone)
* **Harnessing:** Waterproof Multi-Pin Automotive Connector Plug
* **Mounting:** 3M Dual Lock Reclosable Fasteners or Action-Camera Handlebar Clamps

---

## Hardware Pinout Mapping

All connections map directly to the Raspberry Pi's 40-pin GPIO header (3.3V Logic Max):

| Sensor / Module | Sensor Pin | Pi GPIO / Pin | Description |
| :--- | :--- | :--- | :--- |
| **A3144 Speedometer** | VCC | Pin 1 or 2 | Power (3.3V or 5V based on module) |
| | GND | Pin 6 | Ground |
| | Signal | **Pin 11 (GPIO 17)** | Pulse input from wheel magnets |
| **PC817 Tachometer** | Input Side | *Spark Wire* | Wrapped 5-10 times around spark plug lead |
| | Output Collector | Pin 2 or 1 | 3.3V Pull-Up Power source |
| | Output Emitter | **Pin 13 (GPIO 27)** | Cleaned RPM square-wave pulse signal |
| | Output Ground | Pin 9 | System Ground |
| **MAX6675 Temperature** | GND | Pin 14 | Ground |
| | VCC |
