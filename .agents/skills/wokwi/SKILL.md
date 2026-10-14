---
name: wokwi
description: >-
  Use this skill when developing, configuring, or simulating embedded systems and IoT
  projects on ESP32, Arduino, Raspberry Pi Pico, or STM32 using Wokwi. Covers diagram.json
  hardware wiring, wokwi.toml configuration, TFT displays (ILI9341, ST7789), sensor simulation,
  and MicroPython/C++ firmware workflows.
---

# Wokwi Simulation Skill

This skill provides comprehensive instructions for simulating embedded systems (particularly ESP32) using Wokwi in VS Code, the Wokwi web simulator, and `wokwi-cli`.

## 1. Project Configuration Files

Every local Wokwi project consists of two core configuration files at the project root:

### `diagram.json`
Defines the virtual hardware, boards, components, and wiring connections.

- **Board types**:
  - `board-esp32-devkit-c-v4` or `board-esp32-devkit-v1`
  - `board-esp32-s3-devkitc-1`
  - `board-esp32-c3-devkitm-1`
  - `board-pi-pico`
- **Common Display Components**:
  - `wokwi-ili9341`: 320x240 SPI TFT color display (ideal for ESP32 Cheap Yellow Display / CYD simulation)
  - `wokwi-st7789`: 240x240 or 240x320 SPI IPS color display
  - `wokwi-ssd1306`: 128x64 I2C OLED display
- **Interactive Input Components**:
  - `wokwi-potentiometer`: Simulates analog throttle, RPM pickup, or sensors via ADC
  - `wokwi-pushbutton`: Simulates mode buttons or switches
  - `wokwi-rotary-encoder`: Simulates dial navigation or wheel speed

### `wokwi.toml`
Tells the Wokwi VS Code extension where to locate firmware binaries:

```toml
[wokwi]
version = 1
firmware = "firmware.bin"
elf = "firmware.elf"

# Optional RFC2217 serial forwarding for MicroPython REPL / mpremote:
# [[net.forward]]
# from = "localhost:4000"
# to = "target:4000"
```

---

## 2. ESP32 + ILI9341 Wiring Reference (`diagram.json`)

Standard SPI wiring between ESP32 and `wokwi-ili9341`:

```json
{
  "version": 1,
  "author": "Antigravity",
  "editor": "wokwi",
  "parts": [
    { "type": "board-esp32-devkit-c-v4", "id": "esp", "top": 0, "left": 0, "attrs": {} },
    { "type": "wokwi-ili9341", "id": "lcd", "top": -40, "left": 180, "attrs": {} },
    { "type": "wokwi-potentiometer", "id": "pot_rpm", "top": 120, "left": -120, "attrs": {} },
    { "type": "wokwi-pushbutton", "id": "btn_mode", "top": 220, "left": -120, "attrs": { "color": "red" } }
  ],
  "connections": [
    [ "lcd:GND", "esp:GND.1", "black", [ "v0" ] ],
    [ "lcd:VCC", "esp:3V3", "red", [ "v0" ] ],
    [ "lcd:CS", "esp:15", "green", [ "v0" ] ],
    [ "lcd:D/C", "esp:2", "blue", [ "v0" ] ],
    [ "lcd:MOSI", "esp:23", "orange", [ "v0" ] ],
    [ "lcd:SCK", "esp:18", "yellow", [ "v0" ] ],
    [ "lcd:MISO", "esp:19", "gray", [ "v0" ] ],
    [ "pot_rpm:1", "esp:GND.2", "black", [ "v0" ] ],
    [ "pot_rpm:2", "esp:34", "purple", [ "v0" ] ],
    [ "pot_rpm:3", "esp:3V3", "red", [ "v0" ] ],
    [ "btn_mode:1.1", "esp:GND.2", "black", [ "v0" ] ],
    [ "btn_mode:2.1", "esp:21", "cyan", [ "v0" ] ]
  ]
}
```

---

## 3. MicroPython Simulation Workflow

When targeting MicroPython on ESP32 in Wokwi:

1. **Wokwi Web (wokwi.com)**:
   - Select **ESP32 MicroPython**.
   - Paste `diagram.json` in the Diagram tab.
   - MicroPython firmware is bundled automatically; your `main.py` runs on play.
2. **VS Code Wokwi Extension**:
   - Download the official MicroPython ESP32 generic `.bin` firmware.
   - Point `wokwi.toml` `firmware = "ESP32_GENERIC-v1.xx.x.bin"`.
   - Press `F1` -> **Wokwi: Start Simulator**.
   - Connect via `mpremote connect port:rfc2217://localhost:4000 run main.py`.

---

## 4. Porting Desktop Python (Tkinter) to ESP32 Displays

Desktop UI code (Tkinter / Pygame) cannot run on ESP32 microcontrollers because ESP32 lacks desktop window managers and Tcl/Tk.

### Migration Strategy:
1. **Coordinate Rescaling**:
   - Desktop prototype canvas: typically 850x420 or larger.
   - Embedded TFT displays: typically 320x240 (ILI9341 / CYD) or 240x240 (ST7789).
   - Compute a scale factor: $X_{esp} = X_{pc} \times \frac{320}{850}$, $Y_{esp} = Y_{pc} \times \frac{240}{420}$.
2. **Graphic Primitives Mapping**:
   - `canvas.create_line(x1, y1, x2, y2)` $\rightarrow$ `display.line(x1, y1, x2, y2, color)`
   - `canvas.create_text(x, y, text)` $\rightarrow$ `display.draw_text(x, y, text, font, color)`
   - `canvas.create_arc(...)` or polygon $\rightarrow$ Custom trigonometric polygon filler or arc bar generator.
3. **Double Buffering & Flicker Elimination**:
   - TFT displays flicker if cleared every frame.
   - Only erase the active needle or segment (`fill_rect` of old bounding box, or XOR drawing, or LovyanGFX/TFT_eSPI Sprites).
