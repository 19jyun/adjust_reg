import psutil
import time
import wmi

def get_battery_info():
    # Get battery info using psutil
    battery = psutil.sensors_battery()
    
    # Check if the battery info is available
    if battery is None:
        print("Battery information not available.")
        return
    
    # Get the capacity and charging status
    capacity = battery.percent
    is_charging = battery.power_plugged
    charging_status = "Charging" if is_charging else "Discharging"
    
    # Get more detailed info using WMI
    w = wmi.WMI(namespace='root\\wmi')
    battery_info = w.MSAcpi_ThermalZoneTemperature()[0]
    
    # Using WMI to calculate battery power consumption in Watts
    battery_status = w.BatteryStatus()[0]
    discharge_rate = battery_status.DischargeRate / 1000  # In Watts (milliwatts to watts)
    
    # Display the information
    print(f"Capacity: {capacity}%")
    print(f"Status: {charging_status}")
    if not is_charging:
        print(f"Discharge Rate: {discharge_rate:.2f} Watts")
    else:
        print("Charging...")

if __name__ == "__main__":
    while True:
        get_battery_info()
        time.sleep(2)
