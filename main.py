import tkinter as tk

root = tk.Tk()
root.title("Dashboard Simulator (No Hardware Needed)")
root.geometry("1024x600")
root.configure(bg='black')

canvas = tk.Canvas(root, width=1024, height=600, bg='black', highlightthickness=0)
canvas.pack()

# Global tracking variables
current_layout = "s2000"
simulated_rpm = 0

# Create structural UI layers
rpm_bar = canvas.create_polygon(0, 0, 0, 0, fill='yellow')
rpm_arc = canvas.create_arc(362, 150, 662, 450, start=225, extent=0, style='arc', outline='red', width=8)
text_label = canvas.create_text(512, 500, text="RPM: 0", font=("Arial", 30), fill="white")
mode_label = canvas.create_text(512, 50, text="Layout: S2000 (Tap Screen to Swap)", font=("Arial", 18), fill="cyan")

def update_simulated_ui():
    """ Redraws the screen based on the simulated_rpm variable """
    max_rpm = 11000
    
    # Update the text readout
    canvas.itemconfig(text_label, text=f"RPM: {simulated_rpm}")
    
    if current_layout == "s2000":
        # Hide the circular arc, calculate and show the sweeping bar
        canvas.itemconfig(rpm_arc, extent=0)
        max_width = 800
        current_width = (simulated_rpm / max_rpm) * max_width
        points = [112, 300,  112 + current_width, 300,  112 + current_width, 220,  112, 260]
        canvas.coords(rpm_bar, *points)
        
        # Color safety zones
        color = "red" if simulated_rpm >= 8500 else ("orange" if simulated_rpm >= 6000 else "yellow")
        canvas.itemconfig(rpm_bar, fill=color)
        
    elif current_layout == "delsol":
        # Hide the sweeping bar, calculate and show the circular arc
        canvas.coords(rpm_bar, 0, 0, 0, 0)
        total_degrees = -270
        current_angle = (simulated_rpm / max_rpm) * total_degrees
        canvas.itemconfig(rpm_arc, extent=current_angle)
        
        color = "red" if simulated_rpm >= 8500 else "orange"
        canvas.itemconfig(rpm_arc, outline=color)

def handle_mouse_move(event):
    """ Tracks your mouse cursor X position to fake engine throttle """
    global simulated_rpm
    # Map mouse X coordinates (0 to 1024) to RPM (0 to 11000)
    percentage = event.x / 1024
    if percentage < 0: percentage = 0
    if percentage > 1: percentage = 1
    
    simulated_rpm = int(percentage * 11000)
    update_simulated_ui()

def handle_screen_tap(event):
    """ Swaps layouts on click/tap """
    global current_layout
    if current_layout == "s2000":
        current_layout = "delsol"
        canvas.itemconfig(mode_label, text="Layout: Del Sol VTEC")
    else:
        current_layout = "s2000"
        canvas.itemconfig(mode_label, text="Layout: S2000")
    update_simulated_ui()

# Bind mouse movements and clicks for desktop testing
root.bind("<Motion>", handle_mouse_move)
root.bind("<Button-1>", handle_screen_tap)

root.mainloop()
