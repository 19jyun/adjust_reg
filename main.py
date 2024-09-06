import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
from trackpad.curtains import get_current_curtains_values, set_curtains_values, create_curtains_window
from trackpad.super_curtains import get_current_super_curtains_values, set_super_curtains_values, create_super_curtains_window
from trackpad.right_click_zone import get_current_right_click_values, set_right_clicks_values, create_right_click_window
from backup_manager import create_backup_window, initialize_reset_slot
from win32api import GetMonitorInfo, MonitorFromPoint

# DPI 설정을 가져오는 함수 (배율 정보)
def get_scaling_factor():
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()  # 프로그램이 DPI를 인식하도록 설정
        hdc = user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        scaling_factor = dpi / 96.0  # 96 DPI가 100% 배율에 해당함
        return scaling_factor
    except Exception as e:
        print(f"Error getting DPI scaling: {e}")
        return 1.0  # 기본 배율 1.0

scale_factor = get_scaling_factor()
print(f"Scaling factor: {scale_factor}")

def get_taskbar_height():
    user32 = ctypes.windll.user32
    # 전체 화면 해상도
    
    global screen_width, screen_height
    
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # 작업 표시줄을 제외한 해상도
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    work_area = monitor_info['Work']

    taskbar_height = screen_height - work_area[3]
    return taskbar_height


root = None  # 전역 변수를 제대로 처리하기 위해 root를 미리 선언

# 화면의 너비와 높이 가져오기
screen_width = 0
screen_height = 0

taskbar = get_taskbar_height()

screen_height = int(screen_height*scale_factor)
screen_width = int(screen_width*scale_factor)

# 창의 크기를 화면 해상도의 비율로 설정 (예: 너비의 50%, 높이의 70%)
window_width = int(screen_width * 0.26)
window_height = int(screen_height * 0.65)

print(f"Screen width: {screen_width}, Screen height: {screen_height}, Taskbar height: {taskbar}")

# 창의 위치 계산 (우측 하단)
position_right = screen_width - window_width - 5
position_down = screen_height - window_height - taskbar - 5

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

# 창 드래그 비활성화 함수
def disable_window_drag(event):
    # 빈 함수로 이벤트를 처리하지 않음
    return "break"

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

    global window_width, window_height, position_right, position_down, screen_height, screen_width

    # 창의 크기와 위치 설정
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    
    # 창의 크기 조절 비활성화
    root.resizable(False, False)

    # 창 닫기 이벤트 연결
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.overrideredirect(True)

    # 창 이동 비활성화 (제목바 드래그 무시)
    root.bind("<Configure>", disable_window_drag)

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
    btn_backup_manager = tk.Button(root, text="Open Backup Manager", command=lambda: create_backup_window(set_curtains_values, set_super_curtains_values, set_right_clicks_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values))
    btn_backup_manager.pack(pady=20)

    # 'Quit' 버튼 추가
    btn_quit = tk.Button(root, text="Quit", command=on_closing)
    btn_quit.pack(pady=10)

    # 프로그램이 처음 실행될 때만 초기 레지스트리 값을 백업 (Slot 0)
    if is_first_run():
        initialize_reset_slot(get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values)
        mark_first_run()

    root.mainloop()

if __name__ == "__main__":
    request_admin()
    main_window()
