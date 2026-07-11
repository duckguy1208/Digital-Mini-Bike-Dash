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
            425, 395, text="[ Move mouse left/right to rev engine | Click anywhere to swap cluster ]", 
            fill="#666666", font=("Arial", 9, "italic")
        )

        # Bindings
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", lambda e: self.toggle_cluster())

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

    # --- YOUR CUSTOM S2000 DIGITAL GEOMETRY ---
    def get_s2000_arc(self, t):
        """Calculates point on arc, normal vector, and bar coordinates for any progress t (0.0 to 1.0)."""
        x1 = 110 + (t * 630)
        arc_height = math.sin(t * math.pi) * 40
        y1 = 140 - arc_height
        
        dx = 1.0
        dy = -math.cos(t * math.pi) * (45 * math.pi / 630)
        length = math.hypot(dx, dy)
        
        nx, ny = -dy / length, dx / length  # Normal vector pointing downwards/inwards
        
        bar_length = 34
        x2 = x1 + nx * bar_length
        y2 = y1 + ny * bar_length
        
        return x1, y1, x2, y2, nx, ny

    # --- DRAWING ROUTINES ---
    def draw_static_base(self):
        self.canvas.delete("all")
        
        # Re-create help footer
        self.info_text = self.canvas.create_text(
            425, 395, text="[ Move mouse left/right to rev engine | Click anywhere to swap cluster ]", 
            fill="#666666", font=("Arial", 9, "italic")
        )

        if self.cluster_mode == "s2000":
            self.canvas.config(bg="#0b0b0b")

            # Ensure no previous speed label widget remains
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

            # Temp Gauge (Left Side) - Horizontal Right to Left (H on Right, C on Left)
            self.canvas.create_text(110, 310, text="C", fill="#ffaa00", font=("Arial", 11, "bold"))
            self.canvas.create_text(175, 310, text="H", fill="#ffaa00", font=("Arial", 11, "bold"))
            for i in range(7):
                x = 160 - (i * 7)
                self.canvas.create_rectangle(x, 303, x - 4, 317, fill="#221500", outline="")

            # Fuel Gauge (Right Side) - Horizontal Right to Left (F on Right, E on Left)
            self.canvas.create_text(675, 310, text="F", fill="#ffaa00", font=("Arial", 11, "bold"))
            self.canvas.create_text(740, 310, text="E", fill="#ffaa00", font=("Arial", 11, "bold"))
            for i in range(7):
                x = 725 - (i * 7)
                self.canvas.create_rectangle(x, 303, x - 4, 317, fill="#221500", outline="")

            # Unlit Background LED Bars
            for i in range(self.NUM_BARS):
                t = i / float(self.NUM_BARS - 1)
                x1, y1, x2, y2, _, _ = self.get_s2000_arc(t)
                self.canvas.create_line(x1, y1, x2, y2, fill="#221800", width=6, tags="bg_bars")

            # Draw Tick Marks & Numbers BELOW the Tachometer Arc (Step 0 to 22)
            for step in range(0, 23):
                rpm_val = step * 0.5
                t = rpm_val / 11.0
                
                x1, y1, x2, y2, nx, ny = self.get_s2000_arc(t)
                
                is_whole_num = (step % 2 == 0)
                color = "#ff3333" if rpm_val >= 10 else "#ffaa00"
                
                if is_whole_num:
                    # Major Tick Mark below segment
                    tx = x2 + nx * 10
                    ty = y2 + ny * 10
                    self.canvas.create_line(x2, y2, tx, ty, fill=color, width=2)
                    
                    # Number Positioned below the major tick
                    num = int(rpm_val)
                    lbl_x = x2 + nx * 25
                    lbl_y = y2 + ny * 25
                    self.canvas.create_text(lbl_x, lbl_y, text=str(num), fill=color, font=("Arial", 11, "bold"))
                else:
                    # Minor Tick Mark
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

        # Right Gauge (Temp & Fuel)
        self.draw_analog_dial(680, 200, 100, "TEMP / FUEL")
        self.canvas.create_text(640, 160, text="C", fill="#e0e0e0", font=("Arial", 10, "bold"))
        self.canvas.create_text(640, 230, text="H", fill="#ff3333", font=("Arial", 10, "bold"))
        self.canvas.create_text(720, 160, text="F", fill="#e0e0e0", font=("Arial", 10, "bold"))
        self.canvas.create_text(720, 230, text="E", fill="#e0e0e0", font=("Arial", 10, "bold"))
        self.draw_needle(680, 200, 80, 210, color="#ffaa00", width=2) # Temp Needle
        self.draw_needle(680, 200, 80, 330, color="#ffaa00", width=2) # Fuel Needle

        # Center Gauge (Tachometer)
        self.draw_analog_dial(425, 200, 140, "RPM x1000")
        self.draw_analog_ticks(425, 200, 140, min_val=0, max_val=11, redline_val=8.2)

        # Left Gauge (Speedometer)
        self.draw_analog_dial(170, 200, 100, "MPH")
        self.draw_analog_ticks(170, 200, 100, min_val=0, max_val=14, step=2, redline_val=99)

    def draw_analog_dial(self, cx, cy, radius, label):
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#080808", outline="#2a2a2a", width=4)
        self.canvas.create_text(cx, cy + radius - 35, text=label, fill="#888888", font=("Arial", 9, "bold"))

    def draw_analog_ticks(self, cx, cy, radius, min_val, max_val, step=1, redline_val=8.0):
        start_angle, end_angle = 210, -30
        angle_range = start_angle - end_angle
        total_steps = int((max_val - min_val) / step)
        
        for i in range(total_steps + 1):
            val = min_val + (i * step)
            frac = i / float(total_steps)
            angle = math.radians(start_angle - (frac * angle_range))
            color = "#ff3333" if val >= redline_val else "#e0e0e0"
            
            x_out = cx + (radius - 10) * math.cos(angle)
            y_out = cy - (radius - 10) * math.sin(angle)
            x_in = cx + (radius - 22) * math.cos(angle)
            y_in = cy - (radius - 22) * math.sin(angle)
            
            self.canvas.create_line(x_out, y_out, x_in, y_in, fill=color, width=2)
            
            x_txt = cx + (radius - 36) * math.cos(angle)
            y_txt = cy - (radius - 36) * math.sin(angle)
            self.canvas.create_text(x_txt, y_txt, text=str(val), fill=color, font=("Arial", 10, "bold"))

    def draw_needle(self, cx, cy, length, angle_deg, color="#ffaa00", width=3, tag="needle"):
        rad = math.radians(angle_deg)
        x_end = cx + length * math.cos(rad)
        y_end = cy - length * math.sin(rad)
        
        self.canvas.create_line(cx, cy, x_end, y_end, fill=color, width=width, tags=tag)
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#222", outline="#ffaa00", width=2, tags=tag)

    # --- ENGINE SIMULATION & MOUSE INPUT ---
    def on_mouse_move(self, event):
        min_x, max_x = 110, 740
        clamped_x = max(min_x, min(event.x, max_x))
        percentage = (clamped_x - min_x) / float(max_x - min_x)
        self.current_rpm = percentage * 11500
        self.update_cluster(self.current_rpm)

    def update_cluster(self, rpm):
        if self.cluster_mode == "s2000":
            # Digital S2000 Bar Updates
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
            self.speed_label.config(text=str(simulated_speed))
        else:
            # Analog Del Sol Sweeping Needles
            self.canvas.delete("needle")
            
            # Tachometer Needle
            rpm_frac = min(rpm / 11000.0, 1.0)
            tach_angle = 210 - (rpm_frac * 240)
            self.draw_needle(425, 200, 105, tach_angle, color="#ffaa00", width=4)

            # Speedometer Needle
            simulated_speed = (rpm / 11000.0) * 140 if rpm > 500 else 0
            speed_frac = min(simulated_speed / 140.0, 1.0)
            speed_angle = 210 - (speed_frac * 240)
            self.draw_needle(170, 200, 75, speed_angle, color="#ffaa00", width=3)

            # Static Temp / Fuel Needles
            self.draw_needle(680, 200, 70, 195, color="#ffaa00", width=2)
            self.draw_needle(680, 200, 70, -15, color="#ffaa00", width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusterApp(root)
    root.mainloop()

'''
import tkinter as tk
import math

class S2000Cluster:
    def __init__(self, root):
        self.root = root
        self.root.title("Honda S2000 Digital Cluster (11k RPM)")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)
        
        # Dimensions and Constants
        self.WIDTH = 850
        self.HEIGHT = 400
        self.MAX_RPM = 11000
        self.NUM_BARS = 60
        
        # Dashboard Canvas
        self.canvas = tk.Canvas(
            root, width=self.WIDTH, height=self.HEIGHT, 
            bg="#0b0b0b", highlightthickness=2, highlightbackground="#222222"
        )
        self.canvas.pack(pady=20, padx=20)
        
        # Speedometer Display
        self.speed_label = tk.Label(
            self.canvas, text="0", font=("Consolas", 68, "bold"), 
            fg="#ffb400", bg="#0b0b0b"
        )
        self.canvas.create_window(425, 245, window=self.speed_label)
        
        self.canvas.create_text(
            550, 280, text="mph", fill="#ffaa00", font=("Arial", 14, "bold")
        )

        # Draw Base Elements
        self.draw_static_elements()
        
        # Bind Mouse Movement
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Initial render
        self.update_cluster(0)

    def get_arc_geometry(self, t):
        """Calculates point on arc, normal vector, and bar coordinates for any progress t (0.0 to 1.0)."""
        x1 = 110 + (t * 630)
        arc_height = math.sin(t * math.pi) * 40
        y1 = 140 - arc_height
        
        dx = 1.0
        dy = -math.cos(t * math.pi) * (45 * math.pi / 630)
        length = math.hypot(dx, dy)
        
        nx, ny = -dy / length, dx / length  # Normal vector pointing downwards/inwards
        
        bar_length = 34
        x2 = x1 + nx * bar_length
        y2 = y1 + ny * bar_length
        
        return x1, y1, x2, y2, nx, ny

    def get_bar_coordinates(self, index):
        t = index / float(self.NUM_BARS - 1)
        x1, y1, x2, y2, _, _ = self.get_arc_geometry(t)
        return x1, y1, x2, y2

    def draw_static_elements(self):
        # Temp Gauge (Left Side) - Horizontal Right to Left (H on Right, C on Left)
        self.canvas.create_text(110, 310, text="C", fill="#ffaa00", font=("Arial", 11, "bold"))
        self.canvas.create_text(175, 310, text="H", fill="#ffaa00", font=("Arial", 11, "bold"))
        for i in range(7):
            x = 160 - (i * 7)
            self.canvas.create_rectangle(x, 303, x - 4, 317, fill="#221500", outline="")

        # Fuel Gauge (Right Side) - Horizontal Right to Left (F on Right, E on Left)
        self.canvas.create_text(675, 310, text="F", fill="#ffaa00", font=("Arial", 11, "bold"))
        self.canvas.create_text(740, 310, text="E", fill="#ffaa00", font=("Arial", 11, "bold"))
        for i in range(7):
            x = 725 - (i * 7)
            self.canvas.create_rectangle(x, 303, x - 4, 317, fill="#221500", outline="")

        # Unlit Background LED Bars
        for i in range(self.NUM_BARS):
            x1, y1, x2, y2 = self.get_bar_coordinates(i)
            self.canvas.create_line(x1, y1, x2, y2, fill="#221800", width=6)

        # Draw Tick Marks & Numbers BELOW the Tachometer Arc
        # Ticks generated every 0.5 RPM step from 0.5 to 11.0
        for step in range(0, 23):
            rpm_val = step * 0.5
            t = rpm_val / 11.0
            
            x1, y1, x2, y2, nx, ny = self.get_arc_geometry(t)
            
            is_whole_num = (step % 2 == 0)
            color = "#ff3333" if rpm_val >= 9 else "#ffaa00"
            
            if is_whole_num:
                # Major Tick Mark below segment
                tx = x2 + nx * 10
                ty = y2 + ny * 10
                self.canvas.create_line(x2, y2, tx, ty, fill=color, width=2)
                
                # Number Positioned below the major tick
                num = int(rpm_val)
                lbl_x = x2 + nx * 25
                lbl_y = y2 + ny * 25
                self.canvas.create_text(lbl_x, lbl_y, text=str(num), fill=color, font=("Arial", 11, "bold"))
            else:
                # Minor Tick Mark (halfway RPMs like 0.5, 1.5, 2.5...)
                tx = x2 + nx * 4
                ty = y2 + ny * 4
                self.canvas.create_line(x2, y2, tx, ty, fill=color, width=1)

    def on_mouse_move(self, event):
        min_x, max_x = 110, 740
        clamped_x = max(min_x, min(event.x, max_x))
        percentage = (clamped_x - min_x) / float(max_x - min_x)
        current_rpm = percentage * 11500  # Allows revving past 11k redline
        self.update_cluster(current_rpm)

    def update_cluster(self, rpm):
        self.canvas.delete("active_bars")
        active_count = int((rpm / float(self.MAX_RPM)) * self.NUM_BARS)
        
        for i in range(min(active_count, self.NUM_BARS)):
            x1, y1, x2, y2 = self.get_bar_coordinates(i)
            segment_rpm = (i / float(self.NUM_BARS)) * self.MAX_RPM
            
            # RPM Color Bands
            if segment_rpm >= 10000:
                color = "#ff1a1a"  # Redline (10k+)
            elif segment_rpm >= 9000:
                color = "#ff6600"  # VTEC zone (9k - 10k)
            else:
                color = "#ffaa00"  # Amber (0 - 9k)
                
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=6, tags="active_bars")

        simulated_speed = int((rpm / 11000.0) * 145) if rpm > 500 else 0
        self.speed_label.config(text=str(simulated_speed))

if __name__ == "__main__":
    root = tk.Tk()
    app = S2000Cluster(root)
    root.mainloop()
'''