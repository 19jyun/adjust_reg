import tkinter as tk
from tkinter import ttk
import winreg
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 레지스트리 경로 및 키
registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\PrecisionTouchPad'
curtain_keys = ['CurtainTop', 'CurtainLeft', 'CurtainRight', 'CurtainBottom']

# 현재 커튼 레지스트리 값을 읽는 함수
def get_current_curtains_values():
    curtain_values = {}
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
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

# 레지스트리 값을 설정하는 함수
def set_curtains_values(curtain_values):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
        for key, value in curtain_values.items():
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_DWORD, int(value))
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(f"Error setting registry values: {e}")

# 이미지를 업데이트하는 함수
def update_image():
    ax.clear()
    
    # 커튼 구역을 설정
    curtain_width = (slider_left.get() + slider_right.get()) / 2
    curtain_height = slider_top.get()

    # 원본 이미지를 그려줍니다
    ax.imshow(img)
    
    # 그림에 커튼 영역(민감도) 표시
    rect = plt.Rectangle((0.5 - curtain_width/2000, 0.5 - curtain_height/1000),
                         curtain_width / 1000, curtain_height / 1000,
                         linewidth=2, edgecolor='blue', facecolor='green', alpha=0.3)
    ax.add_patch(rect)
    
    # 이미지 업데이트
    canvas.draw()

# 커튼 설정 GUI 창을 생성하는 함수
def create_curtains_window():
    sub_window = tk.Toplevel()
    sub_window.title("Curtains Settings")

    # 이미지 표시할 matplotlib 설정
    global ax, canvas, img
    fig, ax = plt.subplots(figsize=(6, 4))

    img = plt.imread("trackpad/gb4p16.jpg")  # 사용자 이미지 파일 로드
    ax.imshow(img)

    canvas = FigureCanvasTkAgg(fig, master=sub_window)
    canvas.get_tk_widget().pack()

    # 슬라이더 설정
    global slider_top, slider_left, slider_right

    label_top = tk.Label(sub_window, text="Curtain Top (Height)")
    label_top.pack(pady=5)
    slider_top = ttk.Scale(sub_window, from_=0, to=1000, orient='horizontal', command=lambda x: update_image())
    slider_top.pack(pady=5)

    label_left = tk.Label(sub_window, text="Curtain Left (Width)")
    label_left.pack(pady=5)
    slider_left = ttk.Scale(sub_window, from_=0, to=1000, orient='horizontal', command=lambda x: update_image())
    slider_left.pack(pady=5)

    label_right = tk.Label(sub_window, text="Curtain Right (Width)")
    label_right.pack(pady=5)
    slider_right = ttk.Scale(sub_window, from_=0, to=1000, orient='horizontal', command=lambda x: update_image())
    slider_right.pack(pady=5)

    # 초기 슬라이더 값을 현재 레지스트리 값으로 설정
    curtain_values = get_current_curtains_values()
    slider_top.set(curtain_values.get('CurtainTop', 0))
    slider_left.set(curtain_values.get('CurtainLeft', 0))
    slider_right.set(curtain_values.get('CurtainRight', 0))

    # 저장 버튼
    btn_save = tk.Button(sub_window, text="Save Settings", command=lambda: save_curtain_values())
    btn_save.pack(pady=10)

# 커튼 레지스트리 값을 저장하는 함수
def save_curtain_values():
    curtain_values = {
        'CurtainTop': slider_top.get(),
        'CurtainLeft': slider_left.get(),
        'CurtainRight': slider_right.get(),
    }
    set_curtains_values(curtain_values)
    print("Curtain values saved:", curtain_values)
