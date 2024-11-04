# tray_manager.py
import os
import psutil
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image
from battery.display_discharge import stop_monitoring, start_tray_icon
import json
import win32gui
import win32con

tray_icon = None  # Global variable to keep track of the main tray icon
battery_icon = None  # Global variable to keep track of the battery discharge icon
SETTINGS_FILE = "settings/settings.json"  # File to store settings

# Create the tray icon image
def create_image():
    """Create the tray icon image."""
    try:
        image = Image.open('tray_icons/registry.png')  # Specify the path to your icon file
        return image
    except Exception as e:
        print(f"Error loading tray icon image: {e}")
        return None

# Start the main tray icon
def start_main_tray_icon():
    """Start the main tray icon for the application."""
    global tray_icon, battery_icon
    image = create_image()
    if image:
        menu = TrayMenu(
            TrayMenuItem('Restore', restore_application),
            TrayMenuItem('Quit', quit_application)
        )
        tray_icon = TrayIcon("MyWindows", image, menu=menu)
        tray_icon.run_detached()  # Detach so that it runs in the background
    else:
        print("Could not create tray icon due to missing image.")
        
    # Load the settings properly
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        print(f"Settings file '{SETTINGS_FILE}' not found. Skipping battery discharge icon.")
        settings = {}
        
    if settings.get('Display discharge rate', False):
        start_battery_discharge_icon()
        
    return tray_icon

# Stop the main tray icon
def stop_main_tray_icon():
    """Stop the main tray icon."""
    global tray_icon
    if tray_icon:
        tray_icon.stop()
        tray_icon = None

def find_window_by_title(title):
    """Find a window by its title."""
    return win32gui.FindWindow(None, title)

def restore_window(window_title):
    """Restore a minimized window using its title."""
    hwnd = find_window_by_title(window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore if minimized
        win32gui.SetForegroundWindow(hwnd)  # Bring to the foreground

def restore_application(icon, item):
    """Restore the minimized main application window."""
    window_title = "Trackpad Registry Manager"  # The title of your main window
    hwnd = find_window_by_title(window_title)
    
    if hwnd:
        restore_window(window_title)
    else:
        # If the window is not found, you may want to log or handle this case.
        print(f"Window '{window_title}' not found.")

# Quit the entire application, both icon trays must be quit
def quit_application(icon, item):
    global tray_icon, battery_icon
    """Quit the main tray icon and also stop the battery discharge icon if running."""
    if is_battery_discharge_running():
        stop_battery_discharge_icon()  # Stop the battery discharge icon if running
        battery_icon = None
    stop_main_tray_icon()  # Quit the main tray icon
    tray_icon = None
    os._exit(0)

# Stop the battery discharge tray icon if running
def stop_battery_discharge_icon():
    """Stop the battery discharge tray icon if it is running."""
    global battery_icon
    if battery_icon:
        stop_monitoring(battery_icon)
        battery_icon = None

def start_battery_discharge_icon():
    """Start the battery discharge tray icon."""
    global battery_icon
    if not battery_icon:
        battery_icon = start_tray_icon()

# Helper function to check if a specific tray icon process is running (battery discharge)
def is_battery_discharge_running():
    global battery_icon
    if not battery_icon:
        return False
    else:
        return True

