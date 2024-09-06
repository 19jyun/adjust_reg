import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
from backup_manager import create_backup_window
from new_ui_style import NewUIStyle

# UI 스타일 적용
scale_factor = NewUIStyle.get_scaling_factor()
ui_style = NewUIStyle(scale_factor)

# 레지스트리 경로 및 키
registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
super_curtain_keys = ['SuperCurtainTop', 'SuperCurtainLeft', 'SuperCurtainRight', 'SuperCurtainBottom']

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
MAX_SUPER_CURTAIN_LEFT_RIGHT_CM = 7.5  # 75mm = 7.5cm
MAX_SUPER_CURTAIN_TOP_BOTTOM_CM = 5  # 50mm = 5cm

# 현재 슈퍼 커튼 레지스트리 값을 읽는 함수
def get_current_super_curtains_values():
    super_curtain_values = {}
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
        for key in super_curtain_keys:
            try:
                value, reg_type = winreg.QueryValueEx(reg_key, key)
                super_curtain_values[key] = value
            except FileNotFoundError:
                super_curtain_values[key] = 0  # 기본값이 없는 경우 0으로 처리
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error reading registry values: {e}")
    return super_curtain_values

# 레지스트리 값을 설정하는 함수 (값이 없으면 생성)
def set_super_curtains_values(super_curtain_values):
    try:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)  # 키 생성 또는 열기
        for key, value in super_curtain_values.items():
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

    # 슬라이더로 입력받은 값을 사용해 Super Curtain 영역을 그립니다
    super_curtain_top = float(entry_top.get())
    super_curtain_left = float(entry_left.get())
    super_curtain_right = float(entry_right.get())
    super_curtain_bottom = float(entry_bottom.get())

    # 픽셀 단위로 변환 (cm -> px)
    super_curtain_top_px = super_curtain_top * CM_TO_PX_HEIGHT
    super_curtain_left_px = super_curtain_left * CM_TO_PX_WIDTH
    super_curtain_right_px = super_curtain_right * CM_TO_PX_WIDTH
    super_curtain_bottom_px = super_curtain_bottom * CM_TO_PX_HEIGHT

    # 트랙패드의 노란색 기본 영역 그리기 (노란색 배경)
    rect_non_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH_PX, TRACKPAD_HEIGHT_PX, 
                                     linewidth=1, edgecolor=None, facecolor='yellow', alpha=0.5)
    ax.add_patch(rect_non_curtain)

    # 커튼 영역 그리기 (초록색 영역)
    left_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), super_curtain_left_px, TRACKPAD_HEIGHT_PX,
                                 linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    right_curtain = plt.Rectangle((TRACKPAD_X + TRACKPAD_WIDTH_PX, TRACKPAD_Y), -super_curtain_right_px, TRACKPAD_HEIGHT_PX,
                                  linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    top_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y), TRACKPAD_WIDTH_PX, super_curtain_top_px,
                                linewidth=1, edgecolor=None, facecolor='green', alpha=0.5)
    bottom_curtain = plt.Rectangle((TRACKPAD_X, TRACKPAD_Y + TRACKPAD_HEIGHT_PX - super_curtain_bottom_px), 
                                   TRACKPAD_WIDTH_PX, super_curtain_bottom_px, linewidth=1, 
                                   edgecolor=None, facecolor='green', alpha=0.5)
    
    ax.add_patch(left_curtain)
    ax.add_patch(right_curtain)
    ax.add_patch(top_curtain)
    ax.add_patch(bottom_curtain)

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

# 입력 필드의 값을 0.00 형식으로 포맷하는 함수
def format_entry(entry):
    try:
        value = float(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:.2f}")  # 0.00 형식으로 포맷
    except ValueError:
        entry.delete(0, tk.END)
        entry.insert(0, "0.00")  # 기본값으로 리셋

