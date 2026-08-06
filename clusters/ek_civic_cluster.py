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

        self.draw_analog_dial(680, 200, 100, "")
        t_px, t_py = 605, 200
        f_px, f_py = 755, 200

        self.canvas.create_text(t_px, t_py, text="F", fill="#e0e0e0", font=("Arial", 9, "bold"))
        self.canvas.create_text(t_px, t_py, text="E", fill="#e0e0e0", font=("Arial", 9, "bold"))
        self.canvas.create_text(f_px, t_py, text="C", fill="#e0e0e0", font=("Arial", 9, "bold"))
        self.canvas.create_text(f_px, t_py, text="H", fill="#ff3333", font=("Arial", 9, "bold"))

        self.draw_analog_dial(425, 200, 140, "MPH")
        self.draw_analog_ticks(425, 200, 140, min_val=0, max_val=140, step=10, redline_val=99)

        self.draw_analog_dial(170, 200, 100, "RPM x1000")
        self.draw_analog_ticks(170, 200, 100, min_val=0, max_val=11, step=1, redline_val=8.2)

    def draw_analog_dial(self, cx, cy, radius, label):
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#080808", outline="#2a2a2a", width=4)
        self.canvas.create_text(cx, cy + radius - 35, text=label, fill="#888888", font=("Arial", 9, "bold"))

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
                self.canvas.create_text(x_txt, y_txt, text=str(val), fill=color, font=("Arial", 10, "bold"))

    def draw_needle(self, cx, cy, length, angle_deg, color="#ffaa00", width=3, tag="needle"):
        rad = math.radians(angle_deg)
        x_end = cx + length * math.cos(rad)
        y_end = cy - length * math.sin(rad)

        self.canvas.create_line(cx, cy, x_end, y_end, fill=color, width=width, tags=tag)
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#222", outline="#ffaa00", width=2, tags=tag)

    def update_cluster(self, rpm):
        self.canvas.delete("needle")

        rpm_frac = min(rpm / 11000.0, 1.0)
        tach_angle = 210 - (rpm_frac * 240)
        self.draw_needle(170, 200, 85, tach_angle, color="#ffaa00", width=4)

        simulated_speed = (rpm / 11000.0) * 140 if rpm > 500 else 0
        speed_frac = min(simulated_speed / 140.0, 1.0)
        speed_angle = 210 - (speed_frac * 240)
        self.draw_needle(425, 200, 105, speed_angle, color="#ffaa00", width=4)

        self.canvas.delete("ek_temp_needle")
        t_px, t_py = 605, 200
        temp_angle = -30 + ((self.app.current_temp / 100.0) * 240)
        self.draw_needle(t_px, t_py, 46, temp_angle, color="#ff3333", width=3, tag="ek_temp_needle")

        self.canvas.delete("ek_fuel_needle")
        f_px, f_py = 755, 200
        fuel_angle = -30 + ((self.app.current_fuel / 100.0) * 240)
        self.draw_needle(f_px, f_py, 46, fuel_angle, color="#ffffff", width=3, tag="ek_fuel_needle")
