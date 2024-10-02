import customtkinter as ctk
import json
import shutil
import os
import winreg

import tkinter as tk
from tkinter import messagebox
from tray_icons import tray_manager
from widgets.button import BouncingButton
from widgets.sliding_frames import SlidingFrame
from configuration_manager import ScreenInfo

# settings.json 파일 경로
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
class SettingsView(SlidingFrame):
    def __init__(self, parent, controller):
        
        self.screen_info = ScreenInfo()
        
        super().__init__(parent, width=self.screen_info.window_width, height=self.screen_info.window_height)
        self.controller = controller
        
        
        # Load settings.json
        self.settings = self.load_settings()

        # Create the UI elements
        self.create_ui_elements()

        # Define registry paths and values to delete
        self.registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad',
             ['CurtainTop', 'CurtainLeft', 'CurtainRight', 'SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight', 'RightClickZoneWidth', 'RightClickZoneHeight']),
            
            (winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Keyboard Layout',
             ['Scancode Map']),  # Single value for keyboard layout
            
            (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3',
             ['Settings']),  # Binary value for taskbar position and auto-hide
            
            (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced',
             ['TaskbarSmallIcons', 'TaskbarAl', 'ShowClock', 'TaskbarGlomLevel']),  # Taskbar advanced options
            
            (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband',
             ['MinThumbSizePx'])  # Taskbar thumbnail preview size
        ]

    def create_ui_elements(self):
        """Create the UI elements for the settings view."""
        self.admin_rights_var = ctk.BooleanVar(value=self.settings.get("require_admin", False))
        self.admin_rights_checkbox = ctk.CTkCheckBox(self, text="Automatically give admin rights", variable=self.admin_rights_var, command=self.toggle_admin_rights)
        self.admin_rights_checkbox.pack(pady=10)

        self.reset_button = BouncingButton(self, text="Reset All Changes", command=self.reset_options)
        self.reset_button.pack(pady=10)

        self.minimize_to_tray_var = ctk.BooleanVar(value=self.settings.get("minimize_to_tray", False))
        self.minimize_to_tray_checkbox = ctk.CTkCheckBox(self, text="Minimize to system tray instead of completely quitting", variable=self.minimize_to_tray_var, command=self.toggle_minimize_to_tray)
        self.minimize_to_tray_checkbox.pack(pady=10)

        self.display_discharge_rate_var = ctk.BooleanVar(value=self.settings.get("Display discharge rate", False))
        self.display_discharge_rate_checkbox = ctk.CTkCheckBox(self, text="Always display battery discharge rate", variable=self.display_discharge_rate_var, command=self.toggle_display_discharge_rate)
        self.display_discharge_rate_checkbox.pack(pady=10)
        
        BouncingButton(self, text="Back", command=self.controller.wrap_command(self.controller.go_back)).pack(pady=10)

    def load_settings(self):
        """Load settings from settings.json"""
        try:
            with open(SETTINGS_PATH, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"require_admin": False, "minimize_to_tray": False, "Display discharge rate": False}

    def save_settings(self):
        """Save settings to settings.json"""
        with open(SETTINGS_PATH, "w") as file:
            json.dump(self.settings, file, indent=4)

    def toggle_admin_rights(self):
        """Toggle admin rights setting"""
        self.settings["require_admin"] = self.admin_rights_var.get()
        self.save_settings()

    def toggle_minimize_to_tray(self):
        """Toggle minimize to tray setting"""
        minimize_to_tray = self.minimize_to_tray_var.get()
        self.settings['minimize_to_tray'] = minimize_to_tray

        if not minimize_to_tray and self.display_discharge_rate_var.get():
            ask_user = messagebox.askyesno(
                "Minimize to Tray Required for Battery Discharge Rate",
                "To display the battery discharge rate in the system tray, you need to enable 'Minimize to tray'. Are you sure you want to turn this option off?"
            )
            if ask_user:
                self.display_discharge_rate_var.set(False)
                self.settings['Display discharge rate'] = False
                tray_manager.stop_battery_discharge_icon()
            else:
                self.minimize_to_tray_var.set(True)
                self.settings['minimize_to_tray'] = True

        self.save_settings()

    def toggle_display_discharge_rate(self):
        """Toggle display discharge rate setting"""
        display = self.display_discharge_rate_var.get()
        minimize_to_tray = self.settings.get('minimize_to_tray', False)

        if not minimize_to_tray and display:
            user_response = messagebox.askyesno(
                "Minimize to Tray Required",
                "To display the battery discharge rate in the system tray, you need to enable 'Minimize to tray'. Would you like to enable this option?"
            )
            if user_response:
                self.minimize_to_tray_var.set(True)
                self.settings['minimize_to_tray'] = True
                self.settings['Display discharge rate'] = True
                tray_manager.start_battery_discharge_icon()
            else:
                self.display_discharge_rate_var.set(False)
        else:
            if display:
                tray_manager.start_battery_discharge_icon()
            else:
                tray_manager.stop_battery_discharge_icon()

            self.settings['Display discharge rate'] = display
        self.save_settings()

    def reset_options(self):
        """Reset registry keys to default values and reset settings"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all modified settings to default? This will undo all changes made by this program."):
            # Delete only the specific registry values added by this program
            for root_key, path, values in self.registry_paths:
                self.delete_registry(root_key, path, values)
            
            # Restart Explorer for taskbar settings
            os.system("taskkill /f /im explorer.exe & start explorer.exe")
            
            messagebox.showinfo("Reset Complete", "All settings have been reset to default.")

    def delete_registry(self, registry_root, registry_path, values_to_delete):
        """Delete specific registry values inside the specified registry path."""
        try:
            reg_key = winreg.OpenKey(registry_root, registry_path, 0, winreg.KEY_ALL_ACCESS)
            for value_name in values_to_delete:
                try:
                    winreg.DeleteValue(reg_key, value_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(reg_key)
        except FileNotFoundError:
            print(f"Registry path '{registry_path}' not found. Skipping...")
        except PermissionError:
            print(f"Permission denied for '{registry_path}'. Run the script as administrator.")
        except Exception as e:
            print(f"An error occurred while deleting registry values in '{registry_path}': {e}")
