import customtkinter as ctk
import json
import shutil
import os

import tkinter as tk
from tkinter import messagebox
from tray_icons import tray_manager

# settings.json 파일 경로
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
BACKUP_FILE_PATH = os.path.join(os.path.dirname(__file__), "../backup/backups.json")
ORIGINAL_BACKUP_FILE_PATH = os.path.join(os.path.dirname(__file__), "../original_registry.json")

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # settings.json 파일 로드
        self.settings = self.load_settings()

        # "Automatically give admin rights" 체크박스
        self.admin_rights_var = ctk.BooleanVar(value=self.settings.get("require_admin", False))
        self.admin_rights_checkbox = ctk.CTkCheckBox(self, text="Automatically give admin rights", variable=self.admin_rights_var, command=self.toggle_admin_rights)
        self.admin_rights_checkbox.pack(pady=10)

        # "Reset Backup File to Default" 버튼
        self.reset_backup_button = ctk.CTkButton(self, text="Reset Backup File to Default", command=self.reset_backup_file)
        self.reset_backup_button.pack(pady=10)

        # "Minimize to system tray instead of completely quitting" 체크박스
        self.minimize_to_tray_var = ctk.BooleanVar(value=self.settings.get("minimize_to_tray", False))
        self.minimize_to_tray_checkbox = ctk.CTkCheckBox(self, text="Minimize to system tray instead of completely quitting", variable=self.minimize_to_tray_var, command=self.toggle_minimize_to_tray)
        self.minimize_to_tray_checkbox.pack(pady=10)

        # "Always display battery discharge rate" 체크박스
        self.display_discharge_rate_var = ctk.BooleanVar(value=self.settings.get("Display discharge rate", False))
        self.display_discharge_rate_checkbox = ctk.CTkCheckBox(self, text="Always display battery discharge rate", variable=self.display_discharge_rate_var, command=self.toggle_display_discharge_rate)
        self.display_discharge_rate_checkbox.pack(pady=10)

    def load_settings(self):
        """settings.json 파일 로드"""
        try:
            with open(SETTINGS_PATH, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"require_admin": False, "minimize_to_tray": False, "Display discharge rate": False}

    def save_settings(self):
        """settings.json 파일에 변경 사항 저장"""
        with open(SETTINGS_PATH, "w") as file:
            json.dump(self.settings, file, indent=4)

    def toggle_admin_rights(self):
        """admin_rights 토글"""
        self.settings["require_admin"] = self.admin_rights_var.get()
        self.save_settings()

    def toggle_minimize_to_tray(self):
        minimize_to_tray = self.minimize_to_tray_var.get()
        self.settings['minimize_to_tray'] = minimize_to_tray

        if not minimize_to_tray:  # If minimizing to tray is disabled, stop battery discharge icon
            if self.display_discharge_rate_var.get():
                
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
                    
    
        self.save_settings()

    def toggle_display_discharge_rate(self):
        display = self.display_discharge_rate_var.get()
        minimize_to_tray = self.settings.get('minimize_to_tray', False)

        if not minimize_to_tray:
            if display:
                # Ask the user if they want to enable minimizing to the tray
                user_response = messagebox.askyesno(
                    "Minimize to Tray Required",
                    "To display the battery discharge rate in the system tray, you need to enable 'Minimize to tray'. Would you like to enable this option?"
                )
                if user_response:
                    # Automatically enable the "Minimize to tray" option
                    self.minimize_to_tray_var.set(True)
                    self.settings['minimize_to_tray'] = True
                    self.settings['Display discharge rate'] = True
                    self.save_settings()
                    
                    # Start the battery discharge tray icon
                    tray_manager.start_battery_discharge_icon()

                else:
                    self.display_discharge_rate_var.set(False)
        else:
            # Proceed normally if the "Minimize to tray" is already enabled
            if display:
                tray_manager.start_battery_discharge_icon()
            else:
                tray_manager.stop_battery_discharge_icon()

            self.settings['Display discharge rate'] = display
            self.save_settings()

    def reset_backup_file(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the backup file to default?"):
            backup_file = BACKUP_FILE_PATH
            original_file = ORIGINAL_BACKUP_FILE_PATH
            
            if os.path.exists(original_file):
                try:
                    with open(original_file, "r") as orig_file:
                        data = json.load(orig_file)
                    with open(backup_file, "w") as backup_file:
                        json.dump(data, backup_file)
                    print(f"Copied data from {original_file} to {backup_file}")
                except Exception as e:
                    print(f"Error copying data from {original_file} to {backup_file}: {e}")
            else:
                # Create an empty backups.json if original_registry.json does not exist
                with open(backup_file, "w") as f:
                    json.dump({}, f)
                print(f"{original_file} does not exist. Created empty {backup_file}")
    
            messagebox.showinfo("Reset Complete", "Backup file has been reset to default.")

