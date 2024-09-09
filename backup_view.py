import tkinter as tk
from tkinter import messagebox
import os
import json
from new_ui_style import NewUIStyle
from reboot_prompt import prompt_reboot

BACKUP_FILE_PATH = "backups.json"

# save_backups 함수를 클래스 외부로 이동시킵니다.
def save_backups(data):
    with open(BACKUP_FILE_PATH, 'w') as file:
        file.write(json.dumps(data))  # 데이터를 JSON 문자열로 변환하여 파일에 씁니다.

class BackupView(tk.Frame):
    def __init__(self, parent, controller, set_curtains_values, set_super_curtains_values, set_right_click_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.set_curtains_values = set_curtains_values
        self.set_super_curtains_values = set_super_curtains_values
        self.set_right_click_values = set_right_click_values
        self.get_current_curtains_values = get_current_curtains_values
        self.get_current_super_curtains_values = get_current_super_curtains_values
        self.get_current_right_click_values = get_current_right_click_values

        # ui_style 속성을 초기화합니다.
        self.ui_style = controller.ui_style

        # backup_file_path 속성을 초기화합니다.
        self.backup_file_path = BACKUP_FILE_PATH

        label = tk.Label(self, text="Backup Manager")
        label.pack(pady=10, padx=10)

        self.backups = [{} for _ in range(10)]
        self.restore_buttons = []

        self.load_backups()
        self.setup_ui()

    def setup_ui(self):
        padding_x, padding_y = self.ui_style.get_padding()

        # Slot 0 "Default" button
        default_frame = tk.Frame(self)
        default_frame.pack(pady=padding_y)

        default_button = tk.Button(default_frame, text="Default",
                                   command=lambda: self.restore_registry(0))
        self.ui_style.apply_button_style(default_button)
        default_button.pack(side="left", padx=padding_x)

        default_restore_button = tk.Button(default_frame, text="Restore",
                                           command=lambda: self.restore_registry(0))
        self.ui_style.apply_button_style(default_restore_button)
        default_restore_button.pack(side="left", padx=padding_x)
        self.restore_buttons.append(default_restore_button)
        
        default_detail_button = tk.Button(default_frame, text="Detail",
                                  command=lambda: self.show_details(0))
        self.ui_style.apply_button_style(default_detail_button)
        default_detail_button.pack(side="left", padx=padding_x)


        # Slots 1-9 Backup, Restore, and Detail buttons
        for i in range(1, 10):
            slot_frame = tk.Frame(self)
            slot_frame.pack(pady=padding_y)

            slot_button = tk.Button(slot_frame, text=f"Slot {i + 1}",
                                    command=lambda slot=i: self.backup_registry(slot))
            self.ui_style.apply_button_style(slot_button)
            slot_button.pack(side="left", padx=padding_x)

            restore_button = tk.Button(slot_frame, text="Restore",
                                       command=lambda slot=i: self.restore_registry(slot))
            self.ui_style.apply_button_style(restore_button)
            restore_button.pack(side="left", padx=padding_x)

            detail_button = tk.Button(slot_frame, text="Detail",
                                      command=lambda slot=i: self.show_details(slot))
            self.ui_style.apply_button_style(detail_button)
            detail_button.pack(side="left", padx=padding_x)

            self.restore_buttons.append(restore_button)

        # Back button
        btn_back = tk.Button(self, text="Back", command=lambda: self.controller.show_frame("MainMenu"))
        self.ui_style.apply_button_style(btn_back)
        btn_back.pack(pady=padding_y)

        self.update_buttons()

    def load_backups(self):
        if os.path.exists(self.backup_file_path):
            with open(self.backup_file_path, 'r') as file:
                try:
                    loaded_backups = json.load(file)
                    for i, backup in enumerate(loaded_backups):
                        self.backups[i] = backup
                except json.JSONDecodeError:
                    print("Error reading backup file.")
        else:
            save_backups(self.backups)

    def backup_registry(self, slot):
        print(f"Backing up registry for slot {slot}")
        
        curtains_values = self.get_current_curtains_values()
        super_curtains_values = self.get_current_super_curtains_values()
        right_click_values = self.get_current_right_click_values()

        print("Curtains values:", curtains_values)
        print("Super Curtains values:", super_curtains_values)
        print("Right-click values:", right_click_values)

        # 레지스트리 값을 백업에 저장 (CurtainBottom, SuperCurtainBottom을 제외)
        self.backups[slot] = {
            'Curtains': {key: curtains_values[key] for key in ['CurtainTop', 'CurtainLeft', 'CurtainRight'] if key in curtains_values},
            'Super Curtains': {key: super_curtains_values[key] for key in ['SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight'] if key in super_curtains_values},
            'Right-click Zone': {key: right_click_values[key] for key in ['RightClickZoneWidth', 'RightClickZoneHeight'] if key in right_click_values},
        }

        save_backups(self.backups)
        messagebox.showinfo("Backup", f"Registry values backed up in slot {slot + 1}.")
        self.update_buttons()

    def restore_registry(self, slot):
        backup_data = self.backups[slot]
        if not backup_data:
            messagebox.showinfo("Restore", f"No backup available in slot {slot + 1}.")
            return

        self.set_curtains_values(backup_data['Curtains'])
        self.set_super_curtains_values(backup_data['Super Curtains'])
        self.set_right_click_values(backup_data['Right-click Zone'])

        messagebox.showinfo("Restore", f"Registry values restored from slot {slot + 1}.")
        prompt_reboot()

    def show_details(self, slot):
        backup_data = self.backups[slot]
        if not backup_data:
            messagebox.showinfo("Details", f"No backup available in slot {slot + 1}.")
        else:
            details = f"Slot {slot + 1} Backup Details:\n\n"
            details += "Curtains:\n"
            details += "\n".join(f"{key}: {value}" for key, value in backup_data['Curtains'].items())
            details += "\n\nSuper Curtains:\n"
            details += "\n".join(f"{key}: {value}" for key, value in backup_data['Super Curtains'].items())
            details += "\n\nRight-click Zone:\n"
            details += "\n".join(f"{key}: {value}" for key, value in backup_data['Right-click Zone'].items())
            messagebox.showinfo("Details", details)

    def update_buttons(self):
        for i, btn in enumerate(self.restore_buttons):
            if self.backups[i]:
                btn.config(text="Restore", state=tk.NORMAL)
            else:
                btn.config(text="Empty", state=tk.DISABLED)

    def initialize_reset_slot(self):
        self.backups[0] = {
            'Curtains': {'CurtainTop': 0, 'CurtainLeft': 0, 'CurtainRight': 0},
            'Super Curtains': {'SuperCurtainTop': 0, 'SuperCurtainBottom': 0, 'SuperCurtainLeft': 0, 'SuperCurtainRight': 0},
            'Right-click Zone': {'RightClickZoneWidth': 0, 'RightClickZoneHeight': 0}
        }
        save_backups()
        self.update_buttons()
        
    def show(self):
        """BackupView가 표시될 때 호출"""
        self.load_backups()  # 최신 백업 파일을 불러옴
        self.update_buttons()  # 버튼 상태를 업데이트
