import os
import json
import platform
import ctypes
import psutil
import wmi

def is_first_execution():
    """Check if this is the first time the script is being executed."""
    settings_file = "settings/system_data.json"
    return not os.path.exists(settings_file)

def save_system_data(data):
    """Save the collected system data to a JSON file."""
    os.makedirs("settings", exist_ok=True)
    settings_file = "settings/system_data.json"
    with open(settings_file, "w") as f:
        json.dump(data, f)
    print(f"System data saved to {settings_file}")

def check_if_laptop():
    """Check if the device is a laptop or desktop."""
    system = platform.system().lower()
    
    if system == "windows":
        try:
            # Use WMI to detect the system's chassis type
            c = wmi.WMI()
            for enclosure in c.Win32_SystemEnclosure():
                if hasattr(enclosure, 'ChassisTypes'):
                    # Look for ChassisTypes 8, 9, 10, 14 which represent various portable devices
                    if any(chassis_type in [8, 9, 10, 14] for chassis_type in enclosure.ChassisTypes):
                        return True  # It's a laptop
            return False  # Default to desktop if no portable types found
        except Exception as e:
            print(f"Error detecting chassis type: {e}")
            return False
    return False

def check_if_tkl_keyboard():
    """Check if the keyboard is TKL (no numpad)."""
    # Check for number pad by checking if certain keys are available on the keyboard
    has_numpad = ctypes.windll.user32.GetKeyState(0x90)  # NumLock key check
    return not bool(has_numpad)  # If NumLock is not present, assume TKL

def check_if_has_battery():
    """Check if the device has a battery."""
    battery = psutil.sensors_battery()
    return battery is not None

def collect_system_data():
    """Collect system data about the device."""
    system_data = {
        "is_laptop": check_if_laptop(),
        "is_tkl_keyboard": check_if_tkl_keyboard(),
        "has_battery": check_if_has_battery(),
    }
    return system_data

if __name__ == "__main__":
    if is_first_execution():
        # Collect system data only on first execution
        system_data = collect_system_data()
        save_system_data(system_data)
        print("System data collected and saved:")
        print(system_data)
    else:
        print("System data has already been collected.")
