# Placeholder currently:

# USB Monitor

USB Monitor is a **Windows-based utility** designed to enhance security by allowing you to monitor, manage, and control USB device connections. It prevents unauthorized devices from being accessed by requiring explicit user permission before they can be used. If no action is taken, the device is automatically denied access.

> ⚠️ **This project is for educational purposes and authorized use only.**

![USB Monitor](https://github.com/user-attachments/assets/9f9edcb2-98e2-4eeb-9c49-4249b210135f)

---

## 🚀 Features

- 🔌 **USB Device Detection** — Automatically detects when a USB device is inserted.
- 🛑 **Deny Unauthorized USB Devices** — Block access to USB devices unless explicitly accepted by the user.
- ✔️ **Accept or Deny Access** — Provides a GUI that allows the user to decide whether to grant access to a detected USB device.
- ⏳ **Timeout Functionality** — If the user doesn't respond within a set time (e.g., 10 seconds), the device is automatically denied access.
- 🔒 **Secure User Interaction** — Popup alerts and requires confirmation for any device connected.
- 💻 **Background Monitoring** — Runs silently in the background and interacts with the user only when a new USB device is detected.

---

## 🛠️ Technologies Used

- **Python** — Main framework for building the application with a modern graphical user interface.
- **USB Event Handling** — Detects USB events and monitors device connections.

---

## 📦 Installation

### Clone the repository:
```bash
git clone https://github.com/CyberNilsen/USB-Monitor.git
cd USB-Monitor
```
Build the project:
Open the project in Visual Studio, build the solution, and run the application. You need admin permissions to run this program or else it wont work properly.

---

## ▶️ Usage
Once the application is launched, it will automatically monitor USB ports for new device connections.

When a new USB device is inserted, a popup will appear in the bottom-right corner of the screen asking the user to Accept or Deny the device.

If no response is given within the specified timeout period, the USB device will be denied access automatically.

The program can be configured to run in the background at startup, offering seamless security protection.

To run the program yourself you have to run this command inside vscode terminal

```bash
 pyinstaller --onefile --noconsole --uac-admin --name "USB Monitor" USB_Monitor.py
```
Now you go to the dist folder inside of USB-Monitor then you run USB Monitor.exe as admin. Now it should work and to test it all you have to do is connect a USB device and the program should pop up.

---

## ⚠️ Legal Disclaimer
This software is created strictly for educational purposes and ethical security applications. Do not use this tool on any system without explicit written permission.

Unauthorized use may be illegal and could result in criminal charges.

---

## 🛡️ Defense & Detection
To prevent unauthorized USB access, follow these cybersecurity best practices:

USB Port Control — Disable unused USB ports in BIOS/UEFI or via Group Policy.

Device Whitelisting — Only allow authorized USB devices to be used by adding their IDs to a whitelist.

Antivirus & EDR — Use up-to-date security tools to detect suspicious USB behaviors.

Firewall Rules — Restrict the use of high-risk ports (like USB) to specific users or groups.

---

## 📘 Why This Exists
This project was developed to enhance USB security by ensuring unauthorized devices are blocked automatically. It also demonstrates how to control and monitor USB connections for educational and practical use.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

> Developed with curiosity and passion by Andreas ([CyberNilsen](https://github.com/CyberNilsen))


