import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from new_ui_style import NewUIStyle
from backup_view import save_backups, BACKUP_FILE_PATH

class SettingsView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.scale_factor = NewUIStyle.get_scaling_factor()
        self.ui_style = NewUIStyle(self.scale_factor)
        self.settings_file = 'settings.json'
        self.setup_ui()

    def setup_ui(self):
        padding_x, padding_y = self.ui_style.get_padding()

        # "자동 관리자 권한" 체크박스
        self.var_admin_rights = tk.BooleanVar()
        self.var_admin_rights.set(self.load_settings().get('require_admin', False))  # 초기값 로드
        checkbox_admin = tk.Checkbutton(self, text="Automatically give admin rights", variable=self.var_admin_rights, command=self.save_admin_rights)
        self.ui_style.apply_checkbox_style(checkbox_admin)
        checkbox_admin.pack(pady=padding_y)

        # "백업 초기화" 버튼
        btn_reset_backup = tk.Button(self, text="Reset Backup File to Default", command=self.reset_backup_file)
        self.ui_style.apply_button_style(btn_reset_backup)
        btn_reset_backup.pack(pady=padding_y)

        # "Minimize to system tray" 체크박스 추가
        self.var_minimize_to_tray = tk.BooleanVar()
        self.var_minimize_to_tray.set(self.load_settings().get('minimize_to_tray', False))  # 초기값 로드
        checkbox_minimize_to_tray = tk.Checkbutton(self, text="Create a shortcut in system tray", variable=self.var_minimize_to_tray, command=self.save_minimize_to_tray)
        self.ui_style.apply_checkbox_style(checkbox_minimize_to_tray)
        checkbox_minimize_to_tray.pack(pady=padding_y)

        # "Back" 버튼
        btn_back = tk.Button(self, text="Back", command=lambda: self.controller.show_frame("MainMenu"))
        self.ui_style.apply_button_style(btn_back)
        btn_back.pack(pady=padding_y)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
                return settings
        return {}

    def save_admin_rights(self):
        settings = self.load_settings()
        settings['require_admin'] = self.var_admin_rights.get()
        with open(self.settings_file, 'w') as file:
            json.dump(settings, file)
        messagebox.showinfo("Settings Saved", "Settings have been saved.")

    def save_minimize_to_tray(self):
        settings = self.load_settings()
        settings['minimize_to_tray'] = self.var_minimize_to_tray.get()
        self.save_settings(settings)

    def save_settings(self, settings):
        with open(self.settings_file, 'w') as file:
            json.dump(settings, file, indent=4)

    def reset_backup_file(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the backup file to default?"):
            
            backups = [{} for _ in range(11)]
            save_backups(backups)  # backup_manager.py에서 제공하는 save_backups 함수 사용
    
            messagebox.showinfo("Reset Complete", "Backup file has been reset to default.")
