import tkinter as tk
from new_ui_style import NewUIStyle
from curtains_view import CurtainsView
from supercurtains_view import SuperCurtainsView
from rightclick_view import RightClickView
from settings_view import SettingsView
from backup_view import BackupView
import shutil
import os
import json
import psutil
import subprocess
import threading
import ctypes
import sys
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image

def is_admin():
    """현재 스크립트가 관리자 권한으로 실행되었는지 확인합니다."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(argv=None, debug=False):
    """스크립트를 관리자 권한으로 재실행합니다."""
    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller로 패키지된 실행 파일을 처리합니다.
        arguments = map(str, argv[1:])
    else:
        arguments = map(str, argv)
    argument_line = u' '.join(arguments)
    executable = sys.executable
    if debug:
        print('Command line:', executable, argument_line)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, argument_line, None, 1) #배포시 마지막 0으로 바꾸기 (터미널 안나오게)
    sys.exit(0)
    
def check_first_execution():
    """프로그램이 처음 실행되었는지 확인"""
    settings_file = "settings.json"
    backup_file = "backups.json"
    original_file = "original_registry.json"

    if not os.path.exists(settings_file):
        with open(settings_file, "w") as f:
            json.dump({}, f)
            
    if not os.path.exists(backup_file):
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

def is_already_running():
    """Check if the program is already running to prevent multiple instances."""
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if current_process.pid != process.pid and 'new_main.py' in process.cmdline():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False
       
class MainApplication(tk.Tk):
    def __init__(self):
        
        if not is_admin():
            run_as_admin()  # 관리자 권한으로 재실행 요청
        
        tk.Tk.__init__(self)
        self.title("Trackpad Registry Manager")
        self.scale_factor = NewUIStyle.get_scaling_factor()
        self.ui_style = NewUIStyle(self.scale_factor)
        self.geometry(self.ui_style.get_window_geometry())
        self.overrideredirect(True)
        self.frames = {}

        # Curtains, SuperCurtains, RightClick 인스턴스 생성
        self.curtains_view = CurtainsView(self, self)
        self.super_curtains_view = SuperCurtainsView(self, self)
        self.right_click_view = RightClickView(self, self)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.create_frames(container)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 트레이 아이콘 설정
        self.start_tray_icon_manager()

    def create_frames(self, container):
        for F in (MainMenu, CurtainsView, SuperCurtainsView, RightClickView, BackupView, SettingsView):
            page_name = F.__name__
            frame = self.ui_style.create_scrollable_frame(container)
            if F == BackupView:
                page_frame = F(parent=frame.scrollable_frame, controller=self, 
                               set_curtains_values=self.curtains_view.set_curtains_values,
                               set_super_curtains_values=self.super_curtains_view.set_super_curtains_values,
                               set_right_click_values=self.right_click_view.set_right_click_values,
                               get_current_curtains_values=self.curtains_view.get_current_curtains_values,
                               get_current_super_curtains_values=self.super_curtains_view.get_current_super_curtains_values,
                               get_current_right_click_values=self.right_click_view.get_current_right_click_values)
            else:
                page_frame = F(parent=frame.scrollable_frame, controller=self)
            self.frames[page_name] = frame
            page_frame.pack(fill="both", expand=True)
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        # minimize_to_tray 값이 True이면 창을 닫을 때 트레이로 최소화
        settings = self.load_settings()
        if settings.get('minimize_to_tray', False):
            self.withdraw()  # 창 숨김
        else:
            self.quit_application(None, None)

    def start_tray_icon_manager(self):
        # tray_icon_manager.py 실행
        if not self.is_tray_icon_manager_running():
            self.tray_icon_process = subprocess.Popen(['python', 'tray_icon_manager.py', 'new_main.py'])

    def is_tray_icon_manager_running(self):
        """TrayIcon 관리 스크립트가 실행 중인지 확인"""
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'tray_icon_manager.py' in process.cmdline():
                    return True
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
        return False

    def quit_application(self, icon, item):
        """프로그램 종료"""
        self.destroy()
        
        # 트레이 아이콘 관리자 서브프로세스 종료
        if hasattr(self, 'tray_icon_process'):
            if self.tray_icon_process.poll() is None:  # 서브프로세스가 아직 실행 중인지 확인
                self.tray_icon_process.terminate()
                self.tray_icon_process.wait()
        
        os._exit(0)

    def load_settings(self):
        """settings.json 파일에서 설정을 로드."""
        with open("settings.json", "r") as f:
            return json.load(f)

    # 필요한 메서드들을 정의합니다.
    def set_curtains_values(self, values):
        self.curtains_view.set_curtains_values(values)

    def set_super_curtains_values(self, values):
        self.super_curtains_view.set_super_curtains_values(values)

    def set_right_click_values(self, values):
        self.right_click_view.set_right_click_values(values)

    def get_current_curtains_values(self):
        return self.curtains_view.get_current_curtains_values()

    def get_current_super_curtains_values(self):
        return self.super_curtains_view.get_current_super_curtains_values()

    def get_current_right_click_values(self):
        return self.right_click_view.get_current_right_click_values()
            

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ui_style = controller.ui_style

        btn_curtains = tk.Button(self, text="Set Curtains", command=lambda: controller.show_frame("CurtainsView"))
        self.ui_style.apply_button_style(btn_curtains)
        btn_curtains.pack(pady=10)

        btn_super_curtains = tk.Button(self, text="Set Super Curtains", command=lambda: controller.show_frame("SuperCurtainsView"))
        self.ui_style.apply_button_style(btn_super_curtains)
        btn_super_curtains.pack(pady=10)

        btn_right_click_zone = tk.Button(self, text="Set Right-click Zone", command=lambda: controller.show_frame("RightClickView"))
        self.ui_style.apply_button_style(btn_right_click_zone)
        btn_right_click_zone.pack(pady=10)

        btn_backup_manager = tk.Button(self, text="Backup Manager", command=lambda: controller.show_frame("BackupView"))
        self.ui_style.apply_button_style(btn_backup_manager)
        btn_backup_manager.pack(pady=10)

        btn_settings = tk.Button(self, text="Settings", command=lambda: controller.show_frame("SettingsView"))
        self.ui_style.apply_button_style(btn_settings)
        btn_settings.pack(pady=10)

        btn_quit = tk.Button(self, text="Quit", command=lambda: controller.on_closing())
        self.ui_style.apply_button_style(btn_quit)
        btn_quit.pack(pady=10)

if __name__ == "__main__":
    
    # Check if the program is already running
    if is_already_running():
        print("An instance of this program is already running.")
        sys.exit(0)
    
    check_first_execution()
    app = MainApplication()
    app.mainloop()
