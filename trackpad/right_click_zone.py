import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from backup_manager import create_backup_window

# 레지스트리 경로 및 키
registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
right_click_keys = ['RightClickZoneWidth', 'RightClickZoneHeight']

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
MAX_WIDTH_CM = 7.5  # 최대 width는 7.5cm
MAX_HEIGHT_CM = 5  # 최대 height는 5cm

# 현재 Right-Click Zone 레지스트리 값을 읽는 함수
def get_current_right_click_values():
    right_click_values = {}
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
        for key in right_click_keys:
            try:
                value, reg_type = winreg.QueryValueEx(reg_key, key)
                right_click_values[key] = value
            except FileNotFoundError:
                right_click_values[key] = 0  # 기본값이 없는 경우 0으로 처리
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error reading registry values: {e}")
    return right_click_values

# 레지스트리 값을 설정하는 함수 (값이 없으면 생성)
def set_right_clicks_values(right_click_values):
    try:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)  # 키 생성 또는 열기
        for key, value in right_click_values.items():
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error setting registry values: {e}")

# 저장 전, 유저에게 백업을 할 것인지 물어보는 함수
def prompt_for_save():
    response = messagebox.askyesnocancel("Save Registry", "Would you like to save the current registry before saving any edits?")
    return response

# 이미지를 업데이트하는 함수
def update_image():
    ax.clear()

    # 원본 이미지를 그립니다
    ax.imshow(img)

    # 슬라이더로 입력받은 값을 사용해 Right-Click Zone을 그립니다
    right_click_width = float(entry_width.get())
    right_click_height = float(entry_height.get())

    # 픽셀 단위로 변환 (cm -> px)
    right_click_width_px = right_click_width * CM_TO_PX_WIDTH
    right_click_height_px = right_click_height * CM_TO_PX_HEIGHT

    # 트랙패드의 노란색 기본 영역 그리기 (기본 영역)
    rect_non_click = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH_PX, TRACKPAD_HEIGHT_PX, 
                                   linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
    ax.add_patch(rect_non_click)

    # Right-Click Zone을 초록색으로 확장 (우측 하단에서 좌상단으로 확장)
    click_zone = plt.Rectangle((TRACKPAD_X + TRACKPAD_WIDTH_PX - right_click_width_px, 
                                TRACKPAD_Y + TRACKPAD_HEIGHT_PX - right_click_height_px), 
                                right_click_width_px, right_click_height_px,
                               linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    ax.add_patch(click_zone)

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

# 슬라이더에서 값이 변하면 입력 필드(Entry)를 업데이트하고 이미지도 즉시 업데이트
def update_entry_from_slider(slider, entry):
    value = slider.get()
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.2f}")  # 슬라이더 값을 0.00 형식으로 입력 필드에 반영
    update_image()  # 이미지 즉시 업데이트

# 포커스를 벗어나거나 Enter 키를 누르면 슬라이더 값을 업데이트하고 이미지도 즉시 업데이트
def on_entry_complete(entry, slider, max_value):
    update_slider_from_entry(entry, slider, max_value)
    format_entry(entry)  # 0.00 형식으로 포맷
    update_image()  # 이미지 즉시 업데이트

# 입력 필드의 값을 0.00 형식으로 포맷하는 함수
def format_entry(entry):
    try:
        value = float(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:.2f}")  # 0.00 형식으로 포맷
    except ValueError:
        entry.delete(0, tk.END)
        entry.insert(0, "0.00")  # 기본값으로 리셋