# Super Curtains 설정 GUI 창을 생성하는 함수
def create_super_curtains_window():
    # 스크롤 가능한 창을 생성
    scrollable_frame = ui_style.create_scrollable_window("Super Curtains Settings")

    padding_x, padding_y = ui_style.get_padding()

    # 이미지 표시할 matplotlib 설정
    global ax, canvas, img
    fig, ax = plt.subplots(figsize=((ui_style.window_width / ui_style.scale_factor) / 180, (ui_style.window_height / ui_style.scale_factor) / 250))
    img = plt.imread("trackpad/gb4p16_trackpad.jpg")  # 사용자 이미지 파일 로드
    ax.imshow(img, aspect='auto')
    ax.axis('off')  # 이미지 축 제거
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0, wspace=0)
    ax.set_position([0, 0, 1, 1])  # 이미지를 창에 꽉 채우기
    canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas.get_tk_widget().pack(padx=padding_x, pady=padding_y)

    global entry_top, entry_bottom, entry_left, entry_right

    # Top 슬라이더 및 입력 필드
    label_top = tk.Label(scrollable_frame, text="Super Curtain Top (Height, cm)")
    ui_style.apply_label_style(label_top)
    label_top.pack(pady=padding_y)
    slider_top = ttk.Scale(scrollable_frame, from_=0, to=MAX_SUPER_CURTAIN_TOP_BOTTOM_CM, orient='horizontal', length=ui_style.slider_length, 
                           command=lambda x: update_entry_from_slider(slider_top, entry_top))
    slider_top.pack(pady=padding_y)
    entry_top = tk.Entry(scrollable_frame, justify='center')
    ui_style.apply_entry_style(entry_top)
    entry_top.insert(0, "0.00")
    entry_top.pack(pady=padding_y)
    entry_top.bind("<FocusOut>", lambda event: on_entry_complete(entry_top, slider_top, MAX_SUPER_CURTAIN_TOP_BOTTOM_CM))
    entry_top.bind("<Return>", lambda event: on_entry_complete(entry_top, slider_top, MAX_SUPER_CURTAIN_TOP_BOTTOM_CM))

    # Bottom 슬라이더 및 입력 필드
    label_bottom = tk.Label(scrollable_frame, text="Super Curtain Bottom (Height, cm)")
    ui_style.apply_label_style(label_bottom)
    label_bottom.pack(pady=padding_y)
    slider_bottom = ttk.Scale(scrollable_frame, from_=0, to=MAX_SUPER_CURTAIN_TOP_BOTTOM_CM, orient='horizontal', length=ui_style.slider_length, 
                              command=lambda x: update_entry_from_slider(slider_bottom, entry_bottom))
    slider_bottom.pack(pady=padding_y)
    entry_bottom = tk.Entry(scrollable_frame, justify='center')
    ui_style.apply_entry_style(entry_bottom)
    entry_bottom.insert(0, "0.00")
    entry_bottom.pack(pady=padding_y)
    entry_bottom.bind("<FocusOut>", lambda event: on_entry_complete(entry_bottom, slider_bottom, MAX_SUPER_CURTAIN_TOP_BOTTOM_CM))
    entry_bottom.bind("<Return>", lambda event: on_entry_complete(entry_bottom, slider_bottom, MAX_SUPER_CURTAIN_TOP_BOTTOM_CM))

    # Left 슬라이더 및 입력 필드
    label_left = tk.Label(scrollable_frame, text="Super Curtain Left (Width, cm)")
    ui_style.apply_label_style(label_left)
    label_left.pack(pady=padding_y)
    slider_left = ttk.Scale(scrollable_frame, from_=0, to=MAX_SUPER_CURTAIN_LEFT_RIGHT_CM, orient='horizontal', length=ui_style.slider_length, 
                            command=lambda x: update_entry_from_slider(slider_left, entry_left))
    slider_left.pack(pady=padding_y)
    entry_left = tk.Entry(scrollable_frame, justify='center')
    ui_style.apply_entry_style(entry_left)
    entry_left.insert(0, "0.00")
    entry_left.pack(pady=padding_y)
    entry_left.bind("<FocusOut>", lambda event: on_entry_complete(entry_left, slider_left, MAX_SUPER_CURTAIN_LEFT_RIGHT_CM))
    entry_left.bind("<Return>", lambda event: on_entry_complete(entry_left, slider_left, MAX_SUPER_CURTAIN_LEFT_RIGHT_CM))

    # Right 슬라이더 및 입력 필드
    label_right = tk.Label(scrollable_frame, text="Super Curtain Right (Width, cm)")
    ui_style.apply_label_style(label_right)
    label_right.pack(pady=padding_y)
    slider_right = ttk.Scale(scrollable_frame, from_=0, to=MAX_SUPER_CURTAIN_LEFT_RIGHT_CM, orient='horizontal', length=ui_style.slider_length, 
                             command=lambda x: update_entry_from_slider(slider_right, entry_right))
    slider_right.pack(pady=padding_y)
    entry_right = tk.Entry(scrollable_frame, justify='center')
    ui_style.apply_entry_style(entry_right)
    entry_right.insert(0, "0.00")
    entry_right.pack(pady=padding_y)
    entry_right.bind("<FocusOut>", lambda event: on_entry_complete(entry_right, slider_right, MAX_SUPER_CURTAIN_LEFT_RIGHT_CM))
    entry_right.bind("<Return>", lambda event: on_entry_complete(entry_right, slider_right, MAX_SUPER_CURTAIN_LEFT_RIGHT_CM))

    # 초기 슬라이더 값을 현재 레지스트리 값으로 설정
    super_curtain_values = get_current_super_curtains_values()
    slider_top.set(super_curtain_values.get('SuperCurtainTop', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_bottom.set(super_curtain_values.get('SuperCurtainBottom', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_left.set(super_curtain_values.get('SuperCurtainLeft', 0) / 1000)  # mm에서 cm로 변환하여 설정
    slider_right.set(super_curtain_values.get('SuperCurtainRight', 0) / 1000)  # mm에서 cm로 변환하여 설정

    # Save와 Back 버튼을 같은 행에 배치
    frame_buttons = tk.Frame(scrollable_frame)
    frame_buttons.pack(pady=padding_y)

    btn_save = tk.Button(frame_buttons, text="Save", command=lambda: save_super_curtain_values_with_prompt())
    ui_style.apply_button_style(btn_save)
    btn_save.grid(row=0, column=0, padx=padding_x)

    btn_back = tk.Button(frame_buttons, text="Back", command=lambda: scrollable_frame.winfo_toplevel().destroy())
    ui_style.apply_button_style(btn_back)
    btn_back.grid(row=0, column=1, padx=padding_x)

# 저장 시, 유저에게 백업을 할지 묻는 함수
def save_super_curtain_values_with_prompt():
    response = prompt_for_save()

    if response is None:
        # "Cancel editing"
        print("Editing canceled.")
    elif response:
        create_backup_window(set_super_curtains_values, get_current_super_curtains_values)
        save_super_curtain_values()
    else:
        save_super_curtain_values()

# Super Curtain 레지스트리 값을 저장하는 함수
def save_super_curtain_values():
    super_curtain_values = {
        'SuperCurtainTop': int(float(entry_top.get()) * 1000),  # cm -> mm 변환 후 저장
        'SuperCurtainBottom': int(float(entry_bottom.get()) * 1000),  # cm -> mm 변환 후 저장
        'SuperCurtainLeft': int(float(entry_left.get()) * 1000),
        'SuperCurtainRight': int(float(entry_right.get()) * 1000),
    }
    set_super_curtains_values(super_curtain_values)
    print("Super Curtain values saved:", super_curtain_values)
