import os
import sys
import customtkinter as ctk
import ctypes
import json
import psutil
import tkinter as tk
from tkinter.messagebox import askyesno

# Import the consolidated trackpad view class
from intro import IntroView
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

        # Create and display the IntroView within the main container
        intro_frame = IntroView(self)
        intro_frame.display()

        self.frame_stack = [self.container]
        
        self.frames = {}

        self.touchpad_button_frame = SlidingFrame(self.container, width=self.container.winfo_width(), height=self.container.winfo_height())
        self.keyboard_button_frame = SlidingFrame(self.container, width=self.screen_info.window_width, height=self.screen_info.window_height)

        # Register the touchpad and keyboard frames in self.frames using unique keys
        self.frames["TouchpadFrame"] = self.touchpad_button_frame
        self.frames["KeyboardFrame"] = self.keyboard_button_frame

        # Main menu buttons: Trackpad, Keyboard, Taskbar, Settings, Quit
        self.main_buttons = [
            ("Trackpad", self.wrap_command(lambda: self.show_frame("TouchpadFrame"))),
            ("Keyboard", self.wrap_command(lambda: self.show_frame("KeyboardFrame"))),
            ("Taskbar", self.wrap_command(lambda: self.show_frame("Taskbar"))),
            ("Settings", self.wrap_command(lambda: self.show_frame("Settings"))),
            ("Quit", self.quit_app)
        ]

        self.main_button_objects = []
        for text, command in self.main_buttons:
            btn = BouncingButton(self.container, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)
            self.main_button_objects.append(btn)

        self.after(100, self.create_sliding_frames)

        tray_manager.start_main_tray_icon()
        self.show_main_menu()

    def create_sliding_frames(self):
        """Create the sliding frames and register frames using consistent string keys."""
        # Create Trackpad sliding frame
        self.trackpad_buttons = [
            ("Curtains", self.wrap_command(lambda: self.show_frame("TrackpadCurtains"))),
            ("Super Curtains", self.wrap_command(lambda: self.show_frame("TrackpadSuperCurtains"))),
            ("Right Click Zone", self.wrap_command(lambda: self.show_frame("TrackpadRightClick"))),
            ("Back", self.wrap_command(lambda: self.go_back()))
        ]

        for text, command in self.trackpad_buttons:
            btn = BouncingButton(self.touchpad_button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

        # Register Trackpad views using string keys
        self.frames["TrackpadCurtains"] = TouchpadView(self.container, self, mode="curtains")
        self.frames["TrackpadSuperCurtains"] = TouchpadView(self.container, self, mode="supercurtains")
        self.frames["TrackpadRightClick"] = TouchpadView(self.container, self, mode="rightclick")

        # Create Keyboard sliding frame
        self.keyboard_buttons = [
            ("Key Mapping", self.wrap_command(lambda: self.show_frame("KeyMapping"))),
            ("Key Shortcuts", self.wrap_command(lambda: self.show_frame("KeyShortcuts"))),
            ("Back", self.wrap_command(lambda: self.go_back()))
        ]

        for text, command in self.keyboard_buttons:
            btn = BouncingButton(self.keyboard_button_frame, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

        # Register Keyboard views using string keys
        self.frames["KeyMapping"] = KeyRemapView(self.container, self)
        self.frames["KeyShortcuts"] = KeyShortcutsView(self.container, self)

        # Register other views with string keys
        self.frames["Settings"] = SettingsView(self.container, self)
        self.frames["Taskbar"] = TaskbarView(self.container, self)

    def show_main_menu(self):
        """Show the main menu buttons."""
        self.hide_all_frames()
        self.hide_submenus()
        for btn in self.main_button_objects:
            btn.pack(fill="x", padx=10, pady=5, ipady=5)

    def wrap_command(self, command):
        def wrapped_command():
            if not SlidingFrame.animation_lock:
                command()
        return wrapped_command

    def show_frame(self, frame_key):
        """Show the corresponding frame and disable widgets in the current frame."""
        # Disable all widgets in the current top frame before moving to the next frame
        current_frame = self.frame_stack[-1]  # Get the top frame in the stack
        self.disable_widgets(current_frame)

        # Show the selected frame and push it onto the frame stack
        frame = self.frames[frame_key]
        frame.pack()
        self.frame_stack.append(frame)  # Push the new frame onto the stack

    def disable_widgets(self, frame):
        """Disable all buttons in the given frame."""
        for widget in frame.winfo_children():
            # Check if the widget has a 'state' attribute and disable it if it's a button
            if isinstance(widget, BouncingButton):
                widget.configure(state="disabled")

    def enable_widgets(self):
        """Enable widgets in the previous frame."""
        # Get the new top frame in the stack (either a subframe or the main menu)
        previous_frame = self.frame_stack[-1]  # Get the previous frame

        # Enable all widgets in the previous frame
        for widget in previous_frame.winfo_children():
            if isinstance(widget, BouncingButton):
                widget.configure(state="normal")

    def go_back(self):
        """Go back to the previous frame and enable widgets."""
        if len(self.frame_stack) > 1:  # Ensure there's a previous frame to go back to
            # Remove the current frame from the stack and hide it
            current_frame = self.frame_stack.pop()            
            current_frame.pack_forget()  # Hide the current frame
            # Enable widgets in the new top frame (previous frame)
            self.enable_widgets()

    def hide_all_frames(self):
        """Hide all frames."""
        for frame in self.frames.values():
            frame.pack_forget()

    def hide_submenus(self):
        """Hide all submenu buttons."""
        for btn in self.main_button_objects:
            btn.pack_forget()

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
