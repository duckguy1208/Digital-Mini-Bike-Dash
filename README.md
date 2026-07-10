# PicoDash: DIY MicroPython Digital Dashboard

___

A custom DIY digital vehicle dashboard built with a Raspberry Pi Pico and MicroPython, featuring a live GPS/magnet-based speedometer, an inductive pulse tachometer, and an SPI engine temperature monitor.


---

An open-source, instant-on digital dashboard designed for small vehicles, go-karts, and mini jeeps. This project uses a **Raspberry Pi Pico** running **MicroPython** to interface with physical engine sensors and output live telemetry data to a bright SPI LCD display.

##  Features
* **Instant-On Boot Time:** No operating system lag—boots up the millisecond the vehicle key is turned.
* **Speedometer:** Real-time speed calculation using an A3144 Hall Effect sensor and wheel magnets.
* **Tachometer (RPM):** Isolated inductive pickup wrapped around the spark plug wire, safely processed via a PC817 optocoupler.
* **Engine Temperature:** High-temperature tracking via a MAX6675 module and a K-Type thermocouple ring mounted under the spark plug.
* **Custom UI:** Lightweight graphics rendering built using MicroPython's primitive drawing libraries.

---

##  Hardware Shopping List
* **Microcontroller:** Raspberry Pi Pico (or Pico 2 / Pico W)
* **Display:** 3.5" or 4.3" ILI9341 SPI TFT LCD Screen
* **Speed Sensor:** A3144 Hall Effect Sensor Module + Neodymium Magnets
* **RPM Isolation:** PC817 Optocoupler Module (1-channel)
* **Temperature Sensor:** MAX6675 Module with a 14mm K-Type Thermocouple Ring
* **Power Supply:** 12V to 5V Step-Down (Buck) Converter (USB Output)
* **Wiring:** 22 AWG Hookup wire

---

##  Wiring Configuration

| Component | Component Pin | Pico Pin | Pico Function |
| :--- | :--- | :--- | :--- |
| **Hall Effect (Speed)** | VCC / GND / OUT | 36 / 38 / 20 | 3V3 / GND / GPIO 15 |
| **Optocoupler (RPM)** | VCC / OUT / GND | 36 / 21 / 38 | 3V3 / GPIO 16 / GND |
| **MAX6675 (Temp)** | SCK / CS / SO | 4 / 5 / 6 | GPIO 2 / GPIO 3 / GPIO 4 |
| **ILI9341 Screen** | CS / RESET / DC | 22 / 26 / 27 | GPIO 17 / GPIO 20 / GPIO 21 |
| **ILI9341 Screen** | MOSI / SCK | 24 / 25 | GPIO 19 / GPIO 18 |

*Note: Power the Pico directly via the Micro-USB/USB-C port using the 12V-to-5V step-down converter connected to the vehicle's accessory power circuit.*

---

## Installation & Setup

1. **Download Thonny IDE:** Install the free software from [thonny.org](https://thonny.org/).
2. **Flash MicroPython:** Hold the `BOOTSEL` button on your Pico, plug it into your computer, and use Thonny to install the official MicroPython firmware.
3. **Add Libraries:** Upload your required display drivers (e.g., `ili9341.py`) and temperature drivers (`max6675.py`) to the Pico's root directory.
4. **Upload Code:** Save your main dashboard script to the Pico as **`main.py`**. 
   >  *The file must be named `main.py` so the Pico knows to execute it automatically when decoupled from the computer and powered by the vehicle battery.*

