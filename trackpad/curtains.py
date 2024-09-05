import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from backup_manager import create_backup_window
from trackpad.super_curtains import get_current_super_curtains_values, set_super_curtains_values, create_super_curtains_window
from trackpad.right_click_zone import get_current_right_click_values, set_right_click_values, create_right_click_window


# 레지스트리 경로 및 키
registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
curtain_keys = ['CurtainTop', 'CurtainLeft', 'CurtainRight', 'CurtainBottom']

# 트랙패드 크기 (실제 크기)
TRACKPAD_WIDTH_CM = 15  # 트랙패드 실제 너비 15cm
TRACKPAD_HEIGHT_CM = 10.7  # 트랙패드 실제 높이 10.7cm

# 픽셀 단위에서 트랙패드 위치 및 크기 설정
TRACKPAD_X = 145
TRACKPAD_Y = 245
TRACKPAD_WIDTH_PX = 320  # 트랙패드 이미지에서 너비
TRACKPAD_HEIGHT_PX = 235  # 트랙패드 이미지에서 높이

# 변환 비율 (픽셀 -> cm 변환)
CM_TO_PX_WIDTH = TRACKPAD_WIDTH_PX / TRACKPAD_WIDTH_CM
CM_TO_PX_HEIGHT = TRACKPAD_HEIGHT_PX / TRACKPAD_HEIGHT_CM

# 최대 확장 범위 설정 (cm 단위)
MAX_CURTAIN_LEFT_RIGHT_CM = 7.5  # 75mm = 7.5cm
MAX_CURTAIN_TOP_CM = 5  # 50mm = 5cm

# 현재 커튼 레지스트리 값을 읽는 함수
def get_current_curtains_values():
    curtain_values = {}
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
        for key in curtain_keys:
            try:
                value, reg_type = winreg.QueryValueEx(reg_key, key)
                curtain_values[key] = value
            except FileNotFoundError:
                curtain_values[key] = 0  # 기본값이 없는 경우 0으로 처리
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error reading registry values: {e}")
    return curtain_values

# 레지스트리 값을 설정하는 함수 (값이 없으면 생성)
def set_curtains_values(curtain_values):
    try:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)  # 키 생성 또는 열기
        for key, value in curtain_values.items():
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error setting registry values: {e}")

# 저장 전, 유저에게 백업을 할 것인지 물어보는 함수
def prompt_for_save():
    response = messagebox.askyesnocancel("Save Registry", "Would you like to save the current registry before saving any edits?")
    return response

# 레지스트리 값을 백업하는 함수 (main.py에서 백업 시스템 사용)
def save_registry_before_edit():
    # main.py에서 백업 시스템을 불러오는 코드
    # 예: backup_registry_to_slot(slot_number)
    print("Registry backup started.")

