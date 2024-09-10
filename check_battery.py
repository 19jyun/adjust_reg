import psutil
import time
import os

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

def log_battery_drainage(log_file):
    previous_percent = None
    previous_time = None

    with open(log_file, 'w') as f:
        f.write("Timestamp,Percentage,Power Status,Estimated Time Left,Drainage Rate (percent/hour)\n")
        
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

        # Calculate drainage rate in percentage per hour
        drainage_rate = None
        if previous_percent is not None and previous_time is not None and not battery_info["power_plugged"]:
            time_diff = (current_time - previous_time) / 3600  # Time difference in hours
            percent_diff = previous_percent - current_percent
            drainage_rate = round(percent_diff / time_diff, 2) if time_diff > 0 else None

        # Log the data to the file
        with open(log_file, 'a') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{current_percent},{power_status},{estimated_time_left},{drainage_rate}\n")
        
        # Print the data to the console
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Battery: {current_percent}% | Status: {power_status} | Time Left: {estimated_time_left}")
        if drainage_rate is not None:
            print(f"Drainage Rate: {drainage_rate}%/hour")
        print("-" * 40)
        
        # Update the previous values
        previous_percent = current_percent
        previous_time = current_time

        # Wait for a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    log_file = "battery_drainage_log.csv"
    log_battery_drainage(log_file)
