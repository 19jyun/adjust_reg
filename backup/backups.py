import customtkinter as ctk
from tkinter import messagebox
import os
import json
from trackpad.curtains import CurtainsView
from trackpad.supercurtains import SuperCurtainsView
from trackpad.rightclick import RightClickView

BACKUP_FILE_PATH = os.path.join("backup", "backups.json")

# JSON 파일에 데이터를 저장하는 함수
def save_backups(data):
    with open(BACKUP_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

class BackupView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # CurtainsView, SuperCurtainsView, RightClickView 인스턴스 생성
        self.curtains_view = CurtainsView(parent, controller)
        self.supercurtains_view = SuperCurtainsView(parent, controller)
        self.rightclick_view = RightClickView(parent, controller)

        # 백업 파일 경로
        self.backup_file_path = BACKUP_FILE_PATH

        # 백업 데이터를 저장할 리스트 (슬롯 0~9)
        self.backups = [{} for _ in range(10)]
        self.restore_buttons = []

        # 백업 파일 로드
        self.load_backups()

        # UI 구성
        self.setup_ui()

    def setup_ui(self):
        # Default 슬롯 (슬롯 0)
        default_frame = ctk.CTkFrame(self)
        default_frame.pack(pady=10)

        default_button = ctk.CTkButton(default_frame, text="Default", command=lambda: self.restore_registry(0))
        default_button.pack(side="left", padx=10)

        default_restore_button = ctk.CTkButton(default_frame, text="Restore", command=lambda: self.restore_registry(0))
        default_restore_button.pack(side="left", padx=10)
        self.restore_buttons.append(default_restore_button)

        default_detail_button = ctk.CTkButton(default_frame, text="Detail", command=lambda: self.show_details(0))
        default_detail_button.pack(side="left", padx=10)

        # 슬롯 1~9 생성
        for i in range(1, 10):
            slot_frame = ctk.CTkFrame(self)
            slot_frame.pack(pady=10)

            slot_button = ctk.CTkButton(slot_frame, text=f"Slot {i + 1}", command=lambda slot=i: self.backup_registry(slot))
            slot_button.pack(side="left", padx=10)

            restore_button = ctk.CTkButton(slot_frame, text="Restore", command=lambda slot=i: self.restore_registry(slot))
            restore_button.pack(side="left", padx=10)

            detail_button = ctk.CTkButton(slot_frame, text="Detail", command=lambda slot=i: self.show_details(slot))
            detail_button.pack(side="left", padx=10)

            self.restore_buttons.append(restore_button)

        # 버튼 상태 업데이트
        self.update_buttons()

    def load_backups(self):
        """백업 파일을 로드하고 데이터를 메모리에 저장"""
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
        """슬롯에 레지스트리 데이터를 백업"""
        print(f"Backing up registry for slot {slot}")

        # CurtainsView, SuperCurtainsView, RightClickView 클래스의 메서드를 통해 레지스트리 값을 가져옴
        curtains_values = self.curtains_view.get_current_curtains_values()
        supercurtains_values = self.supercurtains_view.get_current_curtains_values()
        rightclick_values = self.rightclick_view.get_current_right_click_values()

        print("Curtains values:", curtains_values)
        print("Super Curtains values:", supercurtains_values)
        print("Right-click values:", rightclick_values)

        # 슬롯에 백업 데이터를 저장
        self.backups[slot] = {
            'Curtains': curtains_values,
            'Super Curtains': supercurtains_values,
            'Right-click Zone': rightclick_values
        }

        # 백업 파일 저장
        save_backups(self.backups)
        messagebox.showinfo("Backup", f"Registry values backed up in slot {slot + 1}.")
        self.update_buttons()

    def restore_registry(self, slot):
        """슬롯에서 레지스트리 데이터를 복원"""
        backup_data = self.backups[slot]
        if not backup_data:
            messagebox.showinfo("Restore", f"No backup available in slot {slot + 1}.")
            return

        # CurtainsView, SuperCurtainsView, RightClickView 클래스의 메서드를 통해 레지스트리 값을 설정
        self.curtains_view.set_curtains_values(backup_data['Curtains'])
        self.supercurtains_view.set_curtains_values(backup_data['Super Curtains'])
        self.rightclick_view.set_right_click_values(backup_data['Right-click Zone'])

        messagebox.showinfo("Restore", f"Registry values restored from slot {slot + 1}.")

    def show_details(self, slot):
        """슬롯에 저장된 백업 데이터의 세부 정보를 표시"""
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
        """백업 슬롯 상태에 따라 Restore 버튼을 업데이트"""
        for i, btn in enumerate(self.restore_buttons):
            if self.backups[i]:
                btn.configure(state=ctk.NORMAL)
            else:
                btn.configure(state=ctk.DISABLED)

    def show(self):
        """BackupView가 표시될 때 호출되는 함수"""
        self.load_backups()  # 최신 백업 파일을 불러옴
        self.update_buttons()  # 버튼 상태를 업데이트
