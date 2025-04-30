import tkinter as tk
from tkinter import ttk
import threading
import time
import platform
import subprocess
import re
import os
import sys
import ctypes
from PIL import Image, ImageTk, ImageDraw

usb_devices = {}
device_lock = threading.Lock()
monitoring = True
notification_windows = {}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

class USBMonitor:
    def __init__(self):
        self.system = platform.system()
        
    def get_current_devices(self):
        devices = {}
        
        if self.system == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            cmd = "powershell -Command \"Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'USB' -or $_.Class -eq 'DiskDrive' -or $_.Class -eq 'USBDevice' -or $_.Class -eq 'HIDClass' } | Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Csv -NoTypeInformation\""
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    startupinfo=startupinfo, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        for line in lines[1:]:
                            if line.strip():
                                parts = line.strip('"').split('","')
                                if len(parts) >= 4:
                                    status, class_name, name, instance_id = parts
                                    devices[instance_id] = {"name": name, "status": status, "class": class_name}
                else:
                    print(f"Command failed with return code {result.returncode}: {result.stderr}")
            except Exception as e:
                print(f"Error getting devices: {e}")
        
        return devices
    
    def block_device(self, device_id):
        if self.system == "Windows":
            for _ in range(3):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                cmd = f'powershell -Command "Disable-PnpDevice -InstanceId \'{device_id}\' -Confirm:$false -ErrorAction Stop"'
                try:
                    result = subprocess.run(
                        cmd, 
                        shell=True,
                        capture_output=True,
                        text=True,
                        startupinfo=startupinfo, 
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode == 0:
                        print(f"Successfully blocked device {device_id}")
                        return True
                    else:
                        print(f"Block attempt failed: {result.stderr}")
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Exception blocking device {device_id}: {e}")
                    time.sleep(0.5)
            
            try:
                cmd = f'pnputil /disable-device "{device_id}"'
                result = subprocess.run(
                    cmd, 
                    shell=True,
                    capture_output=True,
                    text=True,
                    startupinfo=startupinfo, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    print(f"Successfully blocked device using pnputil: {device_id}")
                    return True
                else:
                    print(f"Pnputil block failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"Pnputil exception: {e}")
                return False
       
        return False
    
    def allow_device(self, device_id):
        if self.system == "Windows":
            for _ in range(3):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                cmd = f'powershell -Command "Enable-PnpDevice -InstanceId \'{device_id}\' -Confirm:$false -ErrorAction Stop"'
                try:
                    result = subprocess.run(
                        cmd, 
                        shell=True,
                        capture_output=True,
                        text=True,
                        startupinfo=startupinfo, 
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode == 0:
                        print(f"Successfully allowed device {device_id}")
                        return True
                    else:
                        print(f"Allow attempt failed: {result.stderr}")
                        time.sleep(0.5) 
                except Exception as e:
                    print(f"Exception allowing device {device_id}: {e}")
                    time.sleep(0.5) 
            
            try:
                cmd = f'pnputil /enable-device "{device_id}"'
                result = subprocess.run(
                    cmd, 
                    shell=True,
                    capture_output=True,
                    text=True,
                    startupinfo=startupinfo, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    print(f"Successfully allowed device using pnputil: {device_id}")
                    return True
                else:
                    print(f"Pnputil allow failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"Pnputil exception: {e}")
                return False
        return False

def delayed_usb_check():
    global usb_devices
    time.sleep(0.5)
    
    usb_monitor = USBMonitor()
    new_devices = usb_monitor.get_current_devices()
    
    with device_lock:
        for device_id, device_info in new_devices.items():
            if device_id not in usb_devices:
                print(f"Delayed detection found device: {device_info['name']} ({device_id})")
                device_info["status"] = "pending"
                device_info["detected_time"] = time.time()
                usb_devices[device_id] = device_info
                
                block_success = usb_monitor.block_device(device_id)
                if block_success:
                    print(f"Delayed blocking successful for: {device_info['name']}")
                else:
                    print(f"Delayed blocking failed for: {device_info['name']}, will retry")

                    threading.Thread(target=retry_block, args=(device_id,), daemon=True).start()
                
                threading.Thread(
                    target=show_notification,
                    args=(device_id, device_info["name"]),
                    daemon=True
                ).start()

def retry_block(device_id):
    time.sleep(1)
    with device_lock:
        if device_id in usb_devices and usb_devices[device_id]["status"] == "pending":
            print(f"Retrying block for device: {device_id}")
            usb_monitor = USBMonitor()
            block_success = usb_monitor.block_device(device_id)
            print(f"Retry block result: {block_success}")

def monitor_usb_devices():
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
                        print(f"New device detected: {device_info['name']} ({device_id})")
                        
                        print(f"Immediately blocking device: {device_info['name']}")
                        block_success = usb_monitor.block_device(device_id)
                        
                        if block_success:
                            print(f"Initial blocking successful for: {device_info['name']}")
                        else:
                            print(f"Initial blocking FAILED for: {device_info['name']}, scheduling retry")

                            threading.Thread(target=retry_block, args=(device_id,), daemon=True).start()
                        
                        device_info["status"] = "pending"
                        device_info["detected_time"] = time.time()
                        usb_devices[device_id] = device_info
                        
                        threading.Thread(
                            target=show_notification,
                            args=(device_id, device_info["name"]),
                            daemon=True
                        ).start()
                
                threading.Thread(target=delayed_usb_check, daemon=True).start()
                
                current_time = time.time()
                for device_id, device_info in list(usb_devices.items()):
                    if device_info.get("status") == "pending":
                        time_elapsed = current_time - device_info.get("detected_time", current_time)
                        if time_elapsed > 10:
                            print(f"Auto-denying device after timeout: {device_info['name']}")
                            device_info["status"] = "denied"
                            
                            block_result = usb_monitor.block_device(device_id)
                            print(f"Auto-deny block result: {block_result} for {device_info['name']}")
                            
                            if device_id in notification_windows:
                                try:
                                    root = notification_windows[device_id]
                                    if root.winfo_exists():
                                        root.destroy()
                                    del notification_windows[device_id]
                                except:
                                    pass
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Error in monitoring thread: {e}")
            time.sleep(2)

def show_notification(device_id, device_name):
    global notification_windows
    
    try:

        if device_id in notification_windows:
            try:
                old_root = notification_windows[device_id]
                if old_root.winfo_exists():
                    old_root.destroy()
            except:
                pass
        
        root = tk.Tk()
        notification_windows[device_id] = root
        
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
        window_height = 305
        
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
        
        message_text = f"A new USB device is requesting access:\n{device_name}\n\nThe device is currently blocked.\nDo you want to allow this connection?\n(Auto-deny in 10 seconds)"
        message_label = tk.Label(content_frame, 
                               text=message_text,
                               fg=text_color, bg=bg_color, font=("Segoe UI", 10),
                               justify=tk.CENTER)
        message_label.pack(fill=tk.X, pady=10)
        
        timer_label = tk.Label(content_frame, text="10", fg=warning_color, bg=bg_color, font=("Segoe UI", 10, "bold"))
        timer_label.pack(fill=tk.X)
        
        countdown_remaining = 10
        timer_active = True
        
        def update_countdown():
            nonlocal countdown_remaining
            if countdown_remaining > 0 and root.winfo_exists() and timer_active:
                countdown_remaining -= 1
                timer_label.config(text=str(countdown_remaining))
                root.after(1000, update_countdown)
            elif root.winfo_exists() and timer_active:
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
            nonlocal timer_active
            timer_active = False
            
            with device_lock:
                if device_id in usb_devices:
                    usb_devices[device_id]["status"] = "denied"
            print(f"USB access denied for: {device_name}")
            
            usb_monitor = USBMonitor()
            block_result = usb_monitor.block_device(device_id)
            print(f"Deny block result: {block_result}")
            
            if device_id in notification_windows:
                del notification_windows[device_id]
            
            if root.winfo_exists():
                root.destroy()
        
        def allow_action():
            nonlocal timer_active
            timer_active = False
            
            with device_lock:
                if device_id in usb_devices:
                    usb_devices[device_id]["status"] = "allowed"
            print(f"USB access allowed for: {device_name}")
            
            usb_monitor = USBMonitor()
            allow_result = usb_monitor.allow_device(device_id)
            print(f"Allow result: {allow_result}")
            
            if device_id in notification_windows:
                del notification_windows[device_id]
            
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

        root.after(100, lambda: allow_button.focus_set())
        
        root.after(100, lambda: root.lift())
        root.after(500, lambda: root.attributes("-topmost", True))
            
        root.mainloop()
    except Exception as e:
        print(f"Error showing notification: {e}")

def main():
    global monitoring
    
    if not is_admin():
        print("This program requires administrator privileges to block USB devices.")
        print("Attempting to restart with admin rights...")
        run_as_admin()
        sys.exit(0)
    
    print("Starting USB security monitor...")
    print("This application will monitor for new USB devices and block them immediately.")
    print("You will have 10 seconds to allow a device or it will remain blocked.")
    
    monitor_thread = threading.Thread(target=monitor_usb_devices, daemon=True)
    monitor_thread.start()
    
    try:

        hidden_root = tk.Tk()
        hidden_root.withdraw() 
        
        while True:
            hidden_root.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down USB monitor...")
        monitoring = False
        monitor_thread.join(timeout=2)
        print("USB monitor stopped.")
    except Exception as e:
        print(f"Error in main loop: {e}")
        monitoring = False

if __name__ == "__main__":
    main()