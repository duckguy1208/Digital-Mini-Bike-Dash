import math
from datetime import datetime
import tkinter as tk

from clusters.base_cluster import BaseCluster


class DelSolCluster(BaseCluster):
    def __init__(self, app, canvas):
        super().__init__(app, canvas)
        if not hasattr(self.app, "main_odo_miles"):
            self.app.main_odo_miles = 0.0
        if not hasattr(self.app, "trip_hours"):
            self.app.trip_hours = 0.0
        # track last update time for odometer distance integration
        self.last_odo_time = datetime.now()

    def draw_static_base(self):
        self.canvas.delete("all")
        # Main panel background (EK grey style)
        self.canvas.config(bg="#0b0b0b")

        self.app.info_text = self.canvas.create_text(
            425, 395,
            text="[ Mouse X = RPM | Scroll Wheel = Temp/Battery | Click = Swap Cluster ]",
            fill="#888888",
            font=("Arial", 9, "italic"),
        )

        try:
            self.app.speed_label.destroy()
        except Exception:
            pass

        # =========================================================
        # 1. INDEPENDENT GAUGE POD BACKGROUNDS (EK Style Dark Faces)
        # =========================================================
        # Tachometer Pod Face (Center: 325, 190, Radius: 118)
        self.canvas.create_oval(
            325 - 118, 190 - 118, 325 + 118, 190 + 118,
            fill="#080808", outline="#2a2a2a", width=4
        )

        # Speedometer Pod Face (Center: 555, 190, Radius: 118)
        self.canvas.create_oval(
            555 - 118, 190 - 118, 555 + 118, 190 + 118,
            fill="#080808", outline="#2a2a2a", width=4
        )

        # Fuel & Temp Pod Background Panel (Right side pocket)
        self.canvas.create_rounded_rect = getattr(self, "create_rounded_rect", None) # fallback safe
        self.canvas.create_rectangle(
            690, 140, 790, 360,
            fill="#080808", outline="#2a2a2a", width=4
        )

        # =========================================================
        # 2. FAR LEFT: SRS, CLOCK, AND BUTTONS POD
        # =========================================================

        self.canvas.create_rectangle(120, 290, 180, 315, fill="#1c060a", outline="#2a2a2a", width=2)
        self.clock_text_id = self.canvas.create_text(
            150, 302,
            text="12:00",
            fill="#ffffff",
            font=("Consolas", 12, "bold"),
            tags="digital_clock"
        )

        self.canvas.create_rectangle(120, 320, 165, 335, fill="#141518", outline="#282a30", width=1)
        self.canvas.create_oval(124, 324, 134, 331, fill="#22242a", outline="#444852")
        self.canvas.create_oval(137, 324, 147, 331, fill="#22242a", outline="#444852")
        self.canvas.create_oval(150, 324, 160, 331, fill="#22242a", outline="#444852")

        self.canvas.create_line(195, 320, 205, 305, fill="#111215", width=6)
        self.canvas.create_oval(199, 300, 211, 312, fill="#22242a", outline="#444852")

        # =========================================================
        # 3. TACHOMETER
        # =========================================================
        self.draw_analog_dial(325, 190, 115, "x1000r/min", font_size=8, label_offset=-135)
        self.draw_tachometer_ticks(325, 190, 115)

        # =========================================================
        # 4. SPEEDOMETER & ODOMETERS
        # =========================================================
        self.draw_analog_dial(555, 190, 115, "mph   km/h", font_size=8, label_offset=-80)
        self.canvas.create_text(555, 245, text="UNLEADED\nFUEL ONLY", fill="#ffffff", font=("Arial", 7, "bold"), justify="center")

        self.canvas.create_rectangle(520, 160, 590, 176, fill="#08090b", outline="#333333")
        self.main_odo_text_id = self.canvas.create_text(
            555, 168,
            text=f"{int(self.app.main_odo_miles):06d}",
            fill="#ffffff",
            font=("Consolas", 9, "bold"),
            tags="main_odo"
        )

        self.canvas.create_rectangle(530, 210, 580, 224, fill="#08090b", outline="#333333")
        self.trip_odo_text_id = self.canvas.create_text(
            555, 217,
            text=f"{self.app.trip_hours:.2f} hr",
            fill="#ffffff",
            font=("Consolas", 8, "bold"),
            tags="trip_odo"
        )

        self.draw_speedometer_ticks(555, 190, 115)

        self.canvas.create_line(670, 320, 660, 305, fill="#111215", width=6)
        self.canvas.create_oval(655, 300, 667, 312, fill="#22242a", outline="#444852")

        # =========================================================
        # 5. FAR RIGHT: FUEL & TEMP GAUGES
        # =========================================================
        f_cx, f_cy = 740, 215
        self.canvas.create_text(f_cx + 35, f_cy - 14, text="F", fill="#ffffff", font=("Orbitron", 10, "bold"))
        self.canvas.create_text(f_cx + 33, f_cy + 14, text="E", fill="#ff3333", font=("Orbitron", 10, "bold"))

        for angle_deg in range(-30, 35, 15):
            rad = math.radians(angle_deg)
            is_major = angle_deg in [-30, 30]
            inner_r = 20 if is_major else 24
            tick_color = "#ff3333" if angle_deg >= 15 else "#ffffff"

            x_in = f_cx + inner_r * math.cos(rad)
            y_in = f_cy - inner_r * math.sin(rad)
            x_out = f_cx + 30 * math.cos(rad)
            y_out = f_cy - 30 * math.sin(rad)
            self.canvas.create_line(x_in, y_in, x_out, y_out, fill=tick_color, width=(2 if is_major else 1))

        t_cx, t_cy = 740, 290
        self.canvas.create_text(t_cx + 35, t_cy - 14, text="H", fill="#ff3333", font=("Orbitron", 10, "bold"))
        self.canvas.create_text(t_cx + 33, t_cy + 14, text="C", fill="#ffffff", font=("Orbitron", 10, "bold"))

        for angle_deg in range(-30, 35, 15):
            rad = math.radians(angle_deg)
            is_major = angle_deg in [-30, 30]
            inner_r = 20 if is_major else 24
            tick_color = "#ff3333" if angle_deg <= -15 else "#ffffff"

            x_in = t_cx + inner_r * math.cos(rad)
            y_in = t_cy - inner_r * math.sin(rad)
            x_out = t_cx + 30 * math.cos(rad)
            y_out = t_cy - 30 * math.sin(rad)
            self.canvas.create_line(x_in, y_in, x_out, y_out, fill=tick_color, width=(2 if is_major else 1))

    def draw_tachometer_ticks(self, cx, cy, radius):
        start_angle, end_angle = 180, -50
        angle_range = start_angle - end_angle

        red_start_frac = 8.2 / 11.0
        red_end_frac = 1.0
        
        for r_step in range(12):
            frac = red_start_frac + (r_step / 11.0) * (red_end_frac - red_start_frac)
            ang = math.radians(start_angle - (frac * angle_range))
            x_out = cx + (radius - 12) * math.cos(ang)
            y_out = cy - (radius - 12) * math.sin(ang)
            x_in = cx + (radius - 38) * math.cos(ang)
            y_in = cy - (radius - 38) * math.sin(ang)
            self.canvas.create_line(x_out, y_out, x_in, y_in, fill="#ff3300", width=3)

        for i in range(12):
            frac = i / 11.0
            angle = math.radians(start_angle - (frac * angle_range))

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - 22) * math.cos(angle)
            y_in = cy - (radius - 22) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill="#ffffff", width=2)

            x_txt = cx + (radius - 34) * math.cos(angle)
            y_txt = cy - (radius - 34) * math.sin(angle)

            txt_color = "#ff3333" if i >= 9 else "#ffffff"
            self.canvas.create_text(
                x_txt, y_txt, text=str(i),
                fill=txt_color, font=("Orbitron", 12, "bold")
            )

    def draw_speedometer_ticks(self, cx, cy, radius):
        start_angle, end_angle = 180, -50
        angle_range = start_angle - end_angle

        for val in range(0, 101, 10):
            frac = val / 100.0
            angle = math.radians(start_angle - (frac * angle_range))

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - 22) * math.cos(angle)
            y_in = cy - (radius - 22) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill="#ffffff", width=2)

            x_txt = cx + (radius - 34) * math.cos(angle)
            y_txt = cy - (radius - 34) * math.sin(angle)

            self.canvas.create_text(
                x_txt, y_txt, text=str(val),
                fill="#ffffff", font=("Orbitron", 11, "bold")
            )

        for val in range(5, 100, 10):
            frac = val / 100.0
            angle = math.radians(start_angle - (frac * angle_range))

            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - 16) * math.cos(angle)
            y_in = cy - (radius - 16) * math.sin(angle)

            self.canvas.create_line(x_out, y_out, x_in, y_in, fill="#aaaaaa", width=1)

    def draw_analog_dial(self, cx, cy, radius, label, font_size=9, label_offset=-35):
        if label:
            self.canvas.create_text(
                cx, cy + radius + label_offset,
                text=label, fill="#888888", font=("Orbitron", font_size, "bold")
            )

    def draw_needle(self, cx, cy, length, angle_deg, color="#ffffff", width=3, tag="needle"):
        rad = math.radians(angle_deg)
        x_end = cx + length * math.cos(rad)
        y_end = cy - length * math.sin(rad)

        self.canvas.create_line(cx, cy, x_end, y_end, fill=color, width=width, tags=tag)
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#111215", outline="#282a30", width=2, tags=tag)

    def update_cluster(self, rpm):
        self.canvas.delete("needle")

        NEEDLE_COLOR = "#ffffff"

        now_str = datetime.now().strftime("%I:%M").lstrip("0")
        self.canvas.itemconfig(self.clock_text_id, text=now_str)

        simulated_speed = (rpm / 11000.0) * 100 if rpm > 500 else 0

        # Update odometers based on the displayed speed (mph) and elapsed time
        now = datetime.now()
        dt = (now - getattr(self, "last_odo_time", now)).total_seconds()
        self.last_odo_time = now

        if simulated_speed > 0 and dt > 0:
            # distance (miles) = speed (mph) * time (hours)
            distance_increment = (simulated_speed / 3600.0) * dt
            self.app.main_odo_miles += distance_increment
            # trip is an hour meter: only count when engine is running (>100 RPM)
            if rpm > 100:
                self.app.trip_hours += (dt / 3600.0)

            self.canvas.itemconfig(self.main_odo_text_id, text=f"{int(self.app.main_odo_miles):06d}")
            self.canvas.itemconfig(self.trip_odo_text_id, text=f"{self.app.trip_hours:.2f} hr")

        # Tachometer Needle
        rpm_frac = min(rpm / 11000.0, 1.0)
        tach_angle = 180 - (rpm_frac * 230)
        self.draw_needle(325, 190, 88, tach_angle, color=NEEDLE_COLOR, width=3)

        # Speedometer Needle
        speed_frac = min(simulated_speed / 100.0, 1.0)
        speed_angle = 180 - (speed_frac * 230)
        self.draw_needle(555, 190, 88, speed_angle, color=NEEDLE_COLOR, width=3)

        # Fuel Needle
        self.canvas.delete("delsol_fuel_needle")
        fuel_frac = max(0.0, min(self.app.current_fuel / 100.0, 1.0))
        fuel_angle = 30 - (fuel_frac * 60)
        self.draw_needle(740, 215, 28, fuel_angle, color=NEEDLE_COLOR, width=2, tag="delsol_fuel_needle")

        # Temp Needle
        self.canvas.delete("delsol_temp_needle")
        temp_frac = max(0.0, min(self.app.current_temp / 100.0, 1.0))
        temp_angle = -30 + (temp_frac * 60)
        self.draw_needle(740, 290, 28, temp_angle, color=NEEDLE_COLOR, width=2, tag="delsol_temp_needle")
