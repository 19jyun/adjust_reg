import ctypes
from ctypes import wintypes, windll

ctypes.windll.shcore.SetProcessDpiAwareness(2)

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

# MONITORINFO structure definition
class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD)
    ]

# POINT structure definition
class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG)
    ]

class ScreenInfo:
    def __init__(self):
        self.screen_width = 0
        self.screen_height = 0
        self.window_width = 0
        self.window_height = 0
        
        self.dpi = self.get_scaling_factor()
        self.taskbar_height = self.get_taskbar_height()
        
        self.geometry = self.get_window_size()
        
    @staticmethod
    def get_scaling_factor():
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            hdc = user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
            scaling_factor = dpi / 96.0
            return scaling_factor
        except Exception as e:
            print(f"Error getting DPI scaling: {e}")
            return 1.0
        
    def get_taskbar_height(self):
        user32 = ctypes.windll.user32
        monitor_info = MONITORINFO()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
        point = POINT(0, 0)
        monitor = user32.MonitorFromPoint(point, 1)
        user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info))
        work_area = monitor_info.rcWork
        screen_area = monitor_info.rcMonitor
        taskbar_height = screen_area.bottom - work_area.bottom
        return taskbar_height
       
    def get_physical_monitor_size(self):
        """Retrieve the physical dimensions of the primary monitor in inches."""
        user32 = ctypes.windll.user32
        hdc = user32.GetDC(0)
        
        # Retrieve the width and height in millimeters
        HORZSIZE = 4  # Width in millimeters
        VERTSIZE = 6  # Height in millimeters
        width_mm = ctypes.windll.gdi32.GetDeviceCaps(hdc, HORZSIZE)
        height_mm = ctypes.windll.gdi32.GetDeviceCaps(hdc, VERTSIZE)

        if width_mm > 0 and height_mm > 0:
            # Convert millimeters to inches (1 inch = 25.4 mm)
            width_in = width_mm / 25.4
            height_in = height_mm / 25.4
        else:
            # Use default values if unable to retrieve dimensions
            width_in, height_in = 15.0, 9.0  # Typical laptop size

        return width_in, height_in
        
    def get_window_size(self):
        scaling_factor = self.get_scaling_factor()

        user32 = ctypes.windll.user32
        
        screen_width = int(user32.GetSystemMetrics(0))
        screen_height = int(user32.GetSystemMetrics(1))
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
                # Get physical dimensions of the monitor in inches
        physical_width, physical_height = self.get_physical_monitor_size()
        
        width, height = 0, 0
        # Determine proportions based on physical size
        if physical_width < 15:
            width = 300
            height = 550
        elif 15 <= physical_width <= 18:
            width = 350
            height = 600
        elif 18 < physical_width <= 24:
            width = 400
            height = 650
        elif 24 < physical_width <= 27:
            width = 450
            height = 700
        else:
            width = 500
            height = 750
        
        # Adjust window size based on DPI scaling factor
        window_width = width
        window_height = height
        
        # Calculate taskbar height and subtract it from the vertical position
        taskbar_height = self.get_taskbar_height()

        # Position the window in the bottom-right corner, above the taskbar
        position_right = screen_width - window_width - 5  # 5px margin from right edge
        position_down = screen_height - window_height - taskbar_height - 5  # 5px margin from taskbar
        
        # Adjust window size based on DPI scaling factor
        dpi_window_width = int(window_width/scaling_factor)
        dpi_window_height = int(window_height/scaling_factor)
        
        self.window_width = dpi_window_width
        self.window_height = dpi_window_height
        
        return f"{dpi_window_width}x{dpi_window_height}+{position_right}+{position_down}"
    
# Main function to test the get_physical_monitor_size method
def main():
    screen_info = ScreenInfo()
    width_in, height_in = screen_info.get_physical_monitor_size()
    print(f"Physical Monitor Size: {width_in:.2f} inches (Width) x {height_in:.2f} inches (Height)")
    print(f"window_width: {screen_info.window_width}")
    print(f"window_height: {screen_info.window_height}")

if __name__ == "__main__":
    main()