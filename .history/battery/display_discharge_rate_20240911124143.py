import wmi
import psutil
import time

def get_battery_capacity():
    # Initialize WMI
    c = wmi.WMI()

    # Query for battery information
    battery_list = c.Win32_Battery()
    
    if not battery_list:
        print("Error: No battery information found.")
        return None

    battery_info = battery_list[0]  # Retrieves the first battery

    # Debugging output to check battery information
    print(f"Battery Info: {battery_info}")

    design_capacity = battery_info.DesignCapacity  # Capacity in mWh
    full_charge_capacity = battery_info.FullChargeCapacity  # Full charge capacity in mWh

    # Ensure capacities are valid (not None)
    if design_capacity is None or full_charge_capacity is None:
        print("Error: Battery capacity information is missing.")
        return None

    return {
        "design_capacity_mWh": design_capacity,
        "full_charge_capacity_mWh": full_charge_capacity,
    }

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

def log_battery_drainage():
    battery_capacity_info = get_battery_capacity()
    
    if battery_capacity_info is None:
        print("Error: Could not retrieve battery capacity.")
        return

    # Convert capacity from mWh to Wh
    full_capacity_Wh = battery_capacity_info["full_charge_capacity_mWh"] / 1000

    previous_percent = None
    previous_time = None

    while True:
        battery_info = get_battery_info()
        if battery_info is None:
            print("No battery detected.")
            break

        # Capture current time and battery percentage
        current_time = time.time()
        current_percent = battery_info["percent"]
        power_status = "Plugged In" if battery_info["power_plugged"] else "On Battery"
        estimated_time_left = battery_info["time_remaining"]

        # Calculate drainage rate in percentage per hour and in watts
        drainage_rate = None
        power_drain_watts = None
        if previous_percent is not None and previous_time is not None and not battery_info["power_plugged"]:
            time_diff = (current_time - previous_time) / 3600  # Time difference in hours
            percent_diff = previous_percent - current_percent
            drainage_rate = round(percent_diff / time_diff, 2) if time_diff > 0 else None

            # Estimate power drain in watts: (capacity in Wh * percentage drained per hour) / 100
            power_drain_watts = round((full_capacity_Wh * drainage_rate) / 100, 2)

        # Print the data to the console
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Battery: {current_percent}% | Status: {power_status} | Time Left: {estimated_time_left}")
        if drainage_rate is not None:
            print(f"Drainage Rate: {drainage_rate}%/hour | Power Drain: {power_drain_watts} W")
        print("-" * 40)
        
        # Update the previous values
        previous_percent = current_percent
        previous_time = current_time

        # Wait for 2 seconds before checking again (you can adjust this)
        time.sleep(2)

if __name__ == "__main__":
    log_battery_drainage()