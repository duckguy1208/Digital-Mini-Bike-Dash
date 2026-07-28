import tkinter as tk
import math

class ClusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Honda Digital vs Analog Cluster Simulator")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)
        
        # Current Mode: 's2000' (Digital) or 'delsol' (Analog)
        self.cluster_mode = "s2000"
        
        # Shared Physics State
        self.current_rpm = 0
        self.current_temp = 45  # Temp Percentage (0% = Cold, 100% = Overheating)
        self.current_fuel = 85  # Fuel / Battery Percentage (0% = Empty, 100% = Full)
        
        self.MAX_RPM = 11000
        self.NUM_BARS = 60
        
        self.WIDTH = 850
        self.HEIGHT = 420
        
        # Top Controls
        self.top_frame = tk.Frame(root, bg="#050505")
        self.top_frame.pack(fill="x", pady=(10, 0))
        
        self.toggle_btn = tk.Button(
            self.top_frame, text="Switch to EG Civic Analog Cluster", 
            command=self.toggle_cluster, bg="#222222", fg="#ffffff", 
            activebackground="#444444", activeforeground="#ffffff",
            font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
        )
        self.toggle_btn.pack()

        # Canvas Dashboard
        self.canvas = tk.Canvas(
            root, width=self.WIDTH, height=self.HEIGHT, 
            bg="#0b0b0b", highlightthickness=2, highlightbackground="#222222"
        )
        self.canvas.pack(pady=10, padx=20)
        
        # S2000 Speedometer Window Object
        self.speed_label = tk.Label(
            self.canvas, text="0", font=("Consolas", 68, "bold"), 
            fg="#ffb400", bg="#0b0b0b"
        )
        self.speed_window = self.canvas.create_window(425, 245, window=self.speed_label)

        # Instructions Footer
        self.info_text = self.canvas.create_text(
            425, 395, text="[ Mouse X = RPM | Scroll Wheel = Temp/Battery | Click = Swap Cluster ]", 
            fill="#666666", font=("Arial", 9, "italic")
        )

        # Bindings
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", lambda e: self.toggle_cluster())
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Scroll wheel alters temp/fuel

        # Render initial view
        self.draw_static_base()
        self.update_cluster(0)

    def toggle_cluster(self):
        if self.cluster_mode == "s2000":
            self.cluster_mode = "delsol"
            self.toggle_btn.config(text="Switch to S2000 Digital Cluster")
            self.root.title("Honda EG Civic OEM Analog Cluster")
        else:
            self.cluster_mode = "s2000"
            self.toggle_btn.config(text="Switch to EG Civic Analog Cluster")
            self.root.title("Honda S2000 AP1 Digital Cluster (11k RPM)")
            
        self.draw_static_base()
        self.update_cluster(self.current_rpm)

    # --- S2000 DIGITAL GEOMETRY MATH ---
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

    # --- DRAWING ROUTINES ---
    def draw_static_base(self):
        self.canvas.delete("all")
        
        # Re-create help footer
        self.info_text = self.canvas.create_text(
            425, 395, text="[ Mouse X = RPM | Scroll Wheel = Temp/Battery | Click = Swap Cluster ]", 
            fill="#666666", font=("Arial", 9, "italic")
        )

        if self.cluster_mode == "s2000":
            self.canvas.config(bg="#0b0b0b")

            try:
                self.speed_label.destroy()
            except Exception:
                pass

            # Speedometer Display
            self.speed_label = tk.Label(
                self.canvas, text="0", font=("Consolas", 68, "bold"), 
                fg="#ffb400", bg="#0b0b0b"
            )
            self.speed_window = self.canvas.create_window(425, 245, window=self.speed_label)
            self.canvas.create_text(550, 280, text="mph", fill="#ffaa00", font=("Arial", 14, "bold"))

            # Temp Gauge Labels (Left Side)
            self.canvas.create_text(110, 310, text="C", fill="#ffaa00", font=("Arial", 11, "bold"))
            self.canvas.create_text(175, 310, text="H", fill="#ffaa00", font=("Arial", 11, "bold"))

            # Fuel / Battery Gauge Labels (Right Side) - flipped: E on left, F on right
            self.canvas.create_text(675, 310, text="E", fill="#ffaa00", font=("Arial", 11, "bold"))
            self.canvas.create_text(740, 310, text="F", fill="#ffaa00", font=("Arial", 11, "bold"))

            # Unlit Background LED Bars
            for i in range(self.NUM_BARS):
                t = i / float(self.NUM_BARS - 1)
                x1, y1, x2, y2, _, _ = self.get_s2000_arc(t)
                self.canvas.create_line(x1, y1, x2, y2, fill="#221800", width=6, tags="bg_bars")

            # Draw Tick Marks & Numbers BELOW the Tachometer Arc
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
            return

        # --- EG ANALOG CLUSTER LAYOUT ---
        self.canvas.config(bg="#111215")

        try:
            self.speed_label.destroy()
        except Exception:
            pass

        # Right Gauge Circle (contains two small dials with separate pivots: TEMP and FUEL)
        self.draw_analog_dial(680, 200, 100, "")
        # Small Temp/Fuel pivots (no circles) - pivots next to each other with a vertical gap
        t_px, t_py = 668, 190
        # place fuel pivot inline with temp pivot, slightly lower (vertical gap)
        f_px, f_py = t_px, t_py + 20
        # Temp markers (C/H)
        self.canvas.create_text(t_px, t_py - 32, text="C", fill="#e0e0e0", font=("Arial", 9, "bold"))
        self.canvas.create_text(t_px, t_py + 32, text="H", fill="#ff3333", font=("Arial", 9, "bold"))
        # Fuel markers (E/F) aligned vertically with C/H
        self.canvas.create_text(f_px - 12, t_py - 32, text="E", fill="#e0e0e0", font=("Arial", 9, "bold"))
        self.canvas.create_text(f_px + 12, t_py + 32, text="F", fill="#e0e0e0", font=("Arial", 9, "bold"))

        # Center Gauge (Speedometer) -- swapped with tach
        self.draw_analog_dial(425, 200, 140, "MPH")
        self.draw_analog_ticks(425, 200, 140, min_val=0, max_val=140, step=10, redline_val=99)

        # Left Gauge (Tachometer) -- swapped with speedometer
        self.draw_analog_dial(170, 200, 100, "RPM x1000")
        self.draw_analog_ticks(170, 200, 100, min_val=0, max_val=11, step=1, redline_val=8.2)

    def draw_analog_dial(self, cx, cy, radius, label):
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#080808", outline="#2a2a2a", width=4)
        self.canvas.create_text(cx, cy + radius - 35, text=label, fill="#888888", font=("Arial", 9, "bold"))

    def draw_analog_ticks(self, cx, cy, radius, min_val, max_val, step=1, redline_val=8.0, show_labels=True):
        start_angle, end_angle = 210, -30
        angle_range = start_angle - end_angle
        total_steps = int((max_val - min_val) / step)

        # Dynamic offsets so small dials don't overlap labels/ticks
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

    # --- ENGINE SIMULATION & INPUTS ---
    def on_mouse_move(self, event):
        min_x, max_x = 110, 740
        clamped_x = max(min_x, min(event.x, max_x))
        percentage = (clamped_x - min_x) / float(max_x - min_x)
        self.current_rpm = percentage * 11500
        self.update_cluster(self.current_rpm)

    def on_mouse_wheel(self, event):
        # Mouse wheel up raises Temp & lowers Fuel/Battery; down does the inverse
        step = 5 if event.delta > 0 else -5
        self.current_temp = max(0, min(100, self.current_temp + step))
        self.current_fuel = max(0, min(100, self.current_fuel - step))
        self.update_cluster(self.current_rpm)

    def update_cluster(self, rpm):
        if self.cluster_mode == "s2000":
            # 1. Update Active Tachometer Arc Bars
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

            # 2. Update Digital Speedometer Number
            simulated_speed = int((rpm / 11000.0) * 145) if rpm > 500 else 0
            self.speed_label.config(text=str(simulated_speed))

            # 3. Dynamic Temp Gauge (Left Side, 7 Bars)
            self.canvas.delete("temp_bars")
            active_temp_bars = int((self.current_temp / 100.0) * 7)
            for i in range(7):
                x = 122 + (i * 7)  # Fill left to right toward 'H'
                color = "#ffaa00" if i < active_temp_bars else "#221500"
                if i >= 5 and i < active_temp_bars:
                    color = "#ff1a1a"  # Red warning for high temp
                self.canvas.create_rectangle(x, 303, x + 4, 317, fill=color, outline="", tags="temp_bars")

            # 4. Dynamic Fuel / Battery Gauge (Right Side, 7 Bars) - flipped orientation
            self.canvas.delete("fuel_bars")
            active_fuel_bars = int((self.current_fuel / 100.0) * 7)
            for i in range(7):
                # Fill left to right so the rightmost bars represent FULL (F)
                x = 676 + (i * 7)
                if i < active_fuel_bars:
                    # If overall fuel is very low, show lit bars in red
                    color = "#ff1a1a" if active_fuel_bars <= 2 else "#ffaa00"
                else:
                    color = "#221500"
                self.canvas.create_rectangle(x, 303, x + 4, 317, fill=color, outline="", tags="fuel_bars")

        else:
            # Analog Sweeping Needles
            self.canvas.delete("needle")
            
            # Tachometer Needle (Left Gauge)
            rpm_frac = min(rpm / 11000.0, 1.0)
            tach_angle = 210 - (rpm_frac * 240)
            self.draw_needle(170, 200, 85, tach_angle, color="#ffaa00", width=4)

            # Speedometer Needle (Center Gauge)
            simulated_speed = (rpm / 11000.0) * 140 if rpm > 500 else 0
            speed_frac = min(simulated_speed / 140.0, 1.0)
            speed_angle = 210 - (speed_frac * 240)
            self.draw_needle(425, 200, 105, speed_angle, color="#ffaa00", width=4)

            # Draw Temp Needle at its own pivot (t_px,t_py)
            self.canvas.delete("eg_temp_needle")
            t_px, t_py = 668, 190
            # Map 0-100% to 210 -> -30 so both needles use same angle mapping (parallel)
            temp_angle = 210 - ((self.current_temp / 100.0) * 240)
            self.draw_needle(t_px, t_py, 46, temp_angle, color="#ff3333", width=3, tag="eg_temp_needle")

            # Draw Fuel Needle at its own pivot (f_px,f_py)
            self.canvas.delete("eg_fuel_needle")
            f_px, f_py = 692, 210
            fuel_angle = 210 - ((self.current_fuel / 100.0) * 240)
            self.draw_needle(f_px, f_py, 46, fuel_angle, color="#ffffff", width=3, tag="eg_fuel_needle")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusterApp(root)
    root.mainloop()
