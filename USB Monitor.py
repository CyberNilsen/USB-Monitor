import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

def window():
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
        root.destroy()
    
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
                           text="A new USB device is requesting access.\nDo you want to allow this connection?",
                           fg=text_color, bg=bg_color, font=("Segoe UI", 10),
                           justify=tk.CENTER)
    message_label.pack(fill=tk.X, pady=10)
    
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
        deny()
        root.destroy()
    
    def allow_action():
        allow()
        root.destroy()
    
    btn_container = tk.Frame(button_frame, bg=bg_color)
    btn_container.pack(expand=True)
    
    deny_button = create_button(btn_container, "Deny", deny_action, warning_color, warning_hover)
    deny_button.pack(side=tk.LEFT, padx=10)
    
    allow_button = create_button(btn_container, "Allow", allow_action, success_color, success_hover)
    allow_button.pack(side=tk.LEFT, padx=10)
    
    bottom_space = tk.Frame(container, height=10, bg=bg_color)
    bottom_space.pack(fill=tk.X)

    root.mainloop()

def allow():
    print("USB access allowed")
    return

def deny():
    print("USB access denied")
    return

if __name__ == "__main__":
    window()