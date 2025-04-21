import tkinter as tk
import time   

def window():
    root = tk.Tk()
    root.title("USB Monitor")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
       
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    window_width = 300
    window_height = 200
    
    x = screen_width - window_width - 20
    y = screen_height - window_height - 60
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.configure(bg="black")

    tk.Button(root, text="Deny", command=root.quit, bg="black", fg="white", font=("Arial", 12)).pack(pady=50, padx=70)
    tk.Button(root, text="Allow", command=root.quit, bg="black", fg="white", font=("Arial", 12)).pack(pady=10, padx=10)
    
    root.mainloop()

def allow():
    return

def deny():
    return

if __name__ == "__main__":
    window()