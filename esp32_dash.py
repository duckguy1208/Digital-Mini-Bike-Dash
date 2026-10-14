"""
ESP32 MicroPython Honda-Style Digital Mini Bike Dash
Optimized for 320x240 ILI9341 SPI TFT (ESP32 CYD / Wokwi Simulator)
"""

import math
import time

try:
    import machine
    from machine import Pin, SPI, ADC
except ImportError:
    pass

import ili9341
from ili9341 import color565


# --- Color Palette ---
BG_COLOR = color565(10, 10, 10)
BG_BAR = color565(35, 20, 0)
AMBER = color565(255, 160, 0)
ORANGE = color565(255, 90, 0)
RED = color565(255, 25, 25)
WHITE = color565(240, 240, 240)
GRAY = color565(90, 90, 90)
DARK_GRAY = color565(40, 40, 40)


class S2000ClusterESP32:
    """Honda S2000 AP1 Digital Cluster renderer for 320x240 ILI9341 TFT."""

    def __init__(self, display):
        self.display = display
        self.MAX_RPM = 11000
        self.NUM_BARS = 45

        self.last_active_bars = -1
        self.last_speed = -1
        self.last_temp_bars = -1
        self.last_fuel_bars = -1
        self.last_odo_str = ""

        self.main_odo_miles = 0.0
        self.trip_hours = 0.0
        self.last_time_ms = time.ticks_ms()

        # Precompute arc bar coordinates for maximum runtime performance
        self.bars = []
        for i in range(self.NUM_BARS):
            t = i / float(self.NUM_BARS - 1)
            x1 = 28 + t * 264
            y1 = 58 - math.sin(t * math.pi) * 22
            dx = 1.0
            dy = -math.cos(t * math.pi) * (22.0 * math.pi / 264.0)
            length = math.hypot(dx, dy)
            nx, ny = -dy / length, dx / length
            bar_len = 15
            x2 = x1 + nx * bar_len
            y2 = y1 + ny * bar_len
            self.bars.append((int(x1), int(y1), int(x2), int(y2), nx, ny))

    def draw_static_base(self):
        """Draw cluster static background, labels, tick marks, and scales."""
        self.display.clear(BG_COLOR)

        # 1. Background inactive tachometer bars
        for x1, y1, x2, y2, _, _ in self.bars:
            self.display.draw_thick_line(x1, y1, x2, y2, 3, BG_BAR)

        # 2. RPM Scale Labels (0 to 11 x 1000 RPM)
        for val in range(0, 12):
            t = val / 11.0
            idx = int(t * (self.NUM_BARS - 1))
            x1, y1, x2, y2, nx, ny = self.bars[idx]
            color = RED if val >= 10 else AMBER

            # Tick tick extending outward
            tx = int(x2 + nx * 5)
            ty = int(y2 + ny * 5)
            self.display.draw_line(x2, y2, tx, ty, color)

            # Number label
            num_str = str(val)
            lx = int(x2 + nx * 13) - (len(num_str) * 3)
            ly = int(y2 + ny * 13) - 3
            self.display.draw_text(lx, ly, num_str, color, BG_COLOR, size=1)

        # Top banner label
        self.display.draw_text(130, 8, "r/min x1000", AMBER, BG_COLOR, size=1)

        # 3. Center Speed Unit labels
        self.display.draw_text(225, 115, "MPH", AMBER, BG_COLOR, size=1)
        self.display.draw_text(225, 127, "km/h", DARK_GRAY, BG_COLOR, size=1)

        # 4. Temperature Gauge Static Elements (Left flank)
        self.display.draw_text(25, 172, "C", AMBER, BG_COLOR, size=1)
        self.display.draw_text(75, 172, "H", RED, BG_COLOR, size=1)
        for i in range(7):
            bx = 35 + (i * 6)
            self.display.fill_rect(bx, 170, 4, 10, BG_BAR)

        # 5. Fuel Gauge Static Elements (Right flank)
        self.display.draw_text(240, 172, "E", RED, BG_COLOR, size=1)
        self.display.draw_text(290, 172, "F", AMBER, BG_COLOR, size=1)
        for i in range(7):
            bx = 248 + (i * 6)
            self.display.fill_rect(bx, 170, 4, 10, BG_BAR)

        # 6. Odometer box border
        self.display.fill_rect(100, 175, 120, 16, color565(20, 20, 20))
        self.display.draw_line(100, 175, 220, 175, DARK_GRAY)
        self.display.draw_line(100, 191, 220, 191, DARK_GRAY)

        # Reset state trackers to force complete first draw
        self.last_active_bars = -1
        self.last_speed = -1
        self.last_temp_bars = -1
        self.last_fuel_bars = -1
        self.last_odo_str = ""

    def update(self, rpm, temp=45, fuel=85):
        """Update cluster telemetry with delta rendering for maximum FPS."""
        # --- 1. Tachometer Arc Update (Delta rendering) ---
        clamped_rpm = max(0, min(self.MAX_RPM, rpm))
        target_bars = int((clamped_rpm / float(self.MAX_RPM)) * self.NUM_BARS)

        if target_bars != self.last_active_bars:
            start_i = 0 if self.last_active_bars == -1 else min(self.last_active_bars, target_bars)
            end_i = self.NUM_BARS if self.last_active_bars == -1 else max(self.last_active_bars, target_bars)

            for i in range(start_i, end_i):
                x1, y1, x2, y2, _, _ = self.bars[i]
                if i < target_bars:
                    seg_rpm = (i / float(self.NUM_BARS)) * self.MAX_RPM
                    if seg_rpm >= 10000:
                        c = RED
                    elif seg_rpm >= 9000:
                        c = ORANGE
                    else:
                        c = AMBER
                else:
                    c = BG_BAR
                self.display.draw_thick_line(x1, y1, x2, y2, 3, c)

            self.last_active_bars = target_bars

        # --- 2. Speedometer Update (7-Segment Digits) ---
        sim_speed = int((clamped_rpm / 11000.0) * 145) if clamped_rpm > 500 else 0
        if sim_speed != self.last_speed:
            speed_str = f"{sim_speed:>3}"
            self.display.draw_7seg_number(130, 95, speed_str, AMBER, BG_COLOR, w=24, h=42, t=5, gap=6)
            self.last_speed = sim_speed

        # --- 3. Odometer & Trip Hours Integration ---
        now_ms = time.ticks_ms()
        dt = time.ticks_diff(now_ms, self.last_time_ms) / 1000.0
        self.last_time_ms = now_ms

        if dt > 0:
            if sim_speed > 0:
                self.main_odo_miles += (sim_speed / 3600.0) * dt
            if clamped_rpm > 100:
                self.trip_hours += dt / 3600.0

            odo_str = f"{int(self.main_odo_miles):05d}mi {self.trip_hours:.1f}h"
            if odo_str != self.last_odo_str:
                self.display.draw_text(108, 179, odo_str, WHITE, color565(20, 20, 20), size=1)
                self.last_odo_str = odo_str

        # --- 4. Coolant Temperature Bar Update ---
        active_t = max(0, min(7, int((temp / 100.0) * 7)))
        if active_t != self.last_temp_bars:
            for i in range(7):
                bx = 35 + (i * 6)
                if i < active_t:
                    col = RED if i >= 5 else AMBER
                else:
                    col = BG_BAR
                self.display.fill_rect(bx, 170, 4, 10, col)
            self.last_temp_bars = active_t

        # --- 5. Fuel Bar Update ---
        active_f = max(0, min(7, int((fuel / 100.0) * 7)))
        if active_f != self.last_fuel_bars:
            for i in range(7):
                bx = 248 + (i * 6)
                if i < active_f:
                    col = RED if active_f <= 2 else AMBER
                else:
                    col = BG_BAR
                self.display.fill_rect(bx, 170, 4, 10, col)
            self.last_fuel_bars = active_f


