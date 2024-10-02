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
        
    def get_window_size(self):
        scaling_factor = self.get_scaling_factor()

        user32 = ctypes.windll.user32
        
        screen_width = int(user32.GetSystemMetrics(0))
        screen_height = int(user32.GetSystemMetrics(1))
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Adjust window size based on DPI scaling factor
        window_width = int((screen_width * 0.26))
        window_height = int((screen_height * 0.65))
        
        # Calculate taskbar height and subtract it from the vertical position
        taskbar_height = self.get_taskbar_height()

        # Position the window in the bottom-right corner, above the taskbar
        position_right = screen_width - window_width - 5  # 5px margin from right edge
        position_down = screen_height - window_height - taskbar_height - 5  # 5px margin from taskbar
        
        # Adjust window size based on DPI scaling factor
        dpi_window_width = int((screen_width * 0.26)/scaling_factor)
        dpi_window_height = int((screen_height * 0.65)/scaling_factor)
        
        self.window_width = dpi_window_width
        self.window_height = dpi_window_height
        
        return f"{dpi_window_width}x{dpi_window_height}+{position_right}+{position_down}"
    