import tkinter as tk
from tkinter import messagebox
import json
import os
from new_ui_style import NewUIStyle
from backup.backup_view import save_backups, BACKUP_FILE_PATH
import tray_icons.tray_manager as tray_manager

class SettingsView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.scale_factor = NewUIStyle.get_scaling_factor()
        self.ui_style = NewUIStyle(self.scale_factor)
        self.settings_file = 'settings/settings.json'
        self.setup_ui()
            
    def setup_ui(self):
        padding_x, padding_y = self.ui_style.get_padding()

        # "Automatically give admin rights" checkbox
        self.var_admin_rights = tk.BooleanVar()
        self.var_admin_rights.set(self.load_settings().get('require_admin', False))  # Load initial value
        checkbox_admin = tk.Checkbutton(self, text="Automatically give admin rights", variable=self.var_admin_rights, command=self.save_admin_rights)
        self.ui_style.apply_checkbox_style(checkbox_admin)
        checkbox_admin.pack(pady=padding_y)

        # "Reset Backup File to Default" button
        btn_reset_backup = tk.Button(self, text="Reset Backup File to Default", command=self.reset_backup_file)
        self.ui_style.apply_button_style(btn_reset_backup)
        btn_reset_backup.pack(pady=padding_y)

        # "Minimize to system tray" checkbox
        self.var_minimize_to_tray = tk.BooleanVar()
        self.var_minimize_to_tray.set(self.load_settings().get('minimize_to_tray', False))  # Load initial value
        checkbox_minimize_to_tray = tk.Checkbutton(self, text="Minimize to system tray instead of completely quitting", variable=self.var_minimize_to_tray, command=self.toggle_minimize_to_tray)
        self.ui_style.apply_checkbox_style(checkbox_minimize_to_tray)
        checkbox_minimize_to_tray.pack(pady=padding_y)

        # "Always display battery discharge rate" checkbox
        self.var_display_discharge_rate = tk.BooleanVar()
        self.var_display_discharge_rate.set(self.load_settings().get('Display discharge rate', False))  # Load initial value
        checkbox_display_discharge_rate = tk.Checkbutton(self, text="Always display battery discharge rate", variable=self.var_display_discharge_rate, command=self.toggle_display_discharge_rate)
        self.ui_style.apply_checkbox_style(checkbox_display_discharge_rate)
        checkbox_display_discharge_rate.pack(pady=padding_y)

        # "Back" button
        btn_back = tk.Button(self, text="Back", command=lambda: self.controller.show_frame("MainMenu"))
        self.ui_style.apply_button_style(btn_back)
        btn_back.pack(pady=padding_y)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
                return settings
        return {}

    def save_settings(self, settings):
        with open(self.settings_file, 'w') as file:
            json.dump(settings, file, indent=4)

    def save_admin_rights(self):
        settings = self.load_settings()
        settings['require_admin'] = self.var_admin_rights.get()
        self.save_settings(settings)
        messagebox.showinfo("Settings Saved", "Settings have been saved.")

    def save_minimize_to_tray(self):
        settings = self.load_settings()
        settings['minimize_to_tray'] = self.var_minimize_to_tray.get()
        self.save_settings(settings)

    def toggle_minimize_to_tray(self):
        minimize_to_tray = self.var_minimize_to_tray.get()
        settings = self.load_settings()
        settings['minimize_to_tray'] = minimize_to_tray

        if not minimize_to_tray:  # If minimizing to tray is disabled, stop battery discharge icon
            if self.var_display_discharge_rate.get():
                self.var_display_discharge_rate.set(False)
                settings['Display discharge rate'] = False
                tray_manager.stop_battery_discharge_icon()

        self.save_settings(settings)

    def toggle_display_discharge_rate(self):
        display = self.var_display_discharge_rate.get()
        settings = self.load_settings()
        minimize_to_tray = settings.get('minimize_to_tray', False)

        if not minimize_to_tray:
            if display:
                # Ask the user if they want to enable minimizing to the tray
                user_response = messagebox.askyesno(
                    "Minimize to Tray Required",
                    "To display the battery discharge rate in the system tray, you need to enable 'Minimize to tray'. Would you like to enable this option?"
                )
                if user_response:
                    # Automatically enable the "Minimize to tray" option
                    self.var_minimize_to_tray.set(True)
                    settings['minimize_to_tray'] = True
                    settings['Display discharge rate'] = True
                    self.save_settings(settings)
                    
                    # Start the battery discharge tray icon
                    tray_manager.start_battery_discharge_icon()

                else:
                    self.var_display_discharge_rate.set(False)
        else:
            # Proceed normally if the "Minimize to tray" is already enabled
            if display:
                tray_manager.start_battery_discharge_icon()
            else:
                tray_manager.stop_battery_discharge_icon()

            settings['Display discharge rate'] = display
            self.save_settings(settings)

    def reset_backup_file(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the backup file to default?"):
            backup_file = BACKUP_FILE_PATH
            original_file = 'original_registry.json'
            
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
