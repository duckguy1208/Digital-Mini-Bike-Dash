import math
import tkinter as tk

from clusters.base_cluster import BaseCluster


class EKCivicCluster(BaseCluster):
    def __init__(self, app, canvas):
        super().__init__(app, canvas)

    def draw_static_base(self):
        self.canvas.delete("all")
        self.canvas.config(bg="#111215")

        self.app.info_text = self.canvas.create_text(
            425, 395,
            text="[ Mouse X = RPM | Scroll Wheel = Temp/Battery | Click = Swap Cluster ]",
            fill="#666666",
            font=("Arial", 9, "italic"),
        )

        try:
            self.app.speed_label.destroy()
        except Exception:
            pass

        # --- COMBINED FUEL/TEMP GAUGE ---
        # Draw the outer circular face for the right-side gauge.
        self.draw_analog_dial(680, 200, 100, "")

        # Pivot points for the fuel and temperature needles.
        f_px, f_py = 605, 200  # Fuel needle pivot on the left side of the dial
        t_px, t_py = 755, 200  # Temperature needle pivot on the right side of the dial

        # Add the letter labels around the fuel and temperature dial.
        self.canvas.create_text(f_px + 20, f_py - 42, text="F", fill="#e0e0e0", font=("Orbitron", 15, "bold"))
        self.canvas.create_text(f_px + 20, f_py + 42, text="E", fill="#e0e0e0", font=("Orbitron", 15, "bold"))

        self.canvas.create_text(t_px - 20, t_py - 42, text="H", fill="#e0e0e0", font=("Orbitron", 15, "bold"))
        self.canvas.create_text(t_px - 20, t_py + 42, text="C", fill="#e0e0e0", font=("Orbitron", 15, "bold"))

        # --- DRAW THE TICK MARKS FOR THE FUEL AND TEMPERATURE DIALS ---
        # 1. Fuel gauge ticks: draw the small marks across the left half of the combined dial.
        # These span from -40° to 40° and are spaced every 10°.
        for angle_deg in range(-40, 41, 10):
            rad = math.radians(angle_deg)
            is_major = (angle_deg in [-40, 0, 40])
            
            # Major ticks extend further inward
            tick_color = "#ff3333" if angle_deg == -40 else "#e0e0e0"
            inner_r = 44 if is_major else 50
            line_w = 2 if is_major else 1
            
            x_in = f_px + inner_r * math.cos(rad)
            y_in = f_py - inner_r * math.sin(rad)
            x_out = f_px + 60 * math.cos(rad)
            y_out = f_py - 60 * math.sin(rad)
            
            self.canvas.create_line(x_in, y_in, x_out, y_out, fill=tick_color, width=line_w)

        # 2. Temperature gauge ticks: draw the marks across the right half of the combined dial.
        # These span from 220° down to 140° and are spaced every 10°.
        for angle_deg in range(140, 221, 10):
            rad = math.radians(angle_deg)
            is_major = (angle_deg in [140, 180, 220])
            
            # Hot zone color (top 20 degrees near 'H')
            color = "#ff3333" if angle_deg < 150 else "#e0e0e0"
            inner_r = 44 if is_major else 50
            line_w = 2 if is_major else 1
            
            x_in = t_px + inner_r * math.cos(rad)
            y_in = t_py - inner_r * math.sin(rad)
            x_out = t_px + 60 * math.cos(rad)
            y_out = t_py - 60 * math.sin(rad)
            
            self.canvas.create_line(x_in, y_in, x_out, y_out, fill=color, width=line_w)

        # --- DRAW THE SPEEDOMETER ---
        # Create the circular speedometer face and its numbered tick marks.
        self.draw_analog_dial(425, 200, 140, "MPH", font_size=9, label_offset=-200)
        self.draw_analog_ticks(425, 200, 140, min_val=0, max_val=100, step=10, redline_val=99, label_font_size=15)

        # --- DRAW THE TACHOMETER ---
        # Create the circular tachometer face and its tick marks, including the highlighted red zone.
        self.draw_analog_dial(170, 200, 100, "RPM x1000r/min", font_size=8, label_offset=-130)
        self.draw_analog_ticks(170, 200, 100, min_val=0, max_val=11, step=1, redline_val=9, red_zone=(9, 11), tick_width=2, label_font_size=12)
        self.write_text(170, 200, text="", fill="#888888", font=("Orbitron", 8, "bold"))

    def draw_analog_dial(self, cx, cy, radius, label, font_size=9, label_offset=-35):
        # Draw the outer ring and fill for a single gauge face.
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#080808", outline="#2a2a2a", width=4)
        if label:
            # Add the gauge label such as MPH or RPM x1000 above the dial face.
            self.canvas.create_text(cx, cy + radius + label_offset, text=label, fill="#888888", font=("Orbitron", font_size, "bold"))

    def draw_analog_ticks(self, cx, cy, radius, min_val, max_val, step=1, redline_val=8.0, show_labels=True, red_zone=None, tick_width=2, label_font_size=15):
        start_angle, end_angle = 210, -30
        angle_range = start_angle - end_angle
        total_steps = int((max_val - min_val) / step)

        txt_offset = 36 if radius > 60 else max(10, int(radius * 0.3))
        inner_offset = 22 if radius > 50 else int(radius * 0.45)
        minor_tick_width = max(1, tick_width // 2)

        # Optional red highlight band for the tachometer's danger zone.
        if red_zone is not None:
            start_val, end_val = red_zone
            start_frac = max(0.0, min(1.0, (start_val - min_val) / float(max_val - min_val)))
            end_frac = max(0.0, min(1.0, (end_val - min_val) / float(max_val - min_val)))
            start_deg = start_angle - (start_frac * angle_range)
            end_deg = start_angle - (end_frac * angle_range)
            self.canvas.create_arc(
                cx - radius + 15,
                cy - radius + 15,
                cx + radius - 15,
                cy + radius - 15,
                start=start_deg,
                extent=end_deg - start_deg,
                outline="#ff3333",
                width= 12,
                style="arc",
            )

        # Draw all tick marks first, then draw the numbers separately so each can be styled independently.
        label_positions = []
        major_step = step
        minor_step = step / 2.0

        for i in range(int((max_val - min_val) / minor_step) + 1):
            val = min_val + (i * minor_step)
            if abs(val - round(val / major_step) * major_step) < 1e-9:
                continue

            frac = (val - min_val) / float(max_val - min_val)
            angle = math.radians(start_angle - (frac * angle_range))

            is_red_zone_value = red_zone is not None and red_zone[0] <= val <= red_zone[1]
            minor_tick_color = "#222222" if is_red_zone_value else ("#222222" if val >= redline_val and val != 100 else "#e0e0e0")

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - inner_offset) * math.cos(angle)
            y_in = cy - (radius - inner_offset) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill=minor_tick_color, width=minor_tick_width)

        for i in range(total_steps + 1):
            val = min_val + (i * step)
            frac = i / float(total_steps)
            angle = math.radians(start_angle - (frac * angle_range))

            is_red_zone_value = red_zone is not None and red_zone[0] <= val <= red_zone[1]
            is_red_tick = val == 9 or val == 11
            tick_color = "#ff3333" if is_red_tick else ("#222222" if is_red_zone_value or (val >= redline_val and val != 100) else "#e0e0e0")
            if val == 11 and red_zone is not None:
                tick_color = "#ff3333"

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - inner_offset) * math.cos(angle)
            y_in = cy - (radius - inner_offset) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill=tick_color, width=tick_width)

            if show_labels:
                x_txt = cx + (radius - txt_offset) * math.cos(angle)
                y_txt = cy - (radius - txt_offset) * math.sin(angle)
                label_color = "#ff3333" if is_red_zone_value else ("#ffffff" if val == 100 else ("#ff3333" if val >= redline_val and val != 100 else "#e0e0e0"))
                label_positions.append((x_txt, y_txt, str(val), label_color))

        if show_labels:
            for x_txt, y_txt, text, label_color in label_positions:
                self.canvas.create_text(x_txt, y_txt, text=text, fill=label_color, font=("Orbitron", label_font_size, "bold"))

    def draw_needle(self, cx, cy, length, angle_deg, color="#ffcc00", width=3, tag="needle"):
        # Draw a gauge needle from the center of the dial to the requested angle.
        rad = math.radians(angle_deg)
        x_end = cx + length * math.cos(rad)
        y_end = cy - length * math.sin(rad)

        self.canvas.create_line(cx, cy, x_end, y_end, fill=color, width=width, tags=tag)
        self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#111111", outline="#333333", width=2, tags=tag)

    def update_cluster(self, rpm):
        self.canvas.delete("needle")

        NEEDLE_COLOR = "#ffcc00"

        # 1. Tachometer needle: move the RPM needle based on the current engine speed.
        rpm_frac = min(rpm / 11000.0, 1.0)
        tach_angle = 210 - (rpm_frac * 240)
        self.draw_needle(170, 200, 85, tach_angle, color=NEEDLE_COLOR, width=4)

        # 2. Speedometer needle: move the speed needle based on a simulated speed value.
        simulated_speed = (rpm / 11000.0) * 100 if rpm > 500 else 0
        speed_frac = min(simulated_speed / 100.0, 1.0)
        speed_angle = 210 - (speed_frac * 240)
        self.draw_needle(425, 200, 105, speed_angle, color=NEEDLE_COLOR, width=4)

        # --- DRAW THE FUEL AND TEMPERATURE NEEDLES ---
        f_px, f_py = 605, 200
        t_px, t_py = 755, 200

        # 3. Fuel needle: map the current fuel level onto the fuel dial's range.
        self.canvas.delete("ek_fuel_needle")
        fuel_frac = max(0.0, min(self.app.current_fuel / 100.0, 1.0))
        fuel_angle = -40 + (fuel_frac * 80)
        self.draw_needle(f_px, f_py, 52, fuel_angle, color=NEEDLE_COLOR, width=3, tag="ek_fuel_needle")

        # 4. Temperature needle: map the current temperature onto the temperature dial's range.
        self.canvas.delete("ek_temp_needle")
        temp_frac = max(0.0, min(self.app.current_temp / 100.0, 1.0))
        temp_angle = 220 - (temp_frac * 80)
        self.draw_needle(t_px, t_py, 52, temp_angle, color=NEEDLE_COLOR, width=3, tag="ek_temp_needle")

