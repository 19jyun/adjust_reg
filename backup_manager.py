# backup_manager.py

import tkinter as tk
import os
import json
from tkinter import messagebox

# 백업 파일 경로
BACKUP_FILE_PATH = "registry_backups.json"

# 10개의 백업 슬롯을 위한 리스트
backups = [{} for _ in range(10)]
restore_buttons = []  # Restore 버튼들을 저장할 리스트

# [Detail] 버튼 클릭 시 백업 내용을 보여주는 함수
def show_details(slot):
    backup_data = backups[slot]
    if not backup_data:
        messagebox.showinfo("Details", f"No backup available in slot {slot + 1}.")
    else:
        details = "Registry Backup Details:\n\n"
        details += "Curtains:\n"
        details += "\n".join(f"{key}: {value}" for key, value in backup_data['Curtains'].items())
        details += "\n\nSuper Curtains:\n"
        details += "\n".join(f"{key}: {value}" for key, value in backup_data['Super Curtains'].items())
        details += "\n\nRight-click Zone:\n"
        details += "\n".join(f"{key}: {value}" for key, value in backup_data['Right-click Zone'].items())
        messagebox.showinfo("Details", details)


# 프로그램이 시작될 때 JSON 파일에서 백업 데이터를 로드하는 함수
def load_backups():
    if os.path.exists(BACKUP_FILE_PATH):
        with open(BACKUP_FILE_PATH, 'r') as file:
            try:
                loaded_backups = json.load(file)
                for i, backup in enumerate(loaded_backups):
                    backups[i] = backup
            except json.JSONDecodeError:
                print("Error reading backup file.")
    else:
        save_backups()  # 파일이 없으면 기본 상태로 저장

# 백업 데이터를 JSON 파일로 저장하는 함수
def save_backups():
    with open(BACKUP_FILE_PATH, 'w') as file:
        json.dump(backups, file)

# 초기 레지스트리 값을 'Reset' 슬롯에 저장하는 함수 (모든 값을 0으로 설정)
def initialize_reset_slot():
    """ 초기 레지스트리 값을 backups[0]에 저장 (모든 값을 0으로 초기화) """
    backups[0] = {
        'Curtains': {'CurtainTop': 0, 'CurtainLeft': 0, 'CurtainRight': 0},
        'Super Curtains': {'SuperCurtainTop': 0, 'SuperCurtainBottom': 0, 'SuperCurtainLeft': 0, 'SuperCurtainRight': 0},
        'Right-click Zone': {'RightClickZone': 0}
    }
    save_backups()  # 초기화 후 저장

# 레지스트리 값을 백업하는 함수
def backup_registry(slot, curtains_values, super_curtains_values, right_click_values):
    backups[slot] = {
        'Curtains': curtains_values,
        'Super Curtains': super_curtains_values,
        'Right-click Zone': right_click_values,
    }
    save_backups()  # 백업 후 저장
    messagebox.showinfo("Backup", f"Registry values backed up in slot {slot + 1}.")
    update_buttons()

# 레지스트리 값을 복원하는 함수
def restore_registry(slot, set_curtains_values, set_super_curtains_values, set_right_click_values):
    backup_data = backups[slot]
    if not backup_data:
        messagebox.showinfo("Restore", f"No backup available in slot {slot + 1}.")
        return
    
    # 레지스트리 복원
    set_curtains_values(backup_data['Curtains'])
    set_super_curtains_values(backup_data['Super Curtains'])
    set_right_click_values(backup_data['Right-click Zone'])

    messagebox.showinfo("Restore", f"Registry values restored from slot {slot + 1}.")

# 백업 관리 창에서 버튼 상태를 업데이트하는 함수
def update_buttons():
    for i, btn in enumerate(restore_buttons):
        if backups[i]:
            btn.config(text="Restore", state=tk.NORMAL)
        else:
            btn.config(text="Empty", state=tk.DISABLED)

# 백업 관리 창 생성 함수
def create_backup_window(set_curtains_values, set_super_curtains_values, set_right_click_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values):
    backup_window = tk.Toplevel()
    backup_window.title("Registry Backup Manager")

    global restore_buttons
    restore_buttons = []  # 버튼 리스트 초기화

    # Slot 0을 "default"로 표시하며 모든 값을 0으로 초기화
    default_button = tk.Button(backup_window, text="Default", 
                               command=lambda: restore_registry(0, set_curtains_values, set_super_curtains_values, set_right_click_values))
    default_button.grid(row=0, column=0, padx=10, pady=5)

    default_restore_button = tk.Button(backup_window, text="Restore", 
                                       command=lambda: restore_registry(0, set_curtains_values, set_super_curtains_values, set_right_click_values))
    default_restore_button.grid(row=0, column=1, padx=10, pady=5)

    restore_buttons.append(default_restore_button)  # Slot 0의 Restore 버튼 추가
    # Slot 1~9 버튼 추가 (Backup, Restore, Detail)
    for i in range(1, 10):
        slot_button = tk.Button(backup_window, text=f"Slot {i + 1}", 
                                command=lambda slot=i: backup_registry(slot, 
                                                                      get_current_curtains_values(), 
                                                                      get_current_super_curtains_values(), 
                                                                      get_current_right_click_values()))
        slot_button.grid(row=i, column=0, padx=10, pady=5)

        restore_button = tk.Button(backup_window, text="Restore", 
                                   command=lambda slot=i: restore_registry(slot, set_curtains_values, set_super_curtains_values, set_right_click_values))
        restore_button.grid(row=i, column=1, padx=10, pady=5)

        detail_button = tk.Button(backup_window, text="Detail", 
                                  command=lambda slot=i: show_details(slot))
        detail_button.grid(row=i, column=2, padx=10, pady=5)

        restore_buttons.append(restore_button)  # Restore 버튼을 리스트에 추가

    update_buttons()  # 버튼 상태 초기화

# 프로그램 시작 시 백업 데이터 로드
load_backups()