import math
from datetime import datetime
import tkinter as tk

from clusters.base_cluster import BaseCluster


class S2000Cluster(BaseCluster):
    def __init__(self, app, canvas):
        super().__init__(app, canvas)
        self.MAX_RPM = 11000
        self.NUM_BARS = 60
        if not hasattr(self.app, "main_odo_miles"):
            self.app.main_odo_miles = 0.0
        if not hasattr(self.app, "trip_hours"):
            self.app.trip_hours = 0.0
        self.last_odo_time = datetime.now()

    def get_s2000_arc(self, t):
        x1 = 110 + (t * 630)
        arc_height = math.sin(t * math.pi) * 40
        y1 = 140 - arc_height

        dx = 1.0
        dy = -math.cos(t * math.pi) * (45 * math.pi / 630)
        length = math.hypot(dx, dy)

        nx, ny = -dy / length, dx / length
        bar_length = 34
        x2 = x1 + nx * bar_length
        y2 = y1 + ny * bar_length

        return x1, y1, x2, y2, nx, ny

    def draw_static_base(self):
        self.canvas.delete("all")
        self.canvas.config(bg="#0b0b0b")

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

        self.app.speed_label = tk.Label(
            self.canvas, text="0", font=("Consolas", 68, "bold"),
            fg="#FF8200", bg="#0b0b0b"
        )
        self.canvas.create_rectangle(347, 305, 502, 325, fill="#FF8200", outline="#FF8200")

        self.app.speed_window = self.canvas.create_window(425, 245, window=self.app.speed_label)

        # main odometer (miles) and trip hours display — centered in the smaller rectangle
        self.main_odo_text_id = self.canvas.create_text(
            385, 313,
            text=f"{int(self.app.main_odo_miles):06d}",
            fill="#000000",
            font=("Consolas", 10, "bold")
        )
        self.trip_text_id = self.canvas.create_text(
            455, 313,
            text=f"{self.app.trip_hours:.2f} hr",
            fill="#000000",
            font=("Consolas", 9, "bold")
        )
        # draw the "mph" and "km/h" labels next to the speed display
        self.canvas.create_text(550, 260, text="mph", fill="#ffaa00", font=("Arial", 14, "bold"))
        self.canvas.create_text(550, 285, text="km/h", fill="#4e3400", font=("Arial", 14, "bold"))

        # draw the "C" and "H" for coolant temp, and "E" and "F" for fuel level
        self.canvas.create_text(110, 285, text="C", fill="#ffaa00", font=("Arial", 11, "bold"))
        self.canvas.create_text(180, 285, text="H", fill="#ffaa00", font=("Arial", 11, "bold"))
        self.canvas.create_text(665, 285, text="E", fill="#ffaa00", font=("Arial", 11, "bold"))
        self.canvas.create_text(732, 285, text="F", fill="#ffaa00", font=("Arial", 11, "bold"))

        for i in range(self.NUM_BARS):
            t = i / float(self.NUM_BARS - 1)
            x1, y1, x2, y2, _, _ = self.get_s2000_arc(t)
            self.canvas.create_line(x1, y1, x2, y2, fill="#221800", width=6, tags="bg_bars")

        for step in range(0, 23):
            rpm_val = step * 0.5
            t = rpm_val / 11.0
            x1, y1, x2, y2, nx, ny = self.get_s2000_arc(t)
            is_whole_num = (step % 2 == 0)
            color = "#ff3333" if rpm_val >= 10 else "#ffaa00"

            if is_whole_num:
                tx = x2 + nx * 10
                ty = y2 + ny * 10
                self.canvas.create_line(x2, y2, tx, ty, fill=color, width=2)

                num = int(rpm_val)
                lbl_x = x2 + nx * 25
                lbl_y = y2 + ny * 25
                self.canvas.create_text(lbl_x, lbl_y, text=str(num), fill=color, font=("Arial", 11, "bold"))
            else:
                tx = x2 + nx * 4
                ty = y2 + ny * 4
                self.canvas.create_line(x2, y2, tx, ty, fill=color, width=1)

    def update_cluster(self, rpm):
        self.canvas.delete("active_bars")
        active_count = int((rpm / float(self.MAX_RPM)) * self.NUM_BARS)

        for i in range(min(active_count, self.NUM_BARS)):
            t = i / float(self.NUM_BARS - 1)
            x1, y1, x2, y2, _, _ = self.get_s2000_arc(t)
            segment_rpm = (i / float(self.NUM_BARS)) * self.MAX_RPM

            if segment_rpm >= 10000:
                color = "#ff1a1a"
            elif segment_rpm >= 9000:
                color = "#ff6600"
            else:
                color = "#ffaa00"

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=6, tags="active_bars")

        simulated_speed = int((rpm / 11000.0) * 145) if rpm > 500 else 0
        self.app.speed_label.config(text=str(simulated_speed))

        # update odometer and trip hours based on displayed speed and elapsed time
        now = datetime.now()
        dt = (now - getattr(self, "last_odo_time", now)).total_seconds()
        self.last_odo_time = now

        if simulated_speed > 0 and dt > 0:
            distance_increment = (simulated_speed / 3600.0) * dt
            self.app.main_odo_miles += distance_increment
            if rpm > 100:
                self.app.trip_hours += (dt / 3600.0)

            try:
                self.canvas.itemconfig(self.main_odo_text_id, text=f"{int(self.app.main_odo_miles):06d}")
                self.canvas.itemconfig(self.trip_text_id, text=f"{self.app.trip_hours:.2f} hr")
            except Exception:
                pass

        self.canvas.delete("temp_bars")
        active_temp_bars = int((self.app.current_temp / 100.0) * 7)
        # move temp bars up to align with the left-side letters (near the tach)
        for i in range(7):
            x = 122 + (i * 7)
            color = "#ffaa00" if i < active_temp_bars else "#221500"
            if i >= 5 and i < active_temp_bars:
                color = "#ff1a1a"
            # raised vertical position (y 275-289)
            self.canvas.create_rectangle(x, 275, x + 4, 289, fill=color, outline="", tags="temp_bars")

        self.canvas.delete("fuel_bars")
        active_fuel_bars = int((self.app.current_fuel / 100.0) * 7)
        # move fuel bars up to align with the right-side letters (near the tach)
        for i in range(7):
            x = 676 + (i * 7)
            if i < active_fuel_bars:
                color = "#ff1a1a" if active_fuel_bars <= 2 else "#ffaa00"
            else:
                color = "#221500"
            # raised vertical position (y 275-289)
            self.canvas.create_rectangle(x, 275, x + 4, 289, fill=color, outline="", tags="fuel_bars")
