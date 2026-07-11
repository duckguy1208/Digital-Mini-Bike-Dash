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
