import tkinter as tk

from clusters.ek_civic_cluster import EKCivicCluster
from clusters.s2000_cluster import S2000Cluster
from clusters.del_sol_cluster import DelSolCluster



class ClusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Bike Dash Simulator")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)

        self.cluster_mode = "s2000"
        self.current_rpm = 0
        self.current_temp = 45
        self.current_fuel = 85

        self.WIDTH = 850
        self.HEIGHT = 420

        self.top_frame = tk.Frame(root, bg="#050505")
        self.top_frame.pack(fill="x", pady=(10, 0))

        self.toggle_btn = tk.Button(
            self.top_frame,
            text="Switch to EK Civic Cluster",
            command=self.toggle_cluster,
            bg="#222222",
            fg="#ffffff",
            activebackground="#444444",
            activeforeground="#ffffff",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )
        self.toggle_btn.pack()

        self.canvas = tk.Canvas(
            root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg="#0b0b0b",
            highlightthickness=2,
            highlightbackground="#222222",
        )
        self.canvas.pack(pady=10, padx=20)

        self.speed_label = tk.Label(
            self.canvas, text="0", font=("Consolas", 68, "bold"),
            fg="#ffb400", bg="#0b0b0b"
        )
        self.speed_window = self.canvas.create_window(425, 245, window=self.speed_label)

        self.info_text = self.canvas.create_text(
            425, 395,
            text="[ Mouse X = RPM | Scroll Wheel = Temp/Battery | Click = Swap Cluster ]",
            fill="#666666",
            font=("Arial", 9, "italic"),
        )

        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", lambda e: self.toggle_cluster())
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.clusters = {
            "s2000": S2000Cluster(self, self.canvas),
            "ek_civic": EKCivicCluster(self, self.canvas),
            "del_sol": DelSolCluster(self, self.canvas),
        }

        self.draw_static_base()
        self.update_cluster(0)

    def toggle_cluster(self):
        if self.cluster_mode == "s2000":
            self.cluster_mode = "ek_civic"
            self.toggle_btn.config(text="Switch to Del Sol Cluster")
            self.root.title("Honda EK Civic Cluster")
        elif self.cluster_mode == "ek_civic":
            self.cluster_mode = "del_sol"
            self.toggle_btn.config(text="Switch to S2000 Cluster")
            self.root.title("Honda Del Sol Cluster")
        else:  # del_sol
            self.cluster_mode = "s2000"
            self.toggle_btn.config(text="Switch to EK Civic Cluster")
            self.root.title("Honda S2000 AP1 Cluster")

        self.draw_static_base()
        self.update_cluster(self.current_rpm)

    def draw_static_base(self):
        self.canvas.delete("all")
        self.clusters[self.cluster_mode].draw_static_base()

    def on_mouse_move(self, event):
        min_x, max_x = 110, 740
        clamped_x = max(min_x, min(event.x, max_x))
        percentage = (clamped_x - min_x) / float(max_x - min_x)
        self.current_rpm = percentage * 11500
        self.update_cluster(self.current_rpm)

    def on_mouse_wheel(self, event):
        step = 5 if event.delta > 0 else -5
        self.current_temp = max(0, min(100, self.current_temp + step))
        self.current_fuel = max(0, min(100, self.current_fuel - step))
        self.update_cluster(self.current_rpm)

    def update_cluster(self, rpm):
        self.clusters[self.cluster_mode].update_cluster(rpm)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClusterApp(root)
    root.mainloop()
