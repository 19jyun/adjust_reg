import pythoncom
import psutil
import wmi
from PIL import Image, ImageDraw, ImageFont
import pystray
from threading import Thread, Event
import time
import tray_icons.tray_manager as tray_manager

# Global stop_event definition
stop_event = Event()

def format_rate(rate):
    """Format rate: 'x.x' if rate < 10, integer if rate >= 10."""
    if rate is None:
        return "N/A"
    if rate < 10:
        return f"{rate:.1f}"
    else:
        return f"{int(rate)}"

def create_image(width, height, rate, background_color):
    """Creates an image with the rate displayed on it."""
    rate_str = format_rate(rate)

    font_size = 35 if len(rate_str) >= 3 else 45

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    image = Image.new("RGB", (width, height), background_color)
    dc = ImageDraw.Draw(image)

    text_bbox = dc.textbbox((0, 0), rate_str, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    dc.text(
        ((width - text_width) / 2, (height - text_height) / 2 - 5),
        rate_str, font=font, fill="black"
    )
    
    return image

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    return {
        "percent": battery.percent,
        "power_plugged": battery.power_plugged,
        "secsleft": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
        "time_remaining": time.strftime("%H:%M:%S", time.gmtime(battery.secsleft)) if battery.secsleft > 0 else "N/A",
    }

def get_power_usage():
    try:
        c = wmi.WMI(namespace="root\\wmi")
        battery = c.BatteryStatus()[0]
        power_online = battery.PowerOnline
        discharge_rate = battery.DischargeRate if battery.DischargeRate is not None else 0
        charge_rate = battery.ChargeRate if battery.ChargeRate is not None else 0
        return power_online, discharge_rate, charge_rate
    except Exception as e:
        print(f"Error retrieving power usage: {e}")
        return None, None, None

def update_tray_icon(tray_icon):
    
    pythoncom.CoInitialize()  # Initialize COM library

    """Update the system tray icon with current battery info."""
    while not stop_event.is_set():
        battery_info = get_battery_info()
        if battery_info is None:
            tray_icon.title = 'No battery detected'
            tray_icon.icon = create_image(64, 64, 0, "black")
            break

        power_online, discharge_rate, charge_rate = get_power_usage()

        if battery_info["power_plugged"]:
            power_usage_w = charge_rate / 1000 if charge_rate and charge_rate > 0 else 0
            background_color = "green"
        else:
            power_usage_w = discharge_rate / 1000 if discharge_rate and discharge_rate > 0 else 0
            background_color = "yellow"

        tooltip_text = (
            f"Battery: {battery_info['percent']}% | "
            f"{'Plugged In' if battery_info['power_plugged'] else 'On Battery'}\n"
            f"{'Charging Rate' if battery_info['power_plugged'] else 'Discharge Rate'}: {power_usage_w:.2f} W"
        )
        
        print(tooltip_text)

        tray_icon.title = tooltip_text
        tray_icon.icon = create_image(64, 64, power_usage_w, background_color)

        time.sleep(2)

def stop_monitoring(icon):
    """Stop the monitoring by setting the stop_event and stopping the icon."""
    stop_event.set()
    icon.stop()

def start_tray_icon():
    """Initialize and run the tray icon."""
    icon = pystray.Icon("Battery Monitor")
    icon.icon = create_image(64, 64, 0, "black")  # Default icon
    icon.title = "Initializing battery monitor..."
    icon.menu = pystray.Menu(
        pystray.MenuItem("Stop", lambda: stop_monitoring(icon))
    )
    icon.run_detached()
    
    Thread(target=update_tray_icon, args=(icon,)).start()

    return icon
