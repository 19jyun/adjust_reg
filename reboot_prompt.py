import ctypes
import tkinter as tk
from tkinter import messagebox
import sys
import os

# 시스템을 재부팅하는 함수
def reboot_system():
    try:
        # 관리자 권한으로 실행 중인지 확인
        if ctypes.windll.shell32.IsUserAnAdmin():
            # 시스템 재부팅 명령
            os.system("shutdown /r /t 0")
        else:
            messagebox.showerror("Permission Denied", "Administrator privileges are required to reboot the system.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to reboot the system: {e}")

# 레지스트리 수정 후 재부팅을 물어보는 함수
def prompt_reboot():
    root = tk.Tk()
    root.withdraw()  # 숨김 창 생성

    # 메시지박스 띄우기
    response = messagebox.askyesno("Reboot Required", "Registry has been edited. The system must be rebooted. Would you like to reboot now?")
    
    if response:
        reboot_system()
    else:
        messagebox.showinfo("Reboot Later", "The system changes will take effect after the next reboot.")
    
    root.destroy()
