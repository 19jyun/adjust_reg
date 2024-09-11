import wmi
import psutil
import time

def get_battery_info():
    # Get basic battery info using psutil
    battery = psutil.sensors_battery()
    if battery is None:
        print("No battery detected.")
        return

    capacity = battery.percent
    is_charging = battery.power_plugged
    charging_status = "Charging" if is_charging else "Discharging"
    
    # Get more detailed info using WMI
    w = wmi.WMI(namespace='root\\wmi')
    try:
        battery_status = w.BatteryStatus()[0]
        discharge_rate = battery_status.DischargeRate / 1000  # In Watts (milliwatts to watts)
    except Exception as e:
        print(f"Error retrieving battery status: {e}")
        discharge_rate = None
    
    # Display the information
    print(f"Capacity: {capacity}%")
    print(f"Status: {charging_status}")
    if not is_charging and discharge_rate is not None:
        print(f"Discharge Rate: {discharge_rate:.2f} Watts")
    else:
        print("Charging...")

if __name__ == "__main__":
    while True:
        get_battery_info()
        time.sleep(2)