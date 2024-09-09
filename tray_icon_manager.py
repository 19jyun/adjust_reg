import os
import sys
import psutil
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image

# 트레이 아이콘 이미지 생성
def create_image():
    image = Image.open('registry.png')  # 트레이에 사용할 아이콘 파일 경로
    return image

def on_clicked(icon, item):
    """트레이 아이콘을 클릭하면 메인 프로그램 실행"""
    # 이미 메인 프로그램이 실행 중인지 확인하고, 실행 중이 아니면 실행
    if not is_program_running(sys.argv[1]):
        os.system(f'python {sys.argv[1]}')  # 메인 프로그램 실행

def quit_application(icon, item):
    """트레이 아이콘을 클릭하면 트레이 아이콘 종료"""
    icon.stop()

def is_program_running(program_name):
    """프로세스 이름으로 프로그램이 실행 중인지 확인"""
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if program_name in process.info['cmdline']:
            return True
    return False

def is_already_running():
    # 현재 프로세스와 동일한 이름을 가진 다른 프로세스가 실행 중인지 확인
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = process.info.get('cmdline')
            if cmdline and process.info['pid'] != current_process.pid and 'tray_icon_manager.py' in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tray_icon_manager.py <path_to_main_program>")
        sys.exit(1)

    if is_already_running():
        print("Tray icon manager is already running.")
        sys.exit(0)

    image = create_image()
    menu = TrayMenu(
        TrayMenuItem('Restore', on_clicked),
        TrayMenuItem('Quit', quit_application)
    )
    icon = TrayIcon("Trackpad Registry Manager", image, "Trackpad Registry Manager", menu)
    icon.run()