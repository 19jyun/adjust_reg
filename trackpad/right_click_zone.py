import tkinter as tk
from tkinter import ttk
import winreg

# 레지스트리 값을 수정하는 함수
def modify_registry_value(key, value, status_label):
    try:
        registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
        winreg.CloseKey(reg_key)
        status_label.config(text="Registry value updated successfully.")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

# 현재 레지스트리 값을 읽는 함수
def get_current_right_click_values():
    registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
    right_click_keys = ['RightClickZoneWidth', 'RightClickZoneHeight']
    right_click_values = {}
    
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        for key in right_click_keys:
            try:
                value, reg_type = winreg.QueryValueEx(reg_key, key)
                right_click_values[key] = value
            except FileNotFoundError:
                right_click_values[key] = None  # 값이 없는 경우 처리
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error reading right-click values: {e}")

    return right_click_values

# 레지스트리 값을 설정하는 함수
def set_right_click_values(right_click_values):
    registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
    
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        for key, value in right_click_values.items():
            if value is not None:
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(reg_key)
        print("Right-click Zone values set successfully.")
    except Exception as e:
        print(f"Error setting right-click values: {e}")

# 'Right-click Zone' 설정을 위한 서브 창 생성 함수
def create_right_click_window():
    sub_window = tk.Toplevel()
    sub_window.title("Right-click Zone Settings")

    # Right-click zone 관련 레지스트리 값과 기본값, 범위 설정
    right_click_settings = [
        ("RightClickZoneWidth", 1, 100, 50),
        ("RightClickZoneHeight", 1, 100, 25)
    ]

    # 슬라이더와 상태 레이블을 생성하는 반복문
    for (key, min_value, max_value, default_value) in right_click_settings:
        label = tk.Label(sub_window, text=f"{key} (Range {min_value}-{max_value}):")
        label.pack(pady=5)

        slider = ttk.Scale(sub_window, from_=min_value, to=max_value, orient='horizontal')
        slider.set(default_value)
        slider.pack(pady=5)

        status_label = tk.Label(sub_window, text="No changes made yet.")
        status_label.pack(pady=5)

        # 버튼 클릭 시 레지스트리 값 수정
        btn_apply = tk.Button(sub_window, text=f"Apply {key}", 
                              command=lambda k=key, s=slider, l=status_label: modify_registry_value(k, s.get(), l))
        btn_apply.pack(pady=5)