def run_dash():
    """Main entrypoint for ESP32 hardware and Wokwi simulation."""
    print("Initializing ESP32 Digital Mini Bike Dash...")

    # Hardware SPI setup (matches diagram.json)
    # SCK=GPIO18, MOSI=GPIO23, MISO=GPIO19
    spi = SPI(
        1,
        baudrate=32000000,
        sck=Pin(18),
        mosi=Pin(23),
        miso=Pin(19),
    )

    # Display control pins
    # CS=GPIO15, DC=GPIO2, RST=GPIO4
    display = ili9341.ILI9341(
        spi=spi,
        cs=Pin(15),
        dc=Pin(2),
        rst=Pin(4),
        width=320,
        height=240,
        rotation=90,
    )

    # Input Sensors & Controls (simulated via potentiometers / push button in Wokwi)
    pot_rpm = ADC(Pin(34))
    pot_rpm.atten(ADC.ATTN_11DB)  # Full range ~0 - 3.3V

    pot_aux = ADC(Pin(35))
    pot_aux.atten(ADC.ATTN_11DB)

    btn_mode = Pin(21, Pin.IN, Pin.PULL_UP)

    # Initialize Cluster
    cluster = S2000ClusterESP32(display)
    cluster.draw_static_base()

    print("Dash running! Turn RPM potentiometer to accelerate.")

    last_btn_state = 1
    sweep_rpm = 0
    sweep_dir = 1

    # Startup Tachometer Sweep effect (like a real Honda sports car cluster on ignition ON)
    print("Running gauge startup sweep...")
    for sweep_val in list(range(0, 11500, 400)) + list(range(11500, -1, -400)):
        cluster.update(sweep_val, temp=50, fuel=80)
        time.sleep_ms(15)

    # Main telemetry loop
    while True:
        # Read simulated RPM from Potentiometer (0..65535 -> 0..11500)
        pot_val = pot_rpm.read_u16()
        current_rpm = int((pot_val / 65535.0) * 11500)

        # Read Aux potentiometer for coolant temp (0..100)
        aux_val = pot_aux.read_u16()
        current_temp = int((aux_val / 65535.0) * 100)
        current_fuel = 85  # Default fuel percentage

        # Check button press (active low)
        btn_state = btn_mode.value()
        if btn_state == 0 and last_btn_state == 1:
            print("Cluster mode button pressed!")
            # Re-run startup sweep or swap mode
            cluster.draw_static_base()
            time.sleep_ms(200)
        last_btn_state = btn_state

        # Update display
        cluster.update(current_rpm, temp=current_temp, fuel=current_fuel)
        time.sleep_ms(30)  # Target ~30-35 FPS


if __name__ == "__main__":
    run_dash()