# Right-Click Zone 설정 GUI 창을 생성하는 함수
def create_right_click_window():
    sub_window = tk.Toplevel()
    sub_window.title("Right-Click Zone Settings")

    from main import window_width, window_height, position_right, position_down

    sub_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    sub_window.resizable(False, False)
    sub_window.overrideredirect(True)

    # 창 크기에 비례한 비율 값 계산
    padding_x = int(window_width * 0.03)
    padding_y = int(window_height * 0.01)
    label_font_size = int(window_height * 0.02)
    slider_length = int(window_width * 0.6)

    # 이미지 표시할 matplotlib 설정
    global ax, canvas, img
    fig, ax = plt.subplots(figsize=(window_width/180, window_height/250))
    img = plt.imread("trackpad/gb4p16_trackpad.jpg")  # 사용자 이미지 파일 로드
    ax.imshow(img, aspect='auto')
    ax.axis('off')  # 이미지 축 제거
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0, wspace=0)
    ax.set_position([0, 0, 1, 1])  # 이미지를 창에 꽉 채우기
    canvas = FigureCanvasTkAgg(fig, master=sub_window)
    canvas.get_tk_widget().pack(padx=padding_x, pady=padding_y)

    global entry_width, entry_height

    # Width 슬라이더 및 입력 필드
    label_width = tk.Label(sub_window, text="Right-Click Zone Width (cm)", font=("Arial", label_font_size))
    label_width.pack(pady=padding_y)
    slider_width = ttk.Scale(sub_window, from_=0, to=MAX_WIDTH_CM, orient='horizontal', length=slider_length, 
                             command=lambda x: update_entry_from_slider(slider_width, entry_width))  # 슬라이더 값 변경 시 즉시 반영
    slider_width.pack(pady=padding_y)
    entry_width = tk.Entry(sub_window, justify='center')
    entry_width.insert(0, "0.00")
    entry_width.pack(pady=padding_y)
    entry_width.bind("<FocusOut>", lambda event: on_entry_complete(entry_width, slider_width, MAX_WIDTH_CM))
    entry_width.bind("<Return>", lambda event: on_entry_complete(entry_width, slider_width, MAX_WIDTH_CM))

    # Height 슬라이더 및 입력 필드
    label_height = tk.Label(sub_window, text="Right-Click Zone Height (cm)", font=("Arial", label_font_size))
    label_height.pack(pady=padding_y)
    slider_height = ttk.Scale(sub_window, from_=0, to=MAX_HEIGHT_CM, orient='horizontal', length=slider_length,
                              command=lambda x: update_entry_from_slider(slider_height, entry_height))  # 슬라이더 값 변경 시 즉시 반영
    slider_height.pack(pady=padding_y)
    entry_height = tk.Entry(sub_window, justify='center')
    entry_height.insert(0, "0.00")
    entry_height.pack(pady=padding_y)
    entry_height.bind("<FocusOut>", lambda event: on_entry_complete(entry_height, slider_height, MAX_HEIGHT_CM))
    entry_height.bind("<Return>", lambda event: on_entry_complete(entry_height, slider_height, MAX_HEIGHT_CM))

    # 초기 슬라이더 값을 현재 레지스트리 값으로 설정
    right_click_values = get_current_right_click_values()
    slider_width.set(right_click_values.get('RightClickZoneWidth', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_height.set(right_click_values.get('RightClickZoneHeight', 0) / 1000)  # mm에서 cm로 변환하여 설정

    # Save와 Back 버튼을 같은 행에 배치
    frame_buttons = tk.Frame(sub_window)
    frame_buttons.pack(pady=padding_y)

    btn_save = tk.Button(frame_buttons, text="Save", command=lambda: save_right_click_values_with_prompt())
    btn_save.grid(row=0, column=0, padx=padding_x)

    btn_back = tk.Button(frame_buttons, text="Back", command=sub_window.destroy)
    btn_back.grid(row=0, column=1, padx=padding_x)

# 저장 시, 유저에게 백업을 할지 묻는 함수
def save_right_click_values_with_prompt():
    response = prompt_for_save()

    # 지연 import 방식으로 순환 참조 방지
    from trackpad.super_curtains import get_current_super_curtains_values, set_super_curtains_values
    from trackpad.curtains import get_current_curtains_values, set_curtains_values

    if response is None:
        # "Cancel editing"
        print("Editing canceled.")
    elif response:
        # "Edit after saving"
        create_backup_window(set_curtains_values, set_super_curtains_values, set_right_clicks_values, get_current_curtains_values, get_current_super_curtains_values, get_current_right_click_values)
        save_right_click_values()
    else:
        # "Edit without saving"
        save_right_click_values()

# Right-Click Zone 레지스트리 값을 저장하는 함수
def save_right_click_values():
    right_click_values = {
        'RightClickZoneWidth': int(float(entry_width.get()) * 1000),  # cm -> mm 변환 후 저장
        'RightClickZoneHeight': int(float(entry_height.get()) * 1000),
    }
    set_right_clicks_values(right_click_values)
    print("Right-click zone values saved:", right_click_values)
