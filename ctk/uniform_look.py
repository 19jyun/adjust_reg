import customtkinter as ctk
import ctypes
from ctypes import wintypes

# RECT structure definition
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

class Style:
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
        
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
                
        self.window_width = int(self.screen_width * 0.26)
        self.window_height = int(self.screen_height * 0.65)
        self.position_right = int((self.screen_width - self.window_width) - 5)
        self.position_down = int((self.screen_height - self.window_height) - 5)
        
        self.button_width = int(self.window_width // 10)
        self.button_height = int(self.window_height // 30)
        
        self.label_width = int(self.window_width // 10)
        self.label_height = int(self.window_height // 30)
        
        # Delay font creation
        self._button_font = None
        self._label_font = None
        self._checkbox_font = None
        self._entry_font = None
        
        self.padding_x = int(10 * self.scale_factor)
        self.padding_y = int(10 * self.scale_factor)
        
        self.slider_length = int(self.window_width // 2)
        
        self.entry_width = int(self.window_width // 10)
        self.entry_height = int(self.window_height // 60)
        self.entry_font_size = 12
        
    @property
    def button_font(self):
        if self._button_font is None:
            self._button_font = ctk.CTkFont(family="Poplar Std", size=20, weight='bold')
        return self._button_font
    
    @property
    def label_font(self):
        if self._label_font is None:
            self._label_font = ctk.CTkFont(family="Poplar Std", size=20, weight='bold')
        return self._label_font
    
    @property
    def checkbox_font(self):
        if self._checkbox_font is None:
            self._checkbox_font = ctk.CTkFont(family="Poplar Std", size=15, weight='bold')
        return self._checkbox_font
    
    @property
    def entry_font(self):
        if self._entry_font is None:
            self._entry_font = ctk.CTkFont(family="Poplar Std", size=15, weight='bold')
        return self._entry_font
        
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
    
    def apply_button_style(self, button):
        button.configure(
            fg_color="light blue",  # 배경색
            text_color="black",  # 텍스트 색상
            font = self.button_font,  # 폰트
            hover_color="blue",  # 호버 시 색상
            corner_radius=10,  # 모서리 반경
            width=self.button_width,  # 너비
            height=self.button_height  # 높이
        )
        
    def apply_label_style(self, label):
        label.configure(  # 배경색
            text_color="White",  # 텍스트 색상
            font = self.label_font,  # 폰트
            corner_radius=10,  # 모서리 반경
            width=self.label_width,  # 너비
            height=self.label_height  # 높이
        )
        
    def apply_entry_style(self, entry):
        entry.configure(
            fg_color="light blue",  # 배경색
            text_color="black",  # 텍스트 색상
            font = self.entry_font,  # 폰트
            corner_radius=10,  # 모서리 반경
            width=self.entry_width,  # 너비
            height=self.entry_height  # 높이
        )
        
    def apply_slider_style(self, slider):
        slider.configure(
            fg_color="light blue",  # 배경색
            width=self.slider_length,  # 너비
            height=self.entry_height  # 높이
        )
        
    def apply_checkbox_style(self, checkbox):
        checkbox.configure(
            fg_color="light blue",  # 배경색
            text_color="black",  # 텍스트 색상
            font = self.checkbox_font,  # 폰트
            corner_radius=10,  # 모서리 반경
            width=self.checkbox_width,  # 너비
            height=self.checkbox_height  # 높이
        )
        
    def get_padding(self):
        return self.padding_x, self.padding_y
    
    def get_window_geometry(self):
        return f"{self.window_width}x{self.window_height}+{self.position_right}+{self.position_down}"

    
    def make_window_topmost(self, window):
        window.left()
        window.attributes("-topmost", True)
        window.after(100, lambda: window.attributes("-topmost", False))
        window.focus_force()
        
    def create_frame(self, parent):
    # Create a basic frame without scrolling functionality
        frame = ctk.CTkFrame(
            master=parent, 
            width=self.window_width, 
            height=self.window_height, 
            corner_radius=10, 
            fg_color="white", 
            border_color="black", 
            border_width=2
        )
        # Pack the frame to fill the parent widget
        frame.pack(fill="both", expand=True)
        
        return frame
        
    def _on_mouse_wheel(self, event, canvas):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")