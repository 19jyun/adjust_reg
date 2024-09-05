import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
from trackpad.curtains import get_current_curtains_values, set_curtains_values, create_curtains_window
from trackpad.super_curtains import get_current_super_curtains_values, set_super_curtains_values, create_super_curtains_window
from trackpad.right_click_zone import get_current_right_click_values, set_right_click_values, create_right_click_window
from backup_manager import create_backup_window, initialize_reset_slot

root = None  # 전역 변수를 제대로 처리하기 위해 root를 미리 선언

# 관리자 권한 확인 함수
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 관리자 권한을 요청하는 함수
def request_admin():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()  # 권한 요청을 거부하면 프로그램 종료
        except Exception as e:
            print(f"Admin rights required: {e}")
            sys.exit()

# 프로그램이 처음 실행되는지 확인하는 함수
def is_first_run():
    return not os.path.exists("first_run_flag.txt")

# 프로그램이 처음 실행되었음을 기록하는 함수
def mark_first_run():
    with open("first_run_flag.txt", "w") as f:
        f.write("This file indicates that the program has been run before.")

# 창 닫기 이벤트 처리 함수
def on_closing():
    global root
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()  # 메인 이벤트 루프 종료
        root.destroy()  # 모든 창 닫기
        sys.exit(0)  # 프로그램 완전히 종료

# 메인 창 설정
def main_window():
    global root  # 전역 변수로 root를 설정
    root = tk.Tk()
    root.title("Trackpad Registry Manager")

    # 창 닫기 이벤트 연결
    root.protocol("WM_DELETE_WINDOW", on_closing)

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
    btn_backup_manager = tk.Button(root, text="Open Backup Manager", command=lambda: create_backup_window(set_curtains_values, set_super_curtains_values, set_right_click_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values))
    btn_backup_manager.pack(pady=20)

    # 프로그램이 처음 실행될 때만 초기 레지스트리 값을 백업 (Slot 0)
    if is_first_run():
        initialize_reset_slot(get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values)
        mark_first_run()

    root.mainloop()

if __name__ == "__main__":
    request_admin()
    main_window()
