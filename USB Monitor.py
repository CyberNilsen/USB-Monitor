import tkinter as tk
from tkinter import ttk
import threading
import time
import platform
import subprocess
import re
import os
from PIL import Image, ImageTk, ImageDraw

usb_devices = {}
device_lock = threading.Lock()

monitoring = True

class USBMonitor:
    def __init__(self):
        self.system = platform.system()
        
    def get_current_devices(self):
        """Get a list of currently connected USB devices"""
        devices = {}
        
        if self.system == "Windows":
            cmd = "powershell -Command \"Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'USB' -or $_.Class -eq 'DiskDrive' -or $_.Class -eq 'USBDevice' } | Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Csv -NoTypeInformation\""
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1: 
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip('"').split('","')
                        if len(parts) >= 4:
                            status, class_name, name, instance_id = parts
                            devices[instance_id] = {"name": name, "status": status, "class": class_name}
        
            
        return devices
    
    def block_device(self, device_id):
        """Block a specific USB device based on its ID"""
        if self.system == "Windows":

            cmd = f'pnputil /disable-device "{device_id}"'
            try:
                subprocess.run(cmd, shell=True, check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to block device {device_id}")
                return False
       
        return False
    
    def allow_device(self, device_id):
        """Allow a specific USB device based on its ID"""
        if self.system == "Windows":

            cmd = f'pnputil /enable-device "{device_id}"'
            try:
                subprocess.run(cmd, shell=True, check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to allow device {device_id}")
                return False
        return False

def monitor_usb_devices():
    """Background thread to monitor USB devices"""
    global usb_devices, monitoring
    
    usb_monitor = USBMonitor()
    previous_devices = usb_monitor.get_current_devices()
    
    with device_lock:
        usb_devices = previous_devices
    
    while monitoring:
        try:
            current_devices = usb_monitor.get_current_devices()
            
            with device_lock:
                for device_id, device_info in current_devices.items():
                    if device_id not in usb_devices:

                        device_info["status"] = "pending"
                        device_info["detected_time"] = time.time()
                        usb_devices[device_id] = device_info
                        
                        usb_monitor.block_device(device_id)
                        
                        threading.Thread(target=lambda: show_notification(device_id, device_info["name"])).start()
                
                current_time = time.time()
                for device_id, device_info in list(usb_devices.items()):
                    if device_info.get("status") == "pending":
                        if current_time - device_info.get("detected_time", current_time) > 10:

                            print(f"Auto-denying device after timeout: {device_info['name']}")
                            device_info["status"] = "denied"

                            usb_monitor.block_device(device_id)
            
            time.sleep(1) 
        except Exception as e:
            print(f"Error in monitoring thread: {e}")
            time.sleep(5)

def show_notification(device_id, device_name):
    """Show notification window for a newly detected USB device"""
    root = tk.Tk()
    root.title("USB Monitor")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    
    bg_color = "#1E1E2E" 
    accent_color = "#89B4FA"
    text_color = "#CDD6F4" 
    warning_color = "#F38BA8"  
    success_color = "#A6E3A1"
    warning_hover = "#fc1442"
    success_hover = "#72f567"
    
    root.configure(bg=bg_color)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    window_width = 340
    window_height = 255
    
    x = screen_width - window_width - 20
    y = screen_height - window_height - 60
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    container = tk.Frame(root, bg=bg_color)
    container.pack(fill=tk.BOTH, expand=True)
    
    title_bar = tk.Frame(container, bg=bg_color, height=30)
    title_bar.pack(fill=tk.X, pady=(10, 0))
    
    title_label = tk.Label(title_bar, text="USB Device Detected", fg=accent_color, bg=bg_color, font=("Segoe UI", 12, "bold"))
    title_label.pack(side=tk.LEFT, padx=75)
    
    def close_window():
        deny_action()
    
    close_button = tk.Button(title_bar, text="×", bg=bg_color, fg=text_color, 
                           font=("Arial", 16), bd=0, command=close_window)
    close_button.pack(side=tk.RIGHT, padx=15)
    close_button.config(activebackground=bg_color, activeforeground=warning_color)
    
    def on_close_enter(e):
        close_button.config(fg=warning_color)
    
    def on_close_leave(e):
        close_button.config(fg=text_color)
    
    close_button.bind("<Enter>", on_close_enter)
    close_button.bind("<Leave>", on_close_leave)
    
    content_frame = tk.Frame(container, bg=bg_color)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    icon_frame = tk.Canvas(content_frame, width=60, height=60, bg=bg_color, highlightthickness=0)
    icon_frame.pack(pady=(5, 0))
    
    icon_frame.create_rectangle(25, 10, 35, 25, fill=accent_color, outline="")
    icon_frame.create_rectangle(20, 25, 40, 45, fill=accent_color, outline="")
    icon_frame.create_rectangle(15, 45, 45, 55, fill=accent_color, outline="")
    
    message_label = tk.Label(content_frame, 
                           text=f"A new USB device is requesting access:\n{device_name}\n\nDo you want to allow this connection?\n(Auto-deny in 10 seconds)",
                           fg=text_color, bg=bg_color, font=("Segoe UI", 10),
                           justify=tk.CENTER)
    message_label.pack(fill=tk.X, pady=10)
    
    timer_label = tk.Label(content_frame, text="10", fg=warning_color, bg=bg_color, font=("Segoe UI", 10, "bold"))
    timer_label.pack(fill=tk.X)
    
    countdown_remaining = 10
    
    def update_countdown():
        nonlocal countdown_remaining
        if countdown_remaining > 0 and root.winfo_exists():
            countdown_remaining -= 1
            timer_label.config(text=str(countdown_remaining))
            root.after(1000, update_countdown)
        elif root.winfo_exists():
            deny_action()
    
    root.after(1000, update_countdown)
    
    button_frame = tk.Frame(content_frame, bg=bg_color)
    button_frame.pack(fill=tk.X, pady=10)
    
    def create_button(parent, text, command, color, hover_color):
        btn_frame = tk.Frame(parent, bg=bg_color)
        
        btn = tk.Button(btn_frame, text=text, command=command, 
                      font=("Segoe UI", 11, "bold"),
                      bg=color, fg=bg_color, 
                      activebackground=color, activeforeground=bg_color,
                      bd=0, padx=25, pady=10,
                      cursor="hand2")
        btn.pack(fill=tk.BOTH, expand=True)
        
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn_frame
    
    def deny_action():
        with device_lock:
            if device_id in usb_devices:
                usb_devices[device_id]["status"] = "denied"
        print(f"USB access denied for: {device_name}")
        
        usb_monitor = USBMonitor()
        usb_monitor.block_device(device_id)
        
        if root.winfo_exists():
            root.destroy()
    
    def allow_action():
        with device_lock:
            if device_id in usb_devices:
                usb_devices[device_id]["status"] = "allowed"
        print(f"USB access allowed for: {device_name}")
        
        usb_monitor = USBMonitor()
        usb_monitor.allow_device(device_id)
        
        if root.winfo_exists():
            root.destroy()
    
    btn_container = tk.Frame(button_frame, bg=bg_color)
    btn_container.pack(expand=True)
    
    deny_button = create_button(btn_container, "Deny", deny_action, warning_color, warning_hover)
    deny_button.pack(side=tk.LEFT, padx=10)
    
    allow_button = create_button(btn_container, "Allow", allow_action, success_color, success_hover)
    allow_button.pack(side=tk.LEFT, padx=10)
    
    bottom_space = tk.Frame(container, height=10, bg=bg_color)
    bottom_space.pack(fill=tk.X)

    # Make window draggable/Delete after testing program program is currently not tested.
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def do_move(event):
        dx = event.x - root.x
        dy = event.y - root.y
        x = root.winfo_x() + dx
        y = root.winfo_y() + dy
        root.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", do_move)
    title_label.bind("<ButtonPress-1>", start_move)
    title_label.bind("<ButtonRelease-1>", stop_move)
    title_label.bind("<B1-Motion>", do_move)

    root.mainloop()

def main():
    """Main function to start the USB monitoring service"""
    global monitoring
    
    print("Starting USB security monitor...")
    print("This application will monitor for new USB devices and block them by default.")
    print("You will have 10 seconds to allow a device before it is permanently blocked.")
    
    monitor_thread = threading.Thread(target=monitor_usb_devices, daemon=True)
    monitor_thread.start()
    
    try:

        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down USB monitor...")
        monitoring = False
        monitor_thread.join(timeout=2)
        print("USB monitor stopped.")

if __name__ == "__main__":
    main()