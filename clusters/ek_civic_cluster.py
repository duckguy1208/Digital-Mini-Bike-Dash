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

        # --- RIGHT DIAL (FUEL & TEMP COMBINED) ---
        self.draw_analog_dial(680, 200, 100, "")

        # Pivot locations inside the circle
        f_px, f_py = 605, 200  # Fuel pivot (left side)
        t_px, t_py = 755, 200  # Temp pivot (right side)

        # Labels sitting near outer edges
        self.canvas.create_text(f_px + 5, f_py - 35, text="F", fill="#e0e0e0", font=("Eurostile", 15, "bold"))
        self.canvas.create_text(f_px + 5, f_py + 35, text="E", fill="#e0e0e0", font=("Eurostile", 10, "bold"))

        self.canvas.create_text(t_px - 5, t_py - 35, text="H", fill="#ff3333", font=("Eurostile", 9, "bold"))
        self.canvas.create_text(t_px - 5, t_py + 35, text="C", fill="#e0e0e0", font=("Eurostile", 9, "bold"))

        # --- SPEEDOMETER (Restored 100 MPH) ---
        self.draw_analog_dial(425, 200, 140, "MPH")
        self.draw_analog_ticks(425, 200, 140, min_val=0, max_val=100, step=10, redline_val=99)

        # --- TACHOMETER (Restored 11k RPM) ---
        self.draw_analog_dial(170, 200, 100, "RPM x1000")
        self.draw_analog_ticks(170, 200, 100, min_val=0, max_val=11, step=1, redline_val=8.2)

    def draw_analog_dial(self, cx, cy, radius, label):
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#080808", outline="#2a2a2a", width=4)
        if label:
            self.canvas.create_text(cx, cy + radius - 35, text=label, fill="#888888", font=("Eurostile", 9, "bold"))

    def draw_analog_ticks(self, cx, cy, radius, min_val, max_val, step=1, redline_val=8.0, show_labels=True):
        start_angle, end_angle = 210, -30
        angle_range = start_angle - end_angle
        total_steps = int((max_val - min_val) / step)

        txt_offset = 36 if radius > 60 else max(10, int(radius * 0.3))
        inner_offset = 22 if radius > 50 else int(radius * 0.45)

        for i in range(total_steps + 1):
            val = min_val + (i * step)
            frac = i / float(total_steps)
            angle = math.radians(start_angle - (frac * angle_range))
            color = "#ff3333" if val >= redline_val else "#e0e0e0"

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - inner_offset) * math.cos(angle)
            y_in = cy - (radius - inner_offset) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill=color, width=2)

            if show_labels:
                x_txt = cx + (radius - txt_offset) * math.cos(angle)
                y_txt = cy - (radius - txt_offset) * math.sin(angle)
                self.canvas.create_text(x_txt, y_txt, text=str(val), fill=color, font=("Eurostile", 10, "bold"))

    def draw_needle(self, cx, cy, length, angle_deg, color="#ffcc00", width=3, tag="needle"):
        rad = math.radians(angle_deg)
        x_end = cx + length * math.cos(rad)
        y_end = cy - length * math.sin(rad)

        self.canvas.create_line(cx, cy, x_end, y_end, fill=color, width=width, tags=tag)
        self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#111111", outline="#333333", width=2, tags=tag)

    def update_cluster(self, rpm):
        self.canvas.delete("needle")

        NEEDLE_COLOR = "#ffcc00"

        # 1. Tachometer Needle (0 to 11k RPM)
        rpm_frac = min(rpm / 11000.0, 1.0)
        tach_angle = 210 - (rpm_frac * 240)
        self.draw_needle(170, 200, 85, tach_angle, color=NEEDLE_COLOR, width=4)

        # 2. Speedometer Needle (0 to 100 MPH)
        simulated_speed = (rpm / 11000.0) * 100 if rpm > 500 else 0
        speed_frac = min(simulated_speed / 100.0, 1.0)
        speed_angle = 210 - (speed_frac * 240)
        self.draw_needle(425, 200, 105, speed_angle, color=NEEDLE_COLOR, width=4)

        # --- FLIPPED SUB-DIAL NEEDLES ---
        f_px, f_py = 605, 200
        t_px, t_py = 755, 200

        # 3. Fuel Needle (Sweeps inward pointing to the right: -40 deg [E] up to 40 deg [F])
        self.canvas.delete("ek_fuel_needle")
        fuel_frac = max(0.0, min(self.app.current_fuel / 100.0, 1.0))
        fuel_angle = -40 + (fuel_frac * 80)
        self.draw_needle(f_px, f_py, 40, fuel_angle, color=NEEDLE_COLOR, width=3, tag="ek_fuel_needle")

        # 4. Temp Needle (Sweeps inward pointing to the left: 220 deg [C] down to 140 deg [H])
        self.canvas.delete("ek_temp_needle")
        temp_frac = max(0.0, min(self.app.current_temp / 100.0, 1.0))
        temp_angle = 220 - (temp_frac * 80)
        self.draw_needle(t_px, t_py, 40, temp_angle, color=NEEDLE_COLOR, width=3, tag="ek_temp_needle")
