import pywinusb.hid as hid

def touchpad_handler(data):
    # 터치패드 데이터 처리 로직 추가
    print(f"Touchpad data: {data}")

def list_hid_devices():
    # Find all HID devices
    all_devices = hid.HidDeviceFilter().get_devices()

    # Print the vendor ID and product ID of each device
    for device in all_devices:
        print(f"Device found: Vendor ID = {device.vendor_id}, Product ID = {device.product_id}, Vendor Name = {device.vendor_name}, Product Name = {device.product_name}")

def main():
    # Find all HID devices
    all_devices = hid.HidDeviceFilter().get_devices()

    list_hid_devices()

    # Look for the touchpad device by its usage or vendor ID, if known
    for device in all_devices:
        print(f"Device found: {device.vendor_id}, {device.product_id}")
        
        # You can modify the vendor_id and product_id based on your touchpad device
        if device.vendor_id == 10182 and device.product_id == 291:  
            print(f"Found touchpad: {device.vendor_name} {device.product_name}")
            
            device.open()

            # Set custom handler for raw input reports
            device.set_raw_data_handler(touchpad_handler)

            try:
                print("Listening for touchpad reports. Press Ctrl+C to stop.")
                while True:
                    pass  # Keep the script running
            except KeyboardInterrupt:
                print("Exiting...")
            finally:
                device.close()

if __name__ == "__main__":
    main()