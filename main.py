import tkinter as tk
from tkinter import messagebox
import os
from trackpad.curtains import get_current_curtains_values, set_curtains_values, create_curtains_window
from trackpad.super_curtains import get_current_super_curtains_values, set_super_curtains_values, create_super_curtains_window
from trackpad.right_click_zone import get_current_right_click_values, set_right_click_values, create_right_click_window

# 10개의 백업 슬롯을 위한 리스트
backups = [{} for _ in range(10)]
restore_buttons = []  # Restore 버튼들을 저장할 리스트

# 초기 레지스트리 값을 'Reset' 슬롯에 저장하는 함수
def initialize_reset_slot():
    backups[0] = {
        'Curtains': get_current_curtains_values(),
        'Super Curtains': get_current_super_curtains_values(),
        'Right-click Zone': get_current_right_click_values(),
    }

# 레지스트리 값을 백업하는 함수
def backup_registry(slot):
    curtains_values = get_current_curtains_values()
    super_curtains_values = get_current_super_curtains_values()
    right_click_values = get_current_right_click_values()

    backups[slot] = {
        'Curtains': curtains_values,
        'Super Curtains': super_curtains_values,
        'Right-click Zone': right_click_values,
    }
    messagebox.showinfo("Backup", f"Registry values backed up in slot {slot + 1}.")
    update_buttons()  # 버튼 상태 업데이트

# 레지스트리 값을 복원하는 함수
def restore_registry(slot):
    backup_data = backups[slot]
    if not backup_data:
        messagebox.showinfo("Restore", f"No backup available in slot {slot + 1}.")
        return
    
    # 레지스트리 복원
    set_curtains_values(backup_data['Curtains'])
    set_super_curtains_values(backup_data['Super Curtains'])
    set_right_click_values(backup_data['Right-click Zone'])

    messagebox.showinfo("Restore", f"Registry values restored from slot {slot + 1}.")

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

# 백업 관리 창에서 버튼 상태를 업데이트하는 함수
def update_buttons():
    for i, btn in enumerate(restore_buttons):
        if backups[i]:
            btn.config(text="Restore", state=tk.NORMAL)
        else:
            btn.config(text="Empty", state=tk.DISABLED)

# 백업 관리 창 생성 함수
def create_backup_window():
    backup_window = tk.Toplevel()
    backup_window.title("Registry Backup Manager")

    global restore_buttons
    restore_buttons = []  # 버튼 리스트 초기화

    # Slot 0은 "Reset"으로 표시
    reset_button = tk.Button(backup_window, text="Reset", 
                             command=lambda: restore_registry(0))
    reset_button.grid(row=0, column=0, padx=10, pady=5)

    reset_detail_button = tk.Button(backup_window, text="Detail", 
                                    command=lambda: show_details(0))
    reset_detail_button.grid(row=0, column=1, padx=10, pady=5)

    restore_buttons.append(reset_button)  # Slot 0의 Restore 버튼 추가

    # Slot 1~9 버튼 추가 (Backup, Restore, Detail)
    for i in range(1, 10):
        slot_button = tk.Button(backup_window, text=f"Slot {i + 1}", 
                                command=lambda slot=i: backup_registry(slot))
        slot_button.grid(row=i, column=0, padx=10, pady=5)

        restore_button = tk.Button(backup_window, text="Restore", 
                                   command=lambda slot=i: restore_registry(slot))
        restore_button.grid(row=i, column=1, padx=10, pady=5)

        detail_button = tk.Button(backup_window, text="Detail", 
                                  command=lambda slot=i: show_details(slot))
        detail_button.grid(row=i, column=2, padx=10, pady=5)

        restore_buttons.append(restore_button)  # Restore 버튼을 리스트에 추가

    update_buttons()  # 버튼 상태 초기화

# 프로그램이 처음 실행되는지 확인하는 함수
def is_first_run():
    return not os.path.exists("first_run_flag.txt")

# 프로그램이 처음 실행되었음을 기록하는 함수
def mark_first_run():
    with open("first_run_flag.txt", "w") as f:
        f.write("This file indicates that the program has been run before.")


# 메인 창 설정
def main_window():
    root = tk.Tk()
    root.title("Trackpad Registry Manager")

    # 'Set Curtains' 버튼
    btn_curtains = tk.Button(root, text="Set Curtains", command=create_curtains_window)
    btn_curtains.pack(pady=10)

    # 'Set Super Curtains' 버튼
    btn_super_curtains = tk.Button(root, text="Set Super Curtains", command=create_super_curtains_window)
    btn_super_curtains.pack(pady=10)

    # 'Set Right-click Zone' 버튼
    btn_right_click_zone = tk.Button(root, text="Set Right-click Zone", command=create_right_click_window)
    btn_right_click_zone.pack(pady=10)

    # 'Backup Manager' 버튼 추가
    btn_backup_manager = tk.Button(root, text="Open Backup Manager", command=create_backup_window)
    btn_backup_manager.pack(pady=20)

    # 프로그램이 시작될 때 초기 레지스트리 값을 백업 (Slot 0)
    initialize_reset_slot()

    root.mainloop()

if __name__ == "__main__":
    if is_first_run():
        initialize_reset_slot()
        mark_first_run()
    main_window()