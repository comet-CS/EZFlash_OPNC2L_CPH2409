import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
import shutil
import time
import threading

adb_folder = os.path.join(os.getcwd(), "ADB")

def run_adb_command(command, capture_output=True):
    adb_path = os.path.join(adb_folder, "adb.exe")
    try:
        command_list = [adb_path] + command.split()
        result = subprocess.run(command_list, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode() if capture_output else ''
        error = result.stderr.decode()
        return output, error
    except subprocess.CalledProcessError as e:
        return e.stdout.decode(), e.stderr.decode()

def check_device_connected():
    output, error = run_adb_command("devices", capture_output=True)
    if "device" in output:
        return True
    return False

def reboot_into_bootloader():
    output, error = run_adb_command("reboot bootloader")
    if error:
        messagebox.showerror("Error", f"Failed to reboot into bootloader: {error}")
    else:
        messagebox.showinfo("Info", "Device rebooting into bootloader...")

def flash_firmware():
    if not check_device_connected():
        messagebox.showerror("Error", "No devices connected. Please connect a device.")
        return

    file_path = filedialog.askopenfilename(title="Select Firmware Image", filetypes=[("Image Files", "*.img")])
    if file_path:
        messagebox.showinfo("Flashing", f"Flashing firmware from {file_path}...")
        
        reboot_into_bootloader()

        start_time = time.time()
        output, error = run_adb_command(f"fastboot flash system {file_path}")
        end_time = time.time()

        execution_time = round((end_time - start_time) * 1000, 2)
        if error:
            messagebox.showerror("Error", f"Failed to flash firmware: {error}")
        else:
            messagebox.showinfo("Success", f"Firmware flashed successfully! ({execution_time} ms)")

def create_splash():
    if not check_device_connected():
        messagebox.showerror("Error", "No devices connected. Please connect a device.")
        return

    image_path = filedialog.askopenfilename(title="Select Image for Splash Screen", filetypes=[("Image Files", "*.png;*.jpg")])
    if image_path:
        output_path = "custom_splash.img"
        messagebox.showinfo("Splash Screen", f"Creating splash screen from {image_path}...")
        
        try:
            shutil.copy(image_path, output_path)

            reboot_into_bootloader()

            start_time = time.time()
            output, error = run_adb_command(f"fastboot flash splash {output_path}")
            end_time = time.time()

            execution_time = round((end_time - start_time) * 1000, 2)
            if error:
                messagebox.showerror("Error", f"Failed to flash splash screen: {error}")
            else:
                messagebox.showinfo("Success", f"Splash screen flashed successfully! ({execution_time} ms)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create splash screen: {str(e)}")

def run_custom_adb_command():
    if not check_device_connected():
        messagebox.showerror("Error", "No devices connected. Please connect a device.")
        return

    command = simpledialog.askstring("ADB Command", "(Do not include ADB in the Command!)")
    if command:
        def execute_command():
            start_time = time.time()
            output, error = run_adb_command(command, capture_output=True)
            end_time = time.time()

            execution_time = round((end_time - start_time) * 1000, 2)
            if error:
                messagebox.showerror("Error", f"ADB command failed: {error}")
            else:
                messagebox.showinfo("Success", f"Command executed successfully! ({execution_time} ms)\nOutput: {output}")

        threading.Thread(target=execute_command, daemon=True).start()

def create_gui():
    root = tk.Tk()
    root.title("CPH2409 EZFlash Tool")
    root.geometry("600x450")
    root.configure(bg="#2e2e2e")

    try:
        root.iconbitmap(os.path.join(os.getcwd(), "your_icon.ico"))
    except Exception as e:
        print(f"Error setting icon: {e}")

    title_label = tk.Label(root, text="OnePlus Tool", fg="#fff", bg="#2e2e2e", font=("Arial", 20, "bold"))
    title_label.pack(pady=30)

    instructions_label = tk.Label(root, text="Select an action below to start", fg="#bbb", bg="#2e2e2e", font=("Arial", 12))
    instructions_label.pack(pady=10)

    flash_button = tk.Button(root, text="Flash Firmware", command=flash_firmware, bg="#333", fg="#fff", font=("Helvetica", 12), relief="flat", width=20)
    flash_button.pack(pady=15, fill="x", padx=40)

    splash_button = tk.Button(root, text="Create & Flash Splash Screen", command=create_splash, bg="#333", fg="#fff", font=("Helvetica", 12), relief="flat", width=20)
    splash_button.pack(pady=15, fill="x", padx=40)

    adb_button = tk.Button(root, text="Run Custom ADB Command", command=run_custom_adb_command, bg="#333", fg="#fff", font=("Helvetica", 12), relief="flat", width=20)
    adb_button.pack(pady=15, fill="x", padx=40)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
