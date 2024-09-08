import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk

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

class NewUIStyle:
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
        self.button_height_size = int(2 * self.scale_factor)
        self.button_width_size = int(10 * self.scale_factor)
        self.button_font_size = int(12 * self.scale_factor)
        self.label_font_size = int(14 * self.scale_factor)
        self.checkbox_font_size = int(12 * self.scale_factor)
        self.padding_x = int(10 * self.scale_factor)
        self.padding_y = int(10 * self.scale_factor)
        self.slider_length = int(200 * self.scale_factor)
        self.entry_width = int(15 * self.scale_factor)
        self.entry_height = int(2 * self.scale_factor)
        self.entry_font_size = int(12 * self.scale_factor)

        # Window size properties
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Window size and position calculation
        self.window_width = int(self.screen_width * 0.26)
        self.window_height = int(self.screen_height * 0.65)
        self.position_right = int((self.screen_width - self.window_width) - 5)
        self.position_down = int((self.screen_height - self.window_height - self.get_taskbar_height()) - 5)

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
        button.config(height=self.button_height_size, width=self.button_width_size, font=("Arial", self.button_font_size))

    def apply_label_style(self, label):
        label.config(font=("Arial", self.label_font_size))

    def apply_entry_style(self, entry):
        entry.config(width=self.entry_width, font=("Arial", self.entry_font_size))

    def apply_slider_style(self, slider):
        slider.config(length=self.slider_length)

    def apply_checkbox_style(self, checkbox):
        checkbox.config(font=("Arial", self.checkbox_font_size))

    def get_padding(self):
        return self.padding_x, self.padding_y

    def get_window_geometry(self):
        return f"{self.window_width}x{self.window_height}+{self.position_right}+{self.position_down}"

    def make_window_topmost(self, window):
        window.lift()  # Bring window to top
        window.attributes('-topmost', True)  # Make it always topmost
        window.after(100, lambda: window.attributes('-topmost', False))  # Revert after 100ms
        window.focus_force()  # Set focus to the window

    def center_widgets(self, root):
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
        x = (screen_width / 2) - (size[0] / 2)
        y = (screen_height / 2) - (size[1] / 2)
        root.geometry(f"{size[0]}x{size[1]}+{int(x)}+{int(y)}")

    def create_scrollable_frame(self, parent):
        # Create a scrollable frame
        frame = tk.Frame(parent)
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame.scrollable_frame = scrollable_frame

        # Bind mouse scroll events
        canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>", lambda event: self._on_mouse_wheel(event, canvas)))
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))

        return frame
    
    def _on_mouse_wheel(self, event, canvas):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