# 이미지를 업데이트하는 함수
def update_image():
    ax.clear()

    # 원본 이미지를 그려줍니다
    ax.imshow(img)

    # 커튼 구역을 설정 (트랙패드 영역에서만)
    curtain_top = float(entry_top.get())
    curtain_left = float(entry_left.get())
    curtain_right = float(entry_right.get())

    # 픽셀 단위로 변환 (cm -> px)
    curtain_top_px = curtain_top * CM_TO_PX_HEIGHT
    curtain_left_px = curtain_left * CM_TO_PX_WIDTH
    curtain_right_px = curtain_right * CM_TO_PX_WIDTH

    # 트랙패드의 노란색 non-curtain 영역 그리기 (노란색으로 기본 배경)
    rect_non_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH_PX, TRACKPAD_HEIGHT_PX, 
                                     linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
    ax.add_patch(rect_non_curtain)

    # 커튼 영역 그리기 (초록색으로 커튼 영역을 확장)
    left_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), curtain_left_px, TRACKPAD_HEIGHT_PX,
                                 linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    right_curtain = plt.Rectangle((TRACKPAD_X + TRACKPAD_WIDTH_PX, TRACKPAD_Y), -curtain_right_px, TRACKPAD_HEIGHT_PX,
                                  linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    top_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH_PX, curtain_top_px,
                                linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    
    ax.add_patch(left_curtain)
    ax.add_patch(right_curtain)
    ax.add_patch(top_curtain)

    # 좌표축 제거
    plt.gca().axes.xaxis.set_visible(False)
    plt.gca().axes.yaxis.set_visible(False)
    
    # 이미지 업데이트
    canvas.draw()

# 사용자 입력값 업데이트 함수 (입력 완료 후 슬라이더 값 반영)
def update_slider_from_entry(entry, slider, max_value):
    try:
        value = float(entry.get())
        if value > max_value:
            value = max_value
        slider.set(value)  # 슬라이더 값 업데이트
        update_image()
    except ValueError:
        pass  # 유효하지 않은 값일 경우 무시

# 포커스를 벗어나거나 Enter 키를 누르면 슬라이더 값을 업데이트 (완료된 입력에 대해서만)
def on_entry_complete(entry, slider, max_value):
    update_slider_from_entry(entry, slider, max_value)
    format_entry(entry)  # 0.00 형식으로 포맷

# 입력 필드의 값을 0.00 형식으로 포맷하는 함수
def format_entry(entry):
    try:
        value = float(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:.2f}")  # 0.00 형식으로 포맷
    except ValueError:
        entry.delete(0, tk.END)
        entry.insert(0, "0.00")  # 기본값으로 리셋

# 슬라이더에서 값이 변하면 입력 필드(Entry) 업데이트
def update_entry_from_slider(slider, entry):
    value = slider.get()
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")  # 슬라이더 값을 0.00 형식으로 포맷
    update_image()

# 커튼 설정 GUI 창을 생성하는 함수
def create_curtains_window():
    sub_window = tk.Toplevel()
    sub_window.title("Curtains Settings")

    # 이미지 표시할 matplotlib 설정
    global ax, canvas, img
    fig, ax = plt.subplots(figsize=(6, 4))

    img = plt.imread("trackpad/gb4p16_trackpad.jpg")  # 사용자 이미지 파일 로드
    ax.imshow(img)

    canvas = FigureCanvasTkAgg(fig, master=sub_window)
    canvas.get_tk_widget().pack()

    global entry_top, entry_left, entry_right

    # 슬라이더 설정 및 숫자 입력
    label_top = tk.Label(sub_window, text="Curtain Top (Height, cm)")
    label_top.pack(pady=5)
    slider_top = ttk.Scale(sub_window, from_=0, to=MAX_CURTAIN_TOP_CM, orient='horizontal', command=lambda x: update_entry_from_slider(slider_top, entry_top))
    slider_top.pack(pady=5)
    entry_top = tk.Entry(sub_window, justify='center')
    entry_top.insert(0, "0.00")
    entry_top.pack(pady=5)
    entry_top.bind("<FocusOut>", lambda event: on_entry_complete(entry_top, slider_top, MAX_CURTAIN_TOP_CM))  # 포커스 벗어날 때 포맷
    entry_top.bind("<Return>", lambda event: on_entry_complete(entry_top, slider_top, MAX_CURTAIN_TOP_CM))  # Enter 키 입력 시 포맷

    label_left = tk.Label(sub_window, text="Curtain Left (Width, cm)")
    label_left.pack(pady=5)
    slider_left = ttk.Scale(sub_window, from_=0, to=MAX_CURTAIN_LEFT_RIGHT_CM, orient='horizontal', command=lambda x: update_entry_from_slider(slider_left, entry_left))
    slider_left.pack(pady=5)
    entry_left = tk.Entry(sub_window, justify='center')
    entry_left.insert(0, "0.00")
    entry_left.pack(pady=5)
    entry_left.bind("<FocusOut>", lambda event: on_entry_complete(entry_left, slider_left, MAX_CURTAIN_LEFT_RIGHT_CM))
    entry_left.bind("<Return>", lambda event: on_entry_complete(entry_left, slider_left, MAX_CURTAIN_LEFT_RIGHT_CM))

    label_right = tk.Label(sub_window, text="Curtain Right (Width, cm)")
    label_right.pack(pady=5)
    slider_right = ttk.Scale(sub_window, from_=0, to=MAX_CURTAIN_LEFT_RIGHT_CM, orient='horizontal', command=lambda x: update_entry_from_slider(slider_right, entry_right))
    slider_right.pack(pady=5)
    entry_right = tk.Entry(sub_window, justify='center')
    entry_right.insert(0, "0.00")
    entry_right.pack(pady=5)
    entry_right.bind("<FocusOut>", lambda event: on_entry_complete(entry_right, slider_right, MAX_CURTAIN_LEFT_RIGHT_CM))
    entry_right.bind("<Return>", lambda event: on_entry_complete(entry_right, slider_right, MAX_CURTAIN_LEFT_RIGHT_CM))

    # 초기 슬라이더 값을 현재 레지스트리 값으로 설정
    curtain_values = get_current_curtains_values()
    slider_top.set(curtain_values.get('CurtainTop', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_left.set(curtain_values.get('CurtainLeft', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_right.set(curtain_values.get('CurtainRight', 0) / 1000)  # mm에서 cm로 변환하여 설정

    # 저장 버튼
    btn_save = tk.Button(sub_window, text="Save Settings", command=lambda: save_curtain_values_with_prompt())
    btn_save.pack(pady=10)

# 저장 시, 유저에게 백업을 할지 묻는 함수
def save_curtain_values_with_prompt():
    response = prompt_for_save()

    if response is None:
        # "Cancel editing"
        print("Editing canceled.")
    elif response:
        # "Edit after saving"
        create_backup_window(set_curtains_values, set_super_curtains_values, set_right_click_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values)
        save_curtain_values()
    else:
        # "Edit without saving"
        save_curtain_values()

# 커튼 레지스트리 값을 저장하는 함수
def save_curtain_values():
    curtain_values = {
        'CurtainTop': int(float(entry_top.get()) * 1000),  # cm -> mm 변환 후 저장
        'CurtainLeft': int(float(entry_left.get()) * 1000),
        'CurtainRight': int(float(entry_right.get()) * 1000),
    }
    set_curtains_values(curtain_values)
    print("Curtain values saved:", curtain_values)
