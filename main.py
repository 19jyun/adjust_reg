import os
import sys
import customtkinter as ctk
import ctypes
import json
import psutil

import tkinter as tk
from tkinter.messagebox import askyesno

from trackpad.curtains import CurtainsView
from trackpad.supercurtains import SuperCurtainsView
from trackpad.rightclick import RightClickView
from settings.settings import SettingsView
from backup.backups import BackupView
from tray_icons import tray_manager
from ctk import uniform_look
from ctypes import wintypes, windll

ctypes.windll.shcore.SetProcessDpiAwareness(2)

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
    

def is_admin():
    """Check if the current script is run as an administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(argv=None, debug=False):
    """Re-run the script as an administrator."""
    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Handle case for PyInstaller packaged executable
        arguments = map(str, argv[1:])
    else:
        arguments = map(str, argv)
    argument_line = u' '.join(arguments)
    executable = sys.executable
    if debug:
        print('Command line:', executable, argument_line)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, argument_line, None, 1)  # Change 1 to 0 for no terminal
    sys.exit(0)

def is_already_running():
    """Check if the program is already running to prevent multiple instances."""
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if current_process.pid != process.pid and 'new_main.py' in process.cmdline():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

class MainApp(ctk.CTk):
    def __init__(self):
        
        if not is_admin():
            run_as_admin()  # Request re-run as admin if necessary
        
        super().__init__()        
        self.title("Trackpad registry manager")
        self.resizable(False, False)
        self.geometry(self.get_window_size())
        self.overrideredirect(True)

                # 창을 처음 실행할 때 최상위로 설정
        self.attributes("-topmost", True)
        self.after(1000, lambda: self.attributes("-topmost", False))

        # 메인 프레임 (여러 프레임을 전환할 수 있는 공간)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # 메뉴 프레임
        self.menu_frame = ctk.CTkFrame(self.container)
        self.menu_frame.pack(fill="both", expand=True)

        # 메인 메뉴 버튼 정의
        self.buttons = [
            ("Set Curtains", self.show_curtains_view),
            ("Set Super Curtains", self.show_super_curtains_view),
            ("Set Right Click Zone", self.show_right_click_view),
            ("Backup Manager", self.show_backup_view),
            ("Settings", self.show_settings_view),
            ("Quit", self.quit_app)
        ]
        
        self.button_objects = []
        for text, command in self.buttons:
            btn = ctk.CTkButton(self.menu_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)
            self.button_objects.append(btn)

        # Back 버튼 생성 (초기에는 숨김)
        self.back_button = ctk.CTkButton(self.menu_frame, text="Back", command=self.show_main_menu)
        self.back_button.pack(fill="x", padx=10, pady=5, ipady=5)
        self.back_button.pack_forget()

        # 각 화면에 해당하는 프레임 정의
        self.frames = {}
        for F in (CurtainsView, SuperCurtainsView, RightClickView, BackupView, SettingsView):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.pack_forget()

        tray_manager.start_main_tray_icon()

        self.show_main_menu()

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
        # Get scaled screen width and height (accounting for DPI)
        #screen_width = int(user32.GetSystemMetrics(0) / scaling_factor)
        #screen_height = int(user32.GetSystemMetrics(1) / scaling_factor)
        
        screen_width = int(user32.GetSystemMetrics(0))
        screen_height = int(user32.GetSystemMetrics(1))
        
        # Adjust window size based on DPI scaling factor
        window_width = int((screen_width * 0.26))
        window_height = int((screen_height * 0.65))
        
        # Calculate taskbar height and subtract it from the vertical position
        taskbar_height = self.get_taskbar_height()

        # Position the window in the bottom-right corner, above the taskbar
        position_right = screen_width - window_width - 5  # 5px margin from right edge
        position_down = screen_height - window_height - taskbar_height - 5  # 5px margin from taskbar
        
        # Adjust window size based on DPI scaling factor
        window_width = int((screen_width * 0.26)/scaling_factor)
        window_height = int((screen_height * 0.65)/scaling_factor)
        
        # print("Scaling factor:", scaling_factor)
        # print("Screen width:", screen_width)
        # print("Screen height:", screen_height)
        # print("Window width:", window_width)
        # print("Window height:", window_height)
        # print("Taskbar height:", taskbar_height)
        # print("Position right:", position_right)
        # print("Position down:", position_down)
        
        return f"{window_width}x{window_height}+{position_right}+{position_down}"



    def show_main_menu(self):
        self.back_button.pack_forget()
        for btn in self.button_objects:
            btn.pack(fill="x", padx=10, pady=5, ipady=5)
        self.hide_all_frames()

    def hide_main_menu(self):
        for btn in self.button_objects:
            btn.pack_forget()
        self.back_button.pack(fill="x", padx=10, pady=5, ipady=5)

    def hide_all_frames(self):
        for frame in self.frames.values():
            frame.pack_forget()

    def show_frame(self, page):
        self.hide_all_frames()
        frame = self.frames[page]
        frame.pack(fill="both", expand=True)
        self.hide_main_menu()

    def show_curtains_view(self):
        self.show_frame(CurtainsView)

    def show_super_curtains_view(self):
        self.show_frame(SuperCurtainsView)

    def show_right_click_view(self):
        self.show_frame(RightClickView)

    def show_backup_view(self):
        self.show_frame(BackupView)

    def show_settings_view(self):
        self.show_frame(SettingsView)

    def load_settings(self):
        with open("settings/settings.json", "r") as f:
            return json.load(f)

    def quit_app(self):
        settings = self.load_settings()
        if settings['minimize_to_tray'] is False:
            if askyesno("Quit", "Do you want to quit the application?"):
                self.quit()
                os._exit(0)
            else:
                return
        else: # minimize to tray on, hide the window instead of closing
            self.withdraw()

if __name__ == "__main__":
    
    if is_already_running():
        print("An instance of this program is already running.")
        sys.exit(0)
        
    app = MainApp()
    app.mainloop()
