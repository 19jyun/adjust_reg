import os
import sys
import customtkinter as ctk
import ctypes
import json
import psutil
import tkinter as tk
from tkinter.messagebox import askyesno

# Import the consolidated trackpad view class
from trackpad.touchpad import TouchpadView
from keyboards.key_mapping import KeyRemapView
from keyboards.key_shortcuts import KeyShortcutsView
from settings.settings import SettingsView
from configuration_manager import ScreenInfo
from tray_icons import tray_manager
from taskbar.taskbars import TaskbarView
from widgets.button import BouncingButton
from widgets.sliding_frames import SlidingFrame


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
            if current_process.pid != process.pid and 'main.py' in process.cmdline():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


class MainApp(ctk.CTk):
    def __init__(self):
        if not is_admin():
            run_as_admin()

        super().__init__()

        self.screen_info = ScreenInfo()

        self.title("Trackpad Registry Manager")
        self.resizable(False, False)
        self.geometry(self.screen_info.geometry)
        self.overrideredirect(True)

        self.attributes("-topmost", True)
        self.after(1000, lambda: self.attributes("-topmost", False))

        # Main container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Main menu buttons: Trackpad, Keyboard, Taskbar, Settings, Quit
        self.main_buttons = [
            ("Trackpad", self.show_trackpad_menu),
            ("Keyboard", self.show_keyboard_menu),
            ("Taskbar", lambda: self.show_frame(TaskbarView)),
            ("Settings", lambda: self.show_frame(SettingsView)),
            ("Quit", self.quit_app)
        ]

        self.main_button_objects = []
        for text, command in self.main_buttons:
            btn = BouncingButton(self.container, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)
            self.main_button_objects.append(btn)

        self.touchpad_button_frame = SlidingFrame(self.container, width=10000, height=10000)
        # Trackpad submenu buttons: Curtains, Super Curtains, Right Click Zone, Back
        self.trackpad_buttons = [
            ("Curtains", lambda: self.show_frame((TouchpadView, "curtains"))),
            ("Super Curtains", lambda: self.show_frame((TouchpadView, "supercurtains"))),
            ("Right Click Zone", lambda: self.show_frame((TouchpadView, "rightclick"))),
            ("Back", self.touchpad_button_frame.pack_forget)
        ]
        
        for text, command in self.trackpad_buttons:
            btn = BouncingButton(self.touchpad_button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

        # Frames for each view
        self.frames = {}
        for mode in ["curtains", "supercurtains", "rightclick"]:
            frame = TouchpadView(self.container, self, mode=mode)
            self.frames[(TouchpadView, mode)] = frame
            frame.pack_forget()

        self.frames[KeyRemapView] = KeyRemapView(self.container, self)
        self.frames[KeyShortcutsView] = KeyShortcutsView(self.container, self)
        self.frames[SettingsView] = SettingsView(self.container, self)
        self.frames[TaskbarView] = TaskbarView(self.container, self)

        for frame in self.frames.values():
            frame.pack_forget()

        self.keyboard_button_frame = SlidingFrame(self.container, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.keyboard_buttons = [
            ("Key Mapping", lambda: self.show_frame(KeyRemapView)),
            ("Key Shortcuts", lambda: self.show_frame(KeyShortcutsView)),
            ("Back", self.keyboard_button_frame.pack_forget)
        ]
        
        for text, command in self.keyboard_buttons:
            btn = BouncingButton(self.keyboard_button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

        tray_manager.start_main_tray_icon()
        self.show_main_menu()

    def show_main_menu(self):
        """Show the main menu buttons."""
        self.hide_all_frames()
        self.hide_submenus()
        for btn in self.main_button_objects:
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

    def show_trackpad_menu(self):
        """Show the Trackpad submenu buttons."""
        self.touchpad_button_frame.pack()

    def show_keyboard_menu(self):
        """Show the Keyboard submenu buttons."""
        self.keyboard_button_frame.pack()

    def show_frame(self, frame_key):
        """
        Consolidated method to show any frame.
        Hides all frames and submenus, then displays the specified frame.
        
        Args:
            frame_key: A key representing the frame to show. This can be a class (e.g., SettingsView)
                       or a tuple for TouchpadView with a specific mode (e.g., (TouchpadView, "curtains")).
        """
        #self.hide_all_frames()
        #self.hide_submenus()

        # Show the corresponding frame
        frame = self.frames[frame_key]
        frame.pack()

    def hide_all_frames(self):
        """Hide all frames."""
        for frame in self.frames.values():
            frame.pack_forget()

    def hide_submenus(self):
        """Hide all submenu buttons."""
        for btn in self.main_button_objects:
            btn.pack_forget()
        #self.touchpad_button_frame.pack_forget()
        #self.keyboard_button_frame.pack_forget()

    def load_settings(self):
        """Load settings from settings.json."""
        with open("settings/settings.json", "r") as f:
            return json.load(f)

    def quit_app(self):
        """Quit the application."""
        settings = self.load_settings()
        if settings['minimize_to_tray'] is False:
            if askyesno("Quit", "Do you want to quit the application?"):
                self.quit()
                os._exit(0)
            else:
                return
        else:
            # Minimize to tray on, hide the window instead of closing
            self.withdraw()


if __name__ == "__main__":
    if is_already_running():
        print("An instance of this program is already running.")
        sys.exit(0)

    app = MainApp()
    app.mainloop()
