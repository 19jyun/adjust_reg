import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess
import sys
from new_ui_style import NewUIStyle
from backup_manager import BACKUP_FILE_PATH, save_backups

# 관리자 권한 자동 부여 옵션을 저장하는 파일 경로
settings_file = "settings.json"

def load_settings():
    """settings.json 파일에서 설정을 불러옵니다."""
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    else:
        return {"require_admin": False}

def save_settings(settings):
    """설정을 settings.json 파일에 저장합니다."""
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)

def create_task_scheduler():
    """작업 스케줄러에 프로그램을 관리자 권한으로 실행되도록 등록"""
    task_name = "MyApp_AutoRun_Admin"
    exe_path = os.path.abspath("main.py")  # 현재 실행 중인 프로그램 경로

    # 작업 스케줄러 명령어 생성
    cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /rl highest /f'

    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Task '{task_name}' created successfully for admin execution.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create task: {e}")

def delete_task_scheduler():
    """작업 스케줄러에서 프로그램 실행 작업을 제거"""
    task_name = "MyApp_AutoRun_Admin"

    # 작업 스케줄러에서 작업 제거 명령어
    cmd = f'schtasks /delete /tn "{task_name}" /f'

    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Task '{task_name}' deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete task: {e}")

def toggle_admin_rights():
    """체크박스 상태에 따라 require_admin을 설정하고 작업 스케줄러에 등록 또는 제거"""
    
    settings = load_settings()
    
    if admin_rights_var.get():
        # 체크박스가 해제된 경우 require_admin을 false로 설정하고 작업 스케줄러에 등록
        settings['require_admin'] = False
        create_task_scheduler()  # 관리자 권한 실행을 위해 작업 스케줄러에 등록
    else:
        # 체크박스가 체크된 경우 require_admin을 true로 설정하고 작업 스케줄러에서 제거
        settings['require_admin'] = True
        delete_task_scheduler()  # 관리자 권한 실행을 해제하기 위해 작업 스케줄러에서 제거

    save_settings(settings)
    print(f"Settings updated: {settings}")  # 디버깅용 출력

def reset_backup_file():
    """백업 파일을 기본 상태로 초기화합니다."""
    # 모든 백업 데이터를 empty로 초기화
    backups = [{} for _ in range(11)]
    save_backups(backups)  # backup_manager.py에서 제공하는 save_backups 함수 사용
    messagebox.showinfo("Reset", "Backup file has been reset to default.")

def create_settings_window():
    """Settings 창을 엽니다."""
    settings = load_settings()

    # Tkinter 창 생성
    root = tk.Toplevel()
    root.title("Settings")

    # new_ui_style 적용
    scale_factor = NewUIStyle.get_scaling_factor()
    ui_style = NewUIStyle(scale_factor)
    
    root.geometry(ui_style.get_window_geometry())
    root.resizable(False, False)
    root.overrideredirect(True)

    padding_x, padding_y = ui_style.get_padding()

    # 스크롤 가능한 프레임 생성
    scrollable_frame = ui_style.create_scrollable_frame(root)

    global admin_rights_var

    admin_rights_var = tk.BooleanVar(value=not settings.get('require_admin', False))
    admin_rights_checkbox = tk.Checkbutton(scrollable_frame, text="Automatically give admin rights", variable=admin_rights_var, command=toggle_admin_rights)
    ui_style.apply_checkbox_style(admin_rights_checkbox)
    admin_rights_checkbox.pack(pady=padding_y)

    # 백업 파일 초기화 버튼
    def on_reset_backup():
        if messagebox.askyesno("Reset Backup", "Are you sure you want to reset the backup file to default?"):
            reset_backup_file()

    reset_backup_button = tk.Button(scrollable_frame, text="Reset backup file to default", command=on_reset_backup)
    ui_style.apply_button_style(reset_backup_button)
    reset_backup_button.pack(pady=padding_y)

    # Back 버튼
    btn_back = tk.Button(scrollable_frame, text="Back", command=root.destroy)
    ui_style.apply_button_style(btn_back)
    btn_back.pack(pady=padding_y)

    root.mainloop()
